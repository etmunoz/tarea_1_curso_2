# --8<-- encabezado-grupo
# Archivo: src/puente_a2a/servidor.py
# Objetivo: Puente/adaptador A2A: expone un agente de `langgraph dev` en formato **A2A clásico**.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 1342
# Última modificación: 20261111 1343
# --8<-- fin-encabezado-grupo

"""Puente/adaptador A2A: expone un agente de `langgraph dev` en formato **A2A clásico**.

Problema que resuelve: nuestro `langgraph dev` sirve la Agent Card en
`/.well-known/agent-card.json?assistant_id=<uuid>` y recibe mensajes en `/a2a/<uuid>`.
Un cliente A2A estándar (SDK a2a-protocol.org, como el de un compañero) espera la card
en `/.well-known/agent-card.json` **sin** parámetros y manda los mensajes a la **URL base**.
Este puente traduce entre ambos mundos, SIN dependencias nuevas (solo stdlib + httpx, que
ya está) y sin tocar el agente.

Config por entorno:
  PUENTE_BASE          base del langgraph dev local (def. http://127.0.0.1:2024)
  PUENTE_GRAFO         grafo a exponer (def. agente_ezequiel)
  PUENTE_PORT          puerto del puente (def. 8790)
  PUENTE_URL_PUBLICA   URL pública a anunciar en la card (def. http://127.0.0.1:<port>);
                       al salir por Cloudflare, poner aquí la URL del túnel del puente.

Uso:
    uv run python -m src.puente_a2a.servidor
    # y en otra terminal:  cloudflared tunnel --url http://127.0.0.1:8790
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ))

from src.coordinador import a2a  # noqa: E402


def card_clasica(card_langgraph: dict, url_publica: str) -> dict:
    """Objetivo: reescribir la Agent Card de langgraph a formato A2A clásico, apuntando la
    `url`/`supportedInterfaces` al puente. Entradas: card del langgraph, url_publica (str).
    Salida: dict — la card clásica."""
    url = url_publica.rstrip("/")
    return {
        "name": card_langgraph.get("name") or "agente",
        "description": card_langgraph.get("description", ""),
        "version": card_langgraph.get("version", "1.0.0"),
        "url": url,
        "preferredTransport": "JSONRPC",
        "capabilities": card_langgraph.get("capabilities", {"streaming": False}),
        "defaultInputModes": card_langgraph.get("defaultInputModes", ["text/plain"]),
        "defaultOutputModes": card_langgraph.get("defaultOutputModes", ["text/plain"]),
        "skills": card_langgraph.get("skills", []),
        "supportedInterfaces": [
            {"url": url, "protocolBinding": "JSONRPC", "protocolVersion": "1.0"}
        ],
    }


def extraer_texto_y_ctx(payload: dict) -> tuple[str, str]:
    """Objetivo: sacar el texto del usuario y el contextId de un JSON-RPC message/send.
    Entradas: payload (dict). Salida: (texto (str), context_id (str); genera uno si falta)."""
    msg = ((payload.get("params") or {}).get("message")) or {}
    partes = msg.get("parts") or []
    texto = " ".join(p.get("text", "") for p in partes if isinstance(p, dict) and p.get("text")).strip()
    # langgraph exige que el contextId (thread_id) sea un UUID; coaccionamos el del cliente.
    ctx = a2a.a_uuid(msg.get("contextId") or a2a.nuevo_context_id())
    return texto, ctx


def resultado_a2a(texto: str, rpc_id, context_id: str) -> dict:
    """Objetivo: envolver la respuesta del agente en un resultado JSON-RPC A2A (un Message
    del rol 'agent'). Entradas: texto (str), rpc_id (id del JSON-RPC), context_id (str).
    Salida: dict — la respuesta JSON-RPC completa."""
    return {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "result": {
            "role": "agent",
            "kind": "message",
            "messageId": uuid.uuid4().hex,
            "contextId": context_id,
            "parts": [{"kind": "text", "text": texto}],
        },
    }


def _error_rpc(rpc_id, codigo: int, mensaje: str) -> dict:
    """Objetivo: armar un error JSON-RPC. Entradas: rpc_id, codigo (int), mensaje (str).
    Salida: dict."""
    return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": codigo, "message": mensaje}}


def _config() -> dict:
    """Objetivo: leer la configuración del puente del entorno. Salida: dict."""
    port = int(os.environ.get("PUENTE_PORT", "8790"))
    return {
        "base": os.environ.get("PUENTE_BASE", "http://127.0.0.1:2024").rstrip("/"),
        "grafo": os.environ.get("PUENTE_GRAFO", "agente_ezequiel"),
        "port": port,
        "url_publica": os.environ.get("PUENTE_URL_PUBLICA", f"http://127.0.0.1:{port}").rstrip("/"),
    }


class _Handler(BaseHTTPRequestHandler):
    """Objetivo: manejar las rutas del puente (card clásica + message/send)."""

    cfg: dict = {}

    def _responder(self, codigo: int, cuerpo: dict) -> None:
        datos = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def log_message(self, *_a):  # noqa: D401 - silenciar el log ruidoso por defecto
        """No imprime una línea por request (ruido)."""

    def do_GET(self):  # noqa: N802
        if self.path.startswith("/.well-known/agent-card.json"):
            try:
                card = a2a.agent_card(self.cfg["base"], self.cfg["grafo"])
            except a2a.AgenteNoDisponible as exc:
                self._responder(503, {"error": f"agente no disponible: {exc.motivo}"})
                return
            self._responder(200, card_clasica(card, self.cfg["url_publica"]))
        elif self.path.startswith("/ok"):
            self._responder(200, {"status": "ok"})
        else:
            self._responder(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        largo = int(self.headers.get("Content-Length", 0))
        crudo = self.rfile.read(largo) if largo else b"{}"
        try:
            payload = json.loads(crudo)
        except ValueError:
            self._responder(400, _error_rpc(None, -32700, "Parse error"))
            return
        rpc_id = payload.get("id")
        if payload.get("method") != "message/send":
            self._responder(200, _error_rpc(rpc_id, -32601, "Method not found"))
            return
        texto, ctx = extraer_texto_y_ctx(payload)
        if not texto:
            self._responder(200, _error_rpc(rpc_id, -32602, "Mensaje sin texto"))
            return
        try:
            respuesta = a2a.enviar_mensaje(self.cfg["base"], self.cfg["grafo"], texto, ctx)
        except a2a.AgenteNoDisponible as exc:
            # No se filtran URLs ni trazas internas al cliente remoto.
            self._responder(200, _error_rpc(rpc_id, -32000, "El agente no está disponible temporalmente."))
            return
        self._responder(200, resultado_a2a(respuesta, rpc_id, ctx))


def main() -> None:
    """Objetivo: levantar el puente. Entradas: ninguna (lee el entorno). Salida: None (sirve)."""
    cfg = _config()
    _Handler.cfg = cfg
    servidor = ThreadingHTTPServer(("0.0.0.0", cfg["port"]), _Handler)
    print(f"Puente A2A clásico para «{cfg['grafo']}» → {cfg['base']}")
    print(f"  escuchando en http://127.0.0.1:{cfg['port']}  · card: /.well-known/agent-card.json")
    print(f"  url pública anunciada: {cfg['url_publica']}")
    print("  (Ctrl+C para parar)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nPuente detenido.")


if __name__ == "__main__":
    main()
