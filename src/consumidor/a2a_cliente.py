# --8<-- encabezado-grupo
# Archivo: src/consumidor/a2a_cliente.py
# Objetivo: Cliente A2A: habla con el agente de viajes (remoto) por el protocolo A2A.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1629
# Última modificación: 20261110 2140
# --8<-- fin-encabezado-grupo

"""Cliente A2A: habla con el agente de viajes (remoto) por el protocolo A2A.

No sabe nada de vuelos ni hoteles: sabe descubrir al agente por su Agent Card y
mandarle tareas con `message/send`. Todo lo que devuelve es un **dato** (va al user
prompt del consumidor, nunca al system prompt).

Pasos del protocolo (según AGENTS.md):
  1. assistant_id:  POST {BASE}/assistants/search  {"graph_id": GRAPH}  → UUID
  2. tarjeta:       GET  {BASE}/.well-known/agent-card.json?assistant_id=<uuid>
  3. enviar:        POST {BASE}/a2a/<uuid>  JSON-RPC message/send
                    · contextId = UUID fijo por conversación (= thread_id del remoto)
"""
from __future__ import annotations

import os
import uuid

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE = os.environ.get("A2A_VIAJES_URL", "http://127.0.0.1:2024")
GRAPH = os.environ.get("A2A_VIAJES_GRAPH", "agente_viajes")

# cache del assistant_id por (base, graph): el servidor lo mantiene fijo mientras vive.
_cache_aid: dict[tuple[str, str], str] = {}


def assistant_id(base: str = BASE, graph: str = GRAPH, timeout: float = 10) -> str:
    """UUID que el servidor de LangGraph asigna al grafo remoto."""
    clave = (base, graph)
    if clave not in _cache_aid:
        r = httpx.post(f"{base}/assistants/search", json={"graph_id": graph}, timeout=timeout).json()
        if not r:
            raise RuntimeError(f"El servidor no conoce el grafo '{graph}'. ¿Está corriendo `langgraph dev`?")
        _cache_aid[clave] = r[0]["assistant_id"]
    return _cache_aid[clave]


def agent_card(base: str = BASE, graph: str = GRAPH, timeout: float = 10) -> dict:
    """La Agent Card del agente remoto (nombre, descripción, skills, url del endpoint)."""
    aid = assistant_id(base, graph, timeout)
    return httpx.get(f"{base}/.well-known/agent-card.json", params={"assistant_id": aid}, timeout=timeout).json()


def nuevo_context_id() -> str:
    """Un contextId para una conversación nueva (el remoto lo usa como thread_id)."""
    return str(uuid.uuid4())


def _texto_de_resultado(result: dict) -> str:
    """Extrae el texto de la respuesta A2A (recorre artifacts/status buscando 'text')."""
    textos: list[str] = []

    def _walk(o):
        if isinstance(o, dict):
            if o.get("kind") == "text" and isinstance(o.get("text"), str):
                textos.append(o["text"])
            else:
                for v in o.values():
                    _walk(v)
        elif isinstance(o, list):
            for v in o:
                _walk(v)

    _walk(result)
    return "\n".join(t for t in textos if t.strip()) or str(result)


def enviar_mensaje(texto: str, context_id: str, base: str = BASE, graph: str = GRAPH, timeout: float = 90) -> str:
    """Manda `texto` al agente remoto en la conversación `context_id` y devuelve su respuesta.

    Reusar el mismo `context_id` en llamadas sucesivas hace que el remoto recuerde
    el hilo (memoria por conversación).
    """
    aid = assistant_id(base, graph, timeout)
    cuerpo = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "messageId": uuid.uuid4().hex,
                "contextId": context_id,
                "parts": [{"kind": "text", "text": texto}],
            }
        },
    }
    r = httpx.post(f"{base}/a2a/{aid}", json=cuerpo, timeout=timeout).json()
    if "error" in r:
        return f"[error del agente remoto: {r['error']}]"
    return _texto_de_resultado(r.get("result", r))
