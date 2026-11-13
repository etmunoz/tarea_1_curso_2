#!/usr/bin/env python3
"""Puente A2A: publica UN solo agente de `langgraph dev` como un agente A2A «clásico».

`langgraph dev` puede alojar varios grafos, por eso pide `?assistant_id=<uuid>` para la tarjeta y recibe los
mensajes en `/a2a/<uuid>`. Un cliente A2A estándar espera, en cambio:
  · GET  /.well-known/agent-card.json      (sin parámetros)  → la tarjeta del agente
  · POST /                                 (JSON-RPC)         → message/send o SendMessage
Este puente hace esa traducción para un agente:
  · la tarjeta sale sin parámetros, apunta su URL al puente (o al túnel) y anuncia streaming=false;
  · el contextId que no sea UUID se convierte a uno estable con uuid5 (mismo texto → mismo hilo);
  · el resto de rutas se reenvía tal cual a langgraph dev (modo compatible), así el notebook del taller
    (assistants/search, runs, threads…) sigue funcionando por el mismo túnel. Con --estricto solo se
    publican la tarjeta, POST / y /ok.

Basado en `src/puente_a2a/servidor.py` del repositorio del grupo (autor del original: grupo Fabio Durán ·
Gustavo Reyes · Ezequiel Muñoz), reescrito sin dependencias del coordinador: solo stdlib + httpx.

Uso:
  python herramientas/puente.py fabio                 # puente en 127.0.0.1:8791 → agente_fabio (127.0.0.1:2025)
  python herramientas/puente.py proteinman          # puente en 127.0.0.1:8792 → proteinman (127.0.0.1:2026)
  python herramientas/puente.py fabio --estricto      # solo tarjeta + A2A
  cloudflared tunnel --url http://127.0.0.1:8791    # y se comparte la URL del túnel
"""
import argparse
import json
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx

AGENTES = {
    "fabio": {"base": "http://127.0.0.1:2025", "grafo": "agente_fabio", "puerto": 8791},
    "proteinman": {"base": "http://127.0.0.1:2026", "grafo": "proteinman", "puerto": 8792},
}
METODOS_A2A = {"message/send", "SendMessage", "tasks/get", "GetTask"}
MAX_CUERPO = 1_000_000  # 1 MB: un mensaje de texto nunca necesita más
CABECERAS_SALTO = {"host", "content-length", "connection", "transfer-encoding", "keep-alive",
                   "accept-encoding", "upgrade", "proxy-connection"}


def a_uuid(valor) -> str:
    """contextId → UUID válido y estable (idea de `a_uuid()` del coordinador del grupo)."""
    try:
        return str(uuid.UUID(str(valor)))
    except ValueError:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, str(valor)))


