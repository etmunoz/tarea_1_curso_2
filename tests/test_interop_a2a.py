# --8<-- encabezado-grupo
# Archivo: tests/test_interop_a2a.py
# Objetivo: Pruebas de interoperabilidad A2A (prompt 49).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 1342
# Última modificación: 20261111 2016
# --8<-- fin-encabezado-grupo

"""Pruebas de interoperabilidad A2A (prompt 49).

- Cliente generalizado (`a2a`): detección de dialecto y modo 'clásico' (card sin
  assistant_id; mensajes a la URL base) vs 'langgraph'.
- `a2a.a_uuid`: coacción de contextId arbitrario a UUID estable (fix del 'Invalid thread ID').
- Puente (`src.puente_a2a.servidor`): funciones de traducción y un end-to-end real contra un
  langgraph simulado (sin red externa).
"""
import threading
import uuid
from http.server import ThreadingHTTPServer

import httpx
import pytest

from src.coordinador import a2a
from src.puente_a2a import servidor


class _Resp:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status
        self.headers = {"content-type": "application/json"}

    def raise_for_status(self):
        if self.status_code >= 400:
            req = httpx.Request("GET", "http://x")
            raise httpx.HTTPStatusError("e", request=req, response=httpx.Response(self.status_code, request=req))

    def json(self):
        return self._data


@pytest.fixture(autouse=True)
def _limpiar(monkeypatch):
    a2a._cache_aid.clear()
    a2a._cache_dialecto.clear()
    yield
    a2a._cache_aid.clear()
    a2a._cache_dialecto.clear()


# ---------------- a_uuid (fix del contextId) ----------------

def test_a_uuid_respeta_un_uuid():
    u = str(uuid.uuid4())
    assert a2a.a_uuid(u) == u


def test_a_uuid_deriva_estable_de_texto():
    """Un contextId no-UUID se vuelve un UUID válido y estable (mismo texto → mismo UUID)."""
    a = a2a.a_uuid("gustavo-hilo-1")
    b = a2a.a_uuid("gustavo-hilo-1")
    assert a == b
    uuid.UUID(a)  # no lanza: es un UUID válido
    assert a != a2a.a_uuid("otro-hilo")


# ---------------- dialecto ----------------

def test_dialecto_clasico(monkeypatch):
    """Una card con 'name' servida sin assistant_id ⇒ servidor 'clasico'."""
    monkeypatch.setattr(a2a.httpx, "get", lambda *a, **k: _Resp({"name": "agente_meteorologo"}))
    assert a2a.dialecto("https://companero.example") == "clasico"


def test_dialecto_langgraph(monkeypatch):
    """Un error pidiendo assistant_id ⇒ servidor 'langgraph'."""
    monkeypatch.setattr(a2a.httpx, "get",
                        lambda *a, **k: _Resp({"error": {"message": "Missing assistant_id"}}, status=422))
    assert a2a.dialecto("http://127.0.0.1:2024") == "langgraph"


# ---------------- cliente en modo clásico ----------------

def test_agent_card_clasica(monkeypatch):
    card = {"name": "agente_meteorologo", "description": "clima",
            "supportedInterfaces": [{"url": "https://companero.example"}]}
    monkeypatch.setattr(a2a.httpx, "get", lambda *a, **k: _Resp(card))
    assert a2a.agent_card("https://companero.example", "agente")["name"] == "agente_meteorologo"


def test_enviar_mensaje_clasico_postea_a_la_url_base(monkeypatch):
    """En modo clásico, el mensaje va a la URL de supportedInterfaces (no a /a2a/<id>)."""
    card = {"name": "agente_meteorologo",
            "supportedInterfaces": [{"url": "https://companero.example/rpc"}]}
    monkeypatch.setattr(a2a.httpx, "get", lambda *a, **k: _Resp(card))
    capturado = {}

    def fake_post(url, **k):
        capturado["url"] = url
        return _Resp({"result": {"parts": [{"kind": "text", "text": "va a llover"}]}})

    monkeypatch.setattr(a2a.httpx, "post", fake_post)
    r = a2a.enviar_mensaje("https://companero.example", "agente", "¿clima?", "ctx")
    assert r == "va a llover"
    assert capturado["url"] == "https://companero.example/rpc"  # URL base, no /a2a/<id>


# ---------------- funciones de traducción del puente ----------------

def test_card_clasica_reescribe_url():
    card = servidor.card_clasica({"name": "Agente de Ezequiel", "description": "IA", "skills": [{"name": "s"}]},
                                 "https://pub.example")
    assert card["url"] == "https://pub.example"
    assert card["supportedInterfaces"][0]["url"] == "https://pub.example"
    assert card["name"] == "Agente de Ezequiel"
    assert card["preferredTransport"] == "JSONRPC"


def test_extraer_texto_y_ctx_coacciona_uuid():
    payload = {"params": {"message": {"parts": [{"kind": "text", "text": "hola"}], "contextId": "c1"}}}
    texto, ctx = servidor.extraer_texto_y_ctx(payload)
    assert texto == "hola"
    uuid.UUID(ctx)  # el contextId quedó como UUID válido


def test_resultado_a2a_forma():
    r = servidor.resultado_a2a("respuesta", "7", "ctx")
    assert r["id"] == "7"
    assert r["result"]["role"] == "agent"
    assert r["result"]["parts"][0]["text"] == "respuesta"


# ---------------- puente END-TO-END (servidor real, langgraph simulado) ----------------

def test_puente_end_to_end(monkeypatch):
    """Levanta el puente real en un puerto libre con un langgraph simulado y lo ejerce por HTTP:
    card sin assistant_id, message/send (contextId no-UUID) y método desconocido."""
    monkeypatch.setattr(servidor.a2a, "agent_card",
                        lambda base, graph, timeout=10: {"name": "Agente de Ezequiel", "description": "IA", "skills": []})
    monkeypatch.setattr(servidor.a2a, "enviar_mensaje",
                        lambda base, graph, texto, ctx: f"eco: {texto}")
    servidor._Handler.cfg = {"base": "http://x", "grafo": "agente_ezequiel", "port": 0, "url_publica": "http://pub"}
    srv = ThreadingHTTPServer(("127.0.0.1", 0), servidor._Handler)
    port = srv.server_address[1]
    hilo = threading.Thread(target=srv.serve_forever, daemon=True)
    hilo.start()
    try:
        base = f"http://127.0.0.1:{port}"
        card = httpx.get(f"{base}/.well-known/agent-card.json", timeout=5).json()
        assert card["name"] == "Agente de Ezequiel" and card["url"] == "http://pub"

        env = {"jsonrpc": "2.0", "id": "1", "method": "message/send",
               "params": {"message": {"parts": [{"kind": "text", "text": "hola"}], "contextId": "no-uuid"}}}
        res = httpx.post(base + "/", json=env, timeout=5).json()
        assert res["result"]["parts"][0]["text"] == "eco: hola"

        malo = httpx.post(base + "/", json={"jsonrpc": "2.0", "id": "2", "method": "otro"}, timeout=5).json()
        assert malo["error"]["code"] == -32601
    finally:
        srv.shutdown()
