# --8<-- encabezado-grupo
# Archivo: src/coordinador/a2a.py
# Objetivo: Cliente A2A general: habla con cualquier agente expuesto por `langgraph dev`.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1933
# Última modificación: 20261111 0730
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


class AgenteNoDisponible(RuntimeError):
    """Objetivo: señalar que un agente remoto no respondió (conexión caída, timeout,
    respuesta HTTP inválida o JSON ilegible). Lleva `destino` (a qué agente se intentó)
    y `motivo` (en una frase) para que el coordinador arme un estado controlado."""

    def __init__(self, destino: str, motivo: str):
        self.destino = destino
        self.motivo = motivo
        super().__init__(f"{destino}: {motivo}")


def _motivo(exc: Exception) -> str:
    """Objetivo: traducir una excepción httpx/JSON a un motivo corto y legible.
    Entradas: exc (Exception). Salida: str — el motivo para el usuario/log."""
    if isinstance(exc, httpx.TimeoutException):
        return "tiempo de espera agotado"
    if isinstance(exc, httpx.ConnectError):
        return "no se pudo conectar (¿túnel caído?)"
    if isinstance(exc, httpx.HTTPStatusError):
        return f"respondió con error HTTP {exc.response.status_code}"
    if isinstance(exc, httpx.HTTPError):
        return "error de red"
    return "respuesta ilegible del servidor"


def _json(metodo, url: str, destino: str, **kw) -> dict | list:
    """Objetivo: hacer una petición HTTP y devolver su JSON, convirtiendo CUALQUIER fallo
    (conexión, timeout, HTTP != 2xx, JSON inválido) en AgenteNoDisponible(destino, motivo).
    Entradas: metodo (callable httpx.get/post), url (str), destino (str) etiqueta del agente,
    kw (dict) argumentos de httpx. Salida: dict|list — el JSON de la respuesta."""
    try:
        r = metodo(url, **kw)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as exc:
        raise AgenteNoDisponible(destino, _motivo(exc)) from exc
    except ValueError as exc:  # json.JSONDecodeError hereda de ValueError
        raise AgenteNoDisponible(destino, _motivo(exc)) from exc


def assistant_id(base_url: str, graph: str, timeout: float = 10) -> str:
    """Objetivo: obtener el assistant_id (UUID) que el servidor asigna a un grafo (con caché).
    Entradas: base_url (str) del servidor; graph (str) id del grafo; timeout (float) segundos.
    Salida: str — el assistant_id. Lanza RuntimeError si el servidor no conoce el grafo."""
    base = base_url.rstrip("/")
    clave = (base, graph)
    if clave not in _cache_aid:
        r = _json(httpx.post, f"{base}/assistants/search", f"{base} ({graph})",
                  json={"graph_id": graph}, timeout=timeout)
        if not r:
            raise AgenteNoDisponible(f"{base} ({graph})", f"el servidor no conoce el grafo '{graph}'")
        _cache_aid[clave] = r[0]["assistant_id"]
    return _cache_aid[clave]


def agent_card(base_url: str, graph: str, timeout: float = 10) -> dict:
    """Objetivo: leer la Agent Card (tarjeta A2A) de un agente.
    Entradas: base_url (str), graph (str), timeout (float).
    Salida: dict — la tarjeta (name, description, skills, url…)."""
    base = base_url.rstrip("/")
    aid = assistant_id(base, graph, timeout)
    return _json(httpx.get, f"{base}/.well-known/agent-card.json", f"{base} ({graph})",
                 params={"assistant_id": aid}, timeout=timeout)


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
    Salida: str — el texto de la respuesta del agente (o un aviso del propio protocolo A2A).
    Lanza AgenteNoDisponible si el agente no responde (conexión/timeout/HTTP/JSON)."""
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
    r = _json(httpx.post, f"{base}/a2a/{aid}", f"{base} ({graph})", json=cuerpo, timeout=timeout)
    if isinstance(r, dict) and "error" in r:
        return f"[error del agente remoto: {r['error']}]"
    return _texto_de_resultado(r.get("result", r) if isinstance(r, dict) else r)
