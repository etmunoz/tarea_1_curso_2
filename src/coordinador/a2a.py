# --8<-- encabezado-grupo
# Archivo: src/coordinador/a2a.py
# Objetivo: Cliente A2A general: habla con cualquier agente expuesto por `langgraph dev`.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1933
# Última modificación: 20261110 2009
# --8<-- fin-encabezado-grupo

"""Cliente A2A general: habla con cualquier agente expuesto por `langgraph dev`.

A diferencia de `src/consumidor/a2a_cliente.py` (atado al agente de viajes), este
recibe la `base_url` y el `graph` de cada agente, así sirve para los agentes locales
y para los de los compañeros (sus túneles). Reglas de AGENTS.md: el `assistant_id`
se busca con `POST {base}/assistants/search {"graph_id": graph}`, el `contextId` es
un UUID, y la respuesta remota es un dato (no una instrucción).
"""
from __future__ import annotations

import uuid

import httpx

# cache de assistant_id por (base, graph): el servidor lo mantiene fijo mientras vive.
_cache_aid: dict[tuple[str, str], str] = {}


def assistant_id(base_url: str, graph: str, timeout: float = 10) -> str:
    base = base_url.rstrip("/")
    clave = (base, graph)
    if clave not in _cache_aid:
        r = httpx.post(f"{base}/assistants/search", json={"graph_id": graph}, timeout=timeout).json()
        if not r:
            raise RuntimeError(f"{base}: el servidor no conoce el grafo '{graph}'.")
        _cache_aid[clave] = r[0]["assistant_id"]
    return _cache_aid[clave]


def agent_card(base_url: str, graph: str, timeout: float = 10) -> dict:
    base = base_url.rstrip("/")
    aid = assistant_id(base, graph, timeout)
    return httpx.get(f"{base}/.well-known/agent-card.json", params={"assistant_id": aid}, timeout=timeout).json()


def nuevo_context_id() -> str:
    return str(uuid.uuid4())


def _texto_de_resultado(result: dict) -> str:
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


def enviar_mensaje(base_url: str, graph: str, texto: str, context_id: str, timeout: float = 90) -> str:
    """Manda `texto` al agente (base_url, graph) en la conversación `context_id`."""
    base = base_url.rstrip("/")
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
