# --8<-- encabezado-grupo
# Archivo: src/coordinador/a2a.py
# Objetivo: Cliente A2A general: habla con cualquier agente expuesto por `langgraph dev`.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1933
# Última modificación: 20261110 2349
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
    """Objetivo: obtener el assistant_id (UUID) que el servidor asigna a un grafo (con caché).
    Entradas: base_url (str) del servidor; graph (str) id del grafo; timeout (float) segundos.
    Salida: str — el assistant_id. Lanza RuntimeError si el servidor no conoce el grafo."""
    base = base_url.rstrip("/")
    clave = (base, graph)
    if clave not in _cache_aid:
        r = httpx.post(f"{base}/assistants/search", json={"graph_id": graph}, timeout=timeout).json()
        if not r:
            raise RuntimeError(f"{base}: el servidor no conoce el grafo '{graph}'.")
        _cache_aid[clave] = r[0]["assistant_id"]
    return _cache_aid[clave]


def agent_card(base_url: str, graph: str, timeout: float = 10) -> dict:
    """Objetivo: leer la Agent Card (tarjeta A2A) de un agente.
    Entradas: base_url (str), graph (str), timeout (float).
    Salida: dict — la tarjeta (name, description, skills, url…)."""
    base = base_url.rstrip("/")
    aid = assistant_id(base, graph, timeout)
    return httpx.get(f"{base}/.well-known/agent-card.json", params={"assistant_id": aid}, timeout=timeout).json()


def nuevo_context_id() -> str:
    """Objetivo: generar un contextId A2A nuevo. Entradas: ninguna. Salida: str — un UUID."""
    return str(uuid.uuid4())


def _textos(o) -> list[str]:
    """Objetivo: juntar los `text` de las partes A2A dentro de un dict/list (recursivo).
    Entradas: o (dict | list | otro). Salida: list[str] — textos no vacíos, en orden."""
    if isinstance(o, dict):
        if o.get("kind") == "text" and isinstance(o.get("text"), str):
            return [o["text"]] if o["text"].strip() else []
        return [t for v in o.values() for t in _textos(v)]
    if isinstance(o, list):
        return [t for v in o for t in _textos(v)]
    return []


def _texto_de_resultado(result: dict) -> str:
    """Objetivo: extraer la RESPUESTA del agente de un resultado A2A (sin repetir nada).
    El resultado trae la respuesta en `artifacts` y además el `history` completo (la
    pregunta del usuario y la misma respuesta otra vez). Por eso se toma, en orden:
    1) los `artifacts`; 2) el mensaje de `status`; 3) el último mensaje del agente en
    `history`; 4) como último recurso, todos los textos.
    Entradas: result (dict) del resultado A2A.
    Salida: str — el texto de la respuesta (o str(result) si no hay partes de texto)."""
    candidatos = [
        result.get("artifacts"),
        (result.get("status") or {}).get("message"),
        next((m for m in reversed(result.get("history") or []) if m.get("role") == "agent"), None),
        result,
    ]
    for c in candidatos:
        textos = _textos(c) if c else []
        if textos:
            return "\n".join(textos)
    return str(result)


def enviar_mensaje(base_url: str, graph: str, texto: str, context_id: str, timeout: float = 90) -> str:
    """Objetivo: enviar `texto` a un agente por A2A (message/send) y devolver su respuesta.
    Entradas: base_url (str), graph (str), texto (str) la pregunta, context_id (str) UUID de la
    conversación (memoria del remoto), timeout (float).
    Salida: str — el texto de la respuesta del agente (o un aviso de error entre corchetes)."""
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