class Puente(BaseHTTPRequestHandler):
    cfg: dict = {}
    http = httpx.Client(timeout=180, trust_env=False)
    _aid: str | None = None
    protocol_version = "HTTP/1.1"

    # ── utilidades ───────────────────────────────────────────────────────────
    def log_message(self, fmt, *args):
        if self.cfg.get("verboso"):
            sys.stderr.write(f"[puente {self.cfg['grafo']}] {self.address_string()} {fmt % args}\n")

    def _enviar(self, codigo: int, cuerpo: bytes, tipo="application/json; charset=utf-8", extra=None):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Access-Control-Allow-Origin", "*")  # para chat.html y clientes web
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(cuerpo)

    def _json(self, codigo: int, obj):
        self._enviar(codigo, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def _error_rpc(self, rpc_id, codigo: int, mensaje: str, http=200):
        self._json(http, {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": codigo, "message": mensaje}})

    def _url_publica(self) -> str:
        """La URL con la que llegó el cliente (tras Cloudflare: https://….trycloudflare.com)."""
        if self.cfg.get("url_publica"):
            return self.cfg["url_publica"]
        host = self.headers.get("X-Forwarded-Host") or self.headers.get("Host") or f"127.0.0.1:{self.cfg['puerto']}"
        esquema = self.headers.get("X-Forwarded-Proto") or ("https" if "trycloudflare.com" in host else "http")
        return f"{esquema}://{host}".rstrip("/")

    def _assistant_id(self) -> str:
        if not Puente._aid:
            r = self.http.post(f"{self.cfg['base']}/assistants/search", json={"graph_id": self.cfg["grafo"], "limit": 1})
            r.raise_for_status()
            lista = r.json()
            if not lista:
                raise LookupError(f"no existe el grafo {self.cfg['grafo']}")
            Puente._aid = lista[0]["assistant_id"]
        return Puente._aid

    def _leer_cuerpo(self) -> bytes | None:
        largo = int(self.headers.get("Content-Length") or 0)
        if largo > MAX_CUERPO:
            self._error_rpc(None, -32600, "Mensaje demasiado grande", http=413)
            return None
        return self.rfile.read(largo) if largo else b""

    # ── rutas ────────────────────────────────────────────────────────────────
    def do_OPTIONS(self):  # preflight CORS
        self._enviar(204, b"", extra={"Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS",
                                      "Access-Control-Allow-Headers": "content-type, authorization, a2a-version"})

    def do_GET(self):
        ruta = self.path.split("?", 1)[0]
        if ruta == "/ok":
            return self._json(200, {"ok": True, "puente": self.cfg["grafo"]})
        if ruta == "/.well-known/agent-card.json":
            return self._tarjeta()
        return self._reenviar() if not self.cfg["estricto"] else self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path.split("?", 1)[0] in ("/", ""):
            return self._a2a()
        return self._reenviar() if not self.cfg["estricto"] else self._json(404, {"error": "not found"})

    def do_PATCH(self):
        return self._reenviar() if not self.cfg["estricto"] else self._json(404, {"error": "not found"})

    def do_DELETE(self):
        return self._reenviar() if not self.cfg["estricto"] else self._json(404, {"error": "not found"})

    # ── tarjeta sin assistant_id ─────────────────────────────────────────────
    def _tarjeta(self):
        try:
            aid = self._assistant_id()
            r = self.http.get(f"{self.cfg['base']}/.well-known/agent-card.json", params={"assistant_id": aid})
            r.raise_for_status()
            card = r.json()
        except Exception:
            return self._json(503, {"error": "el agente no está disponible (¿está corriendo langgraph dev?)"})
        url = self._url_publica()
        card["url"] = url
        card["preferredTransport"] = "JSONRPC"
        card["supportedInterfaces"] = [{"url": url, "protocolBinding": "JSONRPC", "protocolVersion": "1.0"}]
        card.setdefault("capabilities", {})["streaming"] = False  # el puente atiende peticiones, no streams
        self._json(200, card)

    # ── A2A en la raíz ───────────────────────────────────────────────────────
    def _a2a(self):
        crudo = self._leer_cuerpo()
        if crudo is None:
            return
        try:
            pet = json.loads(crudo or b"{}")
        except ValueError:
            return self._error_rpc(None, -32700, "Parse error")
        if not isinstance(pet, dict):
            return self._error_rpc(None, -32600, "Invalid Request")
        rpc_id, metodo = pet.get("id"), pet.get("method")
        if metodo not in METODOS_A2A:
            return self._error_rpc(rpc_id, -32601, f"Método no soportado por el puente: {metodo}")
        mensaje = (pet.get("params") or {}).get("message")
        if isinstance(mensaje, dict):
            if mensaje.get("contextId"):
                mensaje["contextId"] = a_uuid(mensaje["contextId"])  # LangGraph exige UUID
            else:
                mensaje["contextId"] = str(uuid.uuid4())
            mensaje.setdefault("messageId", uuid.uuid4().hex)
        try:
            aid = self._assistant_id()
            cabeceras = {"Content-Type": "application/json"}
            if self.headers.get("A2A-Version"):
                cabeceras["A2A-Version"] = self.headers["A2A-Version"]
            r = self.http.post(f"{self.cfg['base']}/a2a/{aid}", json=pet, headers=cabeceras)
        except Exception:
            Puente._aid = None  # por si el servidor se reinició
            return self._error_rpc(rpc_id, -32000, "El agente no está disponible temporalmente.")
        self._enviar(r.status_code, r.content, r.headers.get("content-type", "application/json"))

    # ── modo compatible: el resto de la API de LangGraph, tal cual ────────────
    def _reenviar(self):
        crudo = self._leer_cuerpo()
        if crudo is None:
            return
        cabeceras = {k: v for k, v in self.headers.items() if k.lower() not in CABECERAS_SALTO}
        try:
            r = self.http.request(self.command, f"{self.cfg['base']}{self.path}", content=crudo or None,
                                  headers=cabeceras)
        except Exception:
            return self._json(502, {"error": "el agente no está disponible"})
        self._enviar(r.status_code, r.content, r.headers.get("content-type", "application/json"))


def main():
    p = argparse.ArgumentParser(description="Puente A2A: publica un solo agente de langgraph dev.")
    p.add_argument("agente", choices=AGENTES)
    p.add_argument("--puerto", type=int, help="puerto del puente (por defecto 8791 fabio, 8792 proteinman)")
    p.add_argument("--url-publica", help="URL a anunciar en la tarjeta (por defecto, la del túnel por el que llega)")
    p.add_argument("--estricto", action="store_true", help="publicar solo tarjeta, POST / y /ok")
    p.add_argument("-v", "--verboso", action="store_true", help="registrar cada petición en la terminal")
    a = p.parse_args()
    cfg = dict(AGENTES[a.agente])
    cfg.update(puerto=a.puerto or cfg["puerto"], url_publica=(a.url_publica or "").rstrip("/"),
               estricto=a.estricto, verboso=a.verboso)
    Puente.cfg = cfg
    servidor = ThreadingHTTPServer(("127.0.0.1", cfg["puerto"]), Puente)
    print(f"Puente A2A de «{cfg['grafo']}» ({cfg['base']}) en http://127.0.0.1:{cfg['puerto']}"
          f" · modo {'estricto' if a.estricto else 'compatible'} · Ctrl+C para detener", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nPuente detenido.")


if __name__ == "__main__":
    main()
