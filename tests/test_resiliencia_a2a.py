# --8<-- encabezado-grupo
# Archivo: tests/test_resiliencia_a2a.py
# Objetivo: Pruebas de resiliencia: qué pasa cuando un agente remoto NO está disponible.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 0730
# Última modificación: 20261111 2049
# --8<-- fin-encabezado-grupo

"""Pruebas de resiliencia: qué pasa cuando un agente remoto NO está disponible.

Cubre el guardrail de infraestructura del coordinador (implementación 1):
- `a2a` convierte conexión caída / timeout / HTTP != 2xx / JSON inválido en
  `AgenteNoDisponible` (no deja escapar excepciones crudas de httpx).
- el catálogo se construye igual aunque un agente esté caído.
- el nodo `consultar` del grafo devuelve un estado CONTROLADO (requiere API key).

No necesita red: se simula httpx con dobles.
"""
import os

import httpx
import pytest

from src.coordinador import a2a, catalogo


class _Resp:
    """Doble de httpx.Response: controla status y json()."""

    def __init__(self, data=None, status=200, bad_json=False):
        self._data = data
        self._status = status
        self._bad = bad_json

    def raise_for_status(self):
        if self._status >= 400:
            req = httpx.Request("POST", "http://x")
            raise httpx.HTTPStatusError("error", request=req, response=httpx.Response(self._status, request=req))

    def json(self):
        if self._bad:
            raise ValueError("no es JSON")
        return self._data


@pytest.fixture(autouse=True)
def _limpiar_caches():
    """Limpia las cachés de a2a y catalogo entre pruebas."""
    for d in (a2a._cache_aid, a2a._cache_dialecto, catalogo._cards, catalogo._ultima_card, catalogo._disp):
        d.clear()
    yield
    for d in (a2a._cache_aid, a2a._cache_dialecto, catalogo._cards, catalogo._ultima_card, catalogo._disp):
        d.clear()


def test_connect_error_es_agente_no_disponible(monkeypatch):
    """Conexión caída (túnel abajo) → AgenteNoDisponible con motivo claro."""
    a2a._cache_dialecto["https://caido.example"] = "langgraph"  # evita el GET de detección
    monkeypatch.setattr(a2a.httpx, "post", lambda *a, **k: (_ for _ in ()).throw(httpx.ConnectError("down")))
    with pytest.raises(a2a.AgenteNoDisponible) as e:
        a2a.enviar_mensaje("https://caido.example", "agente_fabio", "hola", "ctx")
    assert "conectar" in e.value.motivo
    assert e.value.destino.startswith("https://caido.example")


def test_timeout_es_agente_no_disponible(monkeypatch):
    """Timeout → AgenteNoDisponible('tiempo de espera agotado')."""
    a2a._cache_dialecto["https://lento.example"] = "langgraph"  # evita el GET de detección
    monkeypatch.setattr(a2a.httpx, "post", lambda *a, **k: (_ for _ in ()).throw(httpx.ReadTimeout("slow")))
    with pytest.raises(a2a.AgenteNoDisponible) as e:
        a2a.enviar_mensaje("https://lento.example", "agente_x", "hola", "ctx")
    assert "espera" in e.value.motivo


def test_http_500_es_agente_no_disponible(monkeypatch):
    """Respuesta HTTP inválida (500) → AgenteNoDisponible con el código."""
    monkeypatch.setattr(a2a.httpx, "post", lambda *a, **k: _Resp(status=500))
    with pytest.raises(a2a.AgenteNoDisponible) as e:
        a2a.assistant_id("https://roto.example", "agente_x")
    assert "500" in e.value.motivo


def test_json_invalido_es_respuesta_invalida(monkeypatch):
    """Cuerpo que no es JSON → RespuestaA2AInvalida (no ValueError crudo). Es un error de
    protocolo, distinto del de transporte (AgenteNoDisponible)."""
    monkeypatch.setattr(a2a.httpx, "post", lambda *a, **k: _Resp(bad_json=True))
    with pytest.raises(a2a.RespuestaA2AInvalida):
        a2a.assistant_id("https://raro.example", "agente_x")
    assert issubclass(a2a.RespuestaA2AInvalida, a2a.ErrorA2A)


def test_grafo_desconocido_es_agente_no_disponible(monkeypatch):
    """El servidor responde pero no conoce el grafo → AgenteNoDisponible."""
    monkeypatch.setattr(a2a.httpx, "post", lambda *a, **k: _Resp(data=[]))
    with pytest.raises(a2a.AgenteNoDisponible) as e:
        a2a.assistant_id("http://127.0.0.1:2024", "agente_inexistente")
    assert "no conoce" in e.value.motivo


def test_catalogo_se_construye_con_un_agente_caido(monkeypatch):
    """Un agente caído NO impide armar el catálogo de los que sí funcionan."""
    def card_falsa(base, graph, timeout=10):
        if "caido" in base:
            raise a2a.AgenteNoDisponible(base, "no se pudo conectar")
        return {"name": "Agente de Ezequiel", "description": "IA y Data Science"}

    monkeypatch.setattr(catalogo, "_cards", {})
    monkeypatch.setattr(catalogo.a2a, "agent_card", card_falsa)
    monkeypatch.setenv("A2A_BASE", "http://127.0.0.1:2024")
    monkeypatch.setenv("A2A_GRAFOS_LOCALES", "agente_ezequiel")
    monkeypatch.setenv("URLS_AGENTES", "https://caido.example#agente_fabio")

    cat = catalogo.construir_catalogo()
    texto = catalogo.texto_catalogo(cat)  # no debe lanzar
    assert "Agente de Ezequiel" in texto
    # El agente caído que NUNCA se descubrió aparece como no elegible (sin ficha), distinto de
    # uno "temporalmente no disponible" (que sí tendría capacidades conocidas).
    assert "sin ficha" in texto
    vivo = next(a for a in cat if a.graph == "agente_ezequiel")
    caido = next(a for a in cat if a.graph == "agente_fabio")
    assert vivo.disponible() is True
    assert caido.disponible() is False
    assert caido.conocido() is False  # nunca se supo qué hace → inexistente, no "desconectado"
    assert caido.nombre == "agente_fabio"  # fallback al id del grafo


@pytest.mark.skipif(not os.environ.get("GOOGLE_API_KEY"), reason="requiere GOOGLE_API_KEY (importa el grafo)")
def test_consultar_devuelve_estado_controlado(monkeypatch):
    """El nodo consultar, ante AgenteNoDisponible, responde un estado controlado
    ('no está disponible temporalmente … los demás continúan operativos')."""
    from langchain_core.messages import HumanMessage  # noqa: PLC0415

    from src.coordinador import graph  # noqa: PLC0415

    class FakeAgente:
        nombre = "Agente de Fabio"
        graph = "agente_fabio"
        local = False

        def conocido(self):
            return True  # sí sabemos qué hace (es el especialista), pero está caído

        def preguntar(self, texto, ctx):
            raise a2a.AgenteNoDisponible("Agente de Fabio", "no se pudo conectar (¿túnel caído?)")

    monkeypatch.setattr(graph, "construir_catalogo", lambda: [FakeAgente()])
    estado = {"messages": [HumanMessage(content="¿Qué símbolos hay en Reiki?")], "elegido": "Agente de Fabio"}
    out = graph.consultar(estado, {"configurable": {"thread_id": "t1"}})
    assert out["ruta"] == ["agente_no_disponible"]
    assert "es el especialista" in out["respuesta"]
    assert "no está disponible" in out["respuesta"]
    assert "continúan operativos" in out["respuesta"]
