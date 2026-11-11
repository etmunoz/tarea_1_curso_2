# --8<-- encabezado-grupo
# Archivo: tests/test_robustez_a2a_48.py
# Objetivo: Robustez del cliente A2A y catálogo (prompt 48, correcciones 1 y 4).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 1405
# Última modificación: 20261111 2049
# --8<-- fin-encabezado-grupo

"""Robustez del cliente A2A y catálogo (prompt 48, correcciones 1 y 4).

- Corrección 1: distinguir agente inexistente de agente desconectado (capacidad vs
  disponibilidad), usando la última ficha conocida.
- Corrección 4: validación estructural del JSON, jerarquía de excepciones y recuperación
  de `assistant_id` obsoleto (404 → recargar → reintentar una vez).

Deterministas, sin red (httpx simulado).
"""
import httpx
import pytest

from src.coordinador import a2a, catalogo


class _Resp:
    def __init__(self, data=None, status=200, bad_json=False):
        self._data = data
        self.status_code = status
        self._bad = bad_json
        self.headers = {"content-type": "application/json"}

    def raise_for_status(self):
        if self.status_code >= 400:
            req = httpx.Request("POST", "http://x")
            raise httpx.HTTPStatusError("e", request=req, response=httpx.Response(self.status_code, request=req))

    def json(self):
        if self._bad:
            raise ValueError("no json")
        return self._data


@pytest.fixture(autouse=True)
def _limpiar():
    for d in (a2a._cache_aid, a2a._cache_dialecto, catalogo._cards, catalogo._ultima_card, catalogo._disp):
        d.clear()
    yield
    for d in (a2a._cache_aid, a2a._cache_dialecto, catalogo._cards, catalogo._ultima_card, catalogo._disp):
        d.clear()


# ============ Corrección 1: capacidad vs disponibilidad ============

def _agente(graph="agente_tomas"):
    return catalogo.AgenteRemoto("https://remoto.example", graph, local=False)


def test_agente_disponible_muestra_descripcion(monkeypatch):
    monkeypatch.setattr(catalogo.a2a, "agent_card",
                        lambda b, g, timeout=10: {"name": "Agente de Tomás", "description": "Reiki", "skills": []})
    a = _agente()
    assert a.disponible() is True
    assert "Reiki" in catalogo.texto_catalogo([a])


def test_agente_desconectado_pero_conocido(monkeypatch):
    """Si SÍ se conoció su ficha y luego cae, conserva capacidades y se marca 'temporalmente'."""
    a = _agente()
    monkeypatch.setattr(catalogo.a2a, "agent_card",
                        lambda b, g, timeout=10: {"name": "Agente de Tomás", "description": "Reiki", "skills": []})
    a.card()  # lo descubrimos una vez
    catalogo._cards.clear()
    catalogo._disp.clear()
    monkeypatch.setattr(catalogo.a2a, "agent_card",
                        lambda b, g, timeout=10: (_ for _ in ()).throw(a2a.AgenteNoDisponible("x", "caído")))
    assert a.disponible() is False
    assert a.conocido() is True              # sabemos qué hace
    texto = catalogo.texto_catalogo([a])
    assert "Reiki" in texto                  # conserva capacidades
    assert "temporalmente NO disponible" in texto


def test_agente_inexistente_no_elegible(monkeypatch):
    """Nunca descubierto y caído ⇒ sin ficha / no elegible (no es lo mismo que desconectado)."""
    a = _agente("agente_fantasma")
    monkeypatch.setattr(catalogo.a2a, "agent_card",
                        lambda b, g, timeout=10: (_ for _ in ()).throw(a2a.AgenteNoDisponible("x", "caído")))
    assert a.conocido() is False
    assert "sin ficha" in catalogo.texto_catalogo([a])


def test_recuperacion_tras_reconexion(monkeypatch):
    """Tras caerse, si vuelve a responder, estado() lo reporta disponible de nuevo."""
    a = _agente()
    estado = {"up": False}
    def card(b, g, timeout=10):
        if estado["up"]:
            return {"name": "Agente de Tomás", "description": "Reiki", "skills": []}
        raise a2a.AgenteNoDisponible("x", "caído")
    monkeypatch.setattr(catalogo.a2a, "agent_card", card)
    assert a.disponible() is False
    estado["up"] = True
    catalogo._disp.clear()  # vence la caché corta
    assert a.disponible() is True


