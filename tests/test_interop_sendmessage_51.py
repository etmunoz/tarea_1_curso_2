# --8<-- encabezado-grupo
# Archivo: tests/test_interop_sendmessage_51.py
# Objetivo: Interoperabilidad con el dialecto `SendMessage` del compañero (prompt 51).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 1737
# Última modificación: 20261111 1741
# --8<-- fin-encabezado-grupo

"""Interoperabilidad con el dialecto `SendMessage` del compañero (prompt 51).

El agente de un compañero (SDK a2a-protocol.org) no implementa `message/send` (devuelve
-32601) sino `SendMessage` (role ROLE_USER, parts sin `kind`, header A2A-Version), y envuelve
el texto en un repr de lista. Nuestro cliente generalizado:
- reintenta con `SendMessage` cuando `message/send` da -32601 en dialecto clásico,
- desanida el texto.

Deterministas, sin red (httpx simulado).
"""
import httpx
import pytest

from src.coordinador import a2a


@pytest.fixture(autouse=True)
def _limpiar():
    a2a._cache_aid.clear()
    a2a._cache_dialecto.clear()
    yield
    a2a._cache_aid.clear()
    a2a._cache_dialecto.clear()


class _R:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status
        self.headers = {"content-type": "application/json"}

    def raise_for_status(self):
        if self.status_code >= 400:
            req = httpx.Request("POST", "http://x")
            raise httpx.HTTPStatusError("e", request=req, response=httpx.Response(self.status_code, request=req))

    def json(self):
        return self._data


# ---- helpers de extracción / desanidado ----

def test_textos_reconoce_type_y_text_minimo():
    assert a2a._textos({"type": "text", "text": "hola"}) == ["hola"]
    assert a2a._textos({"text": "mínima"}) == ["mínima"]
    assert a2a._textos({"kind": "text", "text": "estándar"}) == ["estándar"]


def test_desanidar_repr_de_lista():
    crudo = "[{'type': 'text', 'text': 'Pronóstico: lluvia', 'extras': {'signature': 'abc'}}]"
    assert a2a._desanidar(crudo) == "Pronóstico: lluvia"


def test_desanidar_texto_normal_no_cambia():
    assert a2a._desanidar("Mañana nublado, 15°C") == "Mañana nublado, 15°C"


# ---- fallback message/send -> SendMessage ----

def test_fallback_a_sendmessage(monkeypatch):
    """Si message/send da -32601 en dialecto clásico, reintenta con SendMessage y desanida."""
    card = {"name": "agente_meteorologo", "supportedInterfaces": [{"url": "https://comp.example"}]}
    monkeypatch.setattr(a2a.httpx, "get", lambda *a, **k: _R(card))
    llamadas = []

    def post(url, **k):
        cuerpo = k.get("json") or {}
        headers = k.get("headers") or {}
        llamadas.append((cuerpo.get("method"), headers.get("A2A-Version")))
        if cuerpo.get("method") == "message/send":
            return _R({"error": {"code": -32601, "message": "Method not found"}})
        # SendMessage: respuesta con el texto anidado como repr
        return _R({"result": {"message": {"role": "ROLE_AGENT",
                   "parts": [{"text": "[{'type': 'text', 'text': 'Lluvia débil, 7 a 17 °C.'}]"}]}}})

    monkeypatch.setattr(a2a.httpx, "post", post)
    r = a2a.enviar_mensaje("https://comp.example", "agente", "clima mañana", "ctx-1")
    assert r == "Lluvia débil, 7 a 17 °C."                     # desanidado
    assert ("message/send", None) in llamadas                  # primer intento
    assert ("SendMessage", "1.0") in llamadas                  # fallback con header
    assert len(llamadas) == 2                                  # exactamente un reintento


def test_sin_fallback_cuando_message_send_funciona(monkeypatch):
    """Si message/send responde bien, NO se reintenta con SendMessage."""
    card = {"name": "agente_x", "supportedInterfaces": [{"url": "https://comp.example"}]}
    monkeypatch.setattr(a2a.httpx, "get", lambda *a, **k: _R(card))
    metodos = []

    def post(url, **k):
        metodos.append((k.get("json") or {}).get("method"))
        return _R({"result": {"parts": [{"kind": "text", "text": "ok directo"}]}})

    monkeypatch.setattr(a2a.httpx, "post", post)
    r = a2a.enviar_mensaje("https://comp.example", "agente", "hola", "ctx")
    assert r == "ok directo"
    assert metodos == ["message/send"]                         # sin reintento