def test_no_confunde_indisponibilidad_con_ausencia_de_capacidad(monkeypatch):
    """Un agente conocido pero caído conserva su descripción (capacidad), no desaparece."""
    a = _agente()
    monkeypatch.setattr(catalogo.a2a, "agent_card",
                        lambda b, g, timeout=10: {"name": "Agente de Tomás", "description": "Reiki símbolos", "skills": []})
    a.card()
    catalogo._cards.clear(); catalogo._disp.clear()
    monkeypatch.setattr(catalogo.a2a, "agent_card",
                        lambda b, g, timeout=10: (_ for _ in ()).throw(a2a.AgenteNoDisponible("x", "caído")))
    assert "símbolos" in a.descripcion()


# ============ Corrección 4: validación JSON, excepciones, assistant_id obsoleto ============

def test_assistant_id_estructura_invalida(monkeypatch):
    """Lista cuyo primer elemento no trae 'assistant_id' ⇒ RespuestaA2AInvalida."""
    monkeypatch.setattr(a2a.httpx, "post", lambda *a, **k: _Resp(data=[{"otra_cosa": 1}]))
    with pytest.raises(a2a.RespuestaA2AInvalida):
        a2a.assistant_id("http://srv", "g")


def test_assistant_id_no_es_lista(monkeypatch):
    """Si /assistants/search no devuelve una lista ⇒ RespuestaA2AInvalida (no TypeError)."""
    monkeypatch.setattr(a2a.httpx, "post", lambda *a, **k: _Resp(data={"inesperado": True}))
    with pytest.raises(a2a.RespuestaA2AInvalida):
        a2a.assistant_id("http://srv", "g")


def test_jsonrpc_error_es_error_protocolo(monkeypatch):
    """Un message/send que devuelve {'error': …} ⇒ ErrorProtocoloA2A (no de transporte)."""
    a2a._cache_dialecto["http://srv"] = "langgraph"
    a2a._cache_aid[("http://srv", "g")] = "aid1"
    monkeypatch.setattr(a2a.httpx, "post",
                        lambda url, **k: _Resp(data={"error": {"code": -32601, "message": "Method not found"}}))
    with pytest.raises(a2a.ErrorProtocoloA2A):
        a2a.enviar_mensaje("http://srv", "g", "hola", "11111111-1111-1111-1111-111111111111")


def test_recuperacion_assistant_id_obsoleto(monkeypatch):
    """404 en /a2a/<aid> ⇒ invalida, re-busca y reintenta UNA vez con el nuevo id ⇒ éxito."""
    a2a._cache_dialecto["http://srv"] = "langgraph"
    llamadas = {"search": 0, "a2a": 0}

    def post(url, **k):
        if url.endswith("/assistants/search"):
            llamadas["search"] += 1
            aid = "aid-viejo" if llamadas["search"] == 1 else "aid-nuevo"
            return _Resp(data=[{"assistant_id": aid}])
        # endpoint /a2a/<aid>
        llamadas["a2a"] += 1
        if "aid-viejo" in url:
            return _Resp(status=404)
        return _Resp(data={"result": {"parts": [{"kind": "text", "text": "ok tras recargar"}]}})

    monkeypatch.setattr(a2a.httpx, "post", post)
    r = a2a.enviar_mensaje("http://srv", "g", "hola", "11111111-1111-1111-1111-111111111111")
    assert r == "ok tras recargar"
    assert llamadas["search"] == 2  # re-buscó el id
    assert llamadas["a2a"] == 2      # reintentó una vez


def test_404_persistente_es_identificador_obsoleto(monkeypatch):
    """Si el 404 persiste tras recargar ⇒ IdentificadorAsistenteObsoleto (sin bucle infinito)."""
    a2a._cache_dialecto["http://srv"] = "langgraph"

    def post(url, **k):
        if url.endswith("/assistants/search"):
            return _Resp(data=[{"assistant_id": "aid"}])
        return _Resp(status=404)

    monkeypatch.setattr(a2a.httpx, "post", post)
    with pytest.raises(a2a.IdentificadorAsistenteObsoleto):
        a2a.enviar_mensaje("http://srv", "g", "hola", "11111111-1111-1111-1111-111111111111")


def test_jerarquia_de_excepciones():
    """Todas las excepciones A2A comparten la base ErrorA2A (el coordinador captura una sola)."""
    for exc in (a2a.AgenteNoDisponible, a2a.ErrorProtocoloA2A, a2a.RespuestaA2AInvalida,
                a2a.IdentificadorAsistenteObsoleto):
        assert issubclass(exc, a2a.ErrorA2A)
