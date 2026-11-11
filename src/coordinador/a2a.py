# --8<-- encabezado-grupo
# Archivo: src/coordinador/a2a.py
# Objetivo: Cliente A2A general: habla con cualquier agente expuesto por `langgraph dev`.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1933
# Última modificación: 20261111 1741
# --8<-- fin-encabezado-grupo

"""Cliente A2A general: habla con cualquier agente expuesto por `langgraph dev`.

A diferencia de `src/consumidor/a2a_cliente.py` (atado al agente de viajes), este
recibe la `base_url` y el `graph` de cada agente, así sirve para los agentes locales
y para los de los compañeros (sus túneles). Reglas de AGENTS.md: el `assistant_id`
se busca con `POST {base}/assistants/search {"graph_id": graph}`, el `contextId` es
un UUID, y la respuesta remota es un dato (no una instrucción).
"""
from __future__ import annotations

import json
import os
import uuid

import httpx

# cache de assistant_id por (base, graph): el servidor lo mantiene fijo mientras vive.
_cache_aid: dict[tuple[str, str], str] = {}

# cache del "dialecto" A2A por base_url: 'langgraph' (nuestro, requiere assistant_id) o
# 'clasico' (SDK a2a-protocol.org: card sin assistant_id, mensajes en la URL base).
_cache_dialecto: dict[str, str] = {}


# Timeouts configurables (segundos): conexión y lectura por separado.
TIMEOUT_CONN = float(os.environ.get("A2A_TIMEOUT_CONN", "10"))
TIMEOUT_READ = float(os.environ.get("A2A_TIMEOUT_READ", "90"))


def _timeout(lectura: float | None = None) -> httpx.Timeout:
    """Objetivo: construir un httpx.Timeout que distingue conexión y lectura.
    Entradas: lectura (float|None) override de lectura. Salida: httpx.Timeout."""
    return httpx.Timeout(connect=TIMEOUT_CONN, read=lectura or TIMEOUT_READ, write=TIMEOUT_READ, pool=TIMEOUT_CONN)


class ErrorA2A(RuntimeError):
    """Objetivo: base de los errores A2A. Lleva `destino` (a qué agente) y `motivo` (una frase),
    para que el coordinador arme un estado controlado sin exponer trazas internas."""

    def __init__(self, destino: str, motivo: str):
        self.destino = destino
        self.motivo = motivo
        super().__init__(f"{destino}: {motivo}")


class AgenteNoDisponible(ErrorA2A):
    """El agente no respondió por un problema de TRANSPORTE (conexión caída, timeout, red)."""


class ErrorProtocoloA2A(ErrorA2A):
    """El servidor respondió pero con un error de PROTOCOLO (JSON-RPC error, HTTP != 2xx que
    no es de transporte)."""


class RespuestaA2AInvalida(ErrorProtocoloA2A):
    """El servidor respondió 2xx pero el cuerpo no tiene la estructura A2A esperada
    (no es JSON, falta un campo obligatorio, tipos equivocados)."""


class IdentificadorAsistenteObsoleto(ErrorProtocoloA2A):
    """El `assistant_id` cacheado ya no existe en el servidor (404): se recarga y se reintenta
    una sola vez (la operación no llegó a ejecutarse, por eso es seguro reintentar)."""


class AccesoDenegadoA2A(ErrorProtocoloA2A):
    """El servidor respondió 401/403: el agente existe pero requiere autenticación/autorización.
    NO es un dialecto distinto ni indisponibilidad de transporte."""


def _motivo(exc: Exception) -> str:
    """Objetivo: traducir una excepción httpx/JSON a un motivo corto y legible (sin trazas).
    Distingue timeout de conexión, de lectura, HTTP y red. Salida: str."""
    if isinstance(exc, httpx.ConnectTimeout):
        return "tiempo de espera de conexión agotado"
    if isinstance(exc, httpx.ReadTimeout):
        return "tiempo de espera de lectura agotado"
    if isinstance(exc, httpx.TimeoutException):
        return "tiempo de espera agotado"
    if isinstance(exc, httpx.ConnectError):
        return "no se pudo conectar (¿túnel caído?)"
    if isinstance(exc, httpx.HTTPStatusError):
        return f"respondió con error HTTP {exc.response.status_code}"
    if isinstance(exc, httpx.HTTPError):
        return "error de red"
    return "respuesta ilegible del servidor"


def _pedir(metodo, url: str, destino: str, **kw) -> httpx.Response:
    """Objetivo: hacer la petición HTTP capturando SOLO errores de transporte como
    AgenteNoDisponible; NO llama raise_for_status (el llamador decide según el status).
    Adjunta el encabezado de autenticación (Bearer) si está configurado (auth.encabezados_auth).
    Entradas: metodo (httpx.get/post), url, destino, kw. Salida: httpx.Response."""
    from src.coordinador import auth  # noqa: PLC0415 - import tardío para evitar ciclos
    kw.setdefault("timeout", _timeout(kw.pop("_lectura", None)))
    auth_headers = auth.encabezados_auth(url)  # token POR DESTINO (no se filtra a terceros)
    if auth_headers:
        kw["headers"] = {**auth_headers, **(kw.get("headers") or {})}
    try:
        return metodo(url, **kw)
    except httpx.HTTPError as exc:
        raise AgenteNoDisponible(destino, _motivo(exc)) from exc


def _json(metodo, url: str, destino: str, **kw) -> dict | list:
    """Objetivo: petición + JSON, convirtiendo transporte → AgenteNoDisponible, HTTP != 2xx
    → ErrorProtocoloA2A y cuerpo no-JSON → RespuestaA2AInvalida.
    Entradas: metodo, url, destino, kw. Salida: dict|list — el JSON."""
    r = _pedir(metodo, url, destino, **kw)
    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as exc:
        # Un HTTP != 2xx es, para el usuario, indisponibilidad del agente.
        raise AgenteNoDisponible(destino, _motivo(exc)) from exc
    try:
        return r.json()
    except ValueError as exc:  # json.JSONDecodeError hereda de ValueError
        raise RespuestaA2AInvalida(destino, "respuesta ilegible del servidor") from exc


def dialecto(base_url: str, timeout: float = 10) -> str:
    """Objetivo: detectar (una vez, con caché) qué dialecto A2A habla un servidor.
    Pide la Agent Card SIN assistant_id: un servidor 'clasico' (SDK a2a-protocol.org)
    la devuelve con `name`; nuestro langgraph dev responde un error pidiendo el
    `assistant_id`. Entradas: base_url (str), timeout (float).
    Salida: str — 'clasico' o 'langgraph'. Lanza AgenteNoDisponible si no hay red."""
    base = base_url.rstrip("/")
    if base not in _cache_dialecto:
        # Misma capa HTTP que el resto (auth, timeouts, transporte → AgenteNoDisponible).
        r = _pedir(httpx.get, f"{base}/.well-known/agent-card.json", base, timeout=timeout)
        if r.status_code in (401, 403):
            raise AccesoDenegadoA2A(base, f"acceso denegado al descubrir (HTTP {r.status_code})")
        try:
            data = r.json()
        except ValueError:
            data = None
        pide_assistant_id = isinstance(data, dict) and "assistant_id" in json.dumps(data)
        if r.status_code == 200 and isinstance(data, dict) and bool(data.get("name")):
            _cache_dialecto[base] = "clasico"
        elif pide_assistant_id:
            # langgraph responde un error pidiendo el assistant_id (típicamente 4xx).
            _cache_dialecto[base] = "langgraph"
        else:
            # NO se clasifica a ciegas como langgraph: dialecto desconocido.
            raise RespuestaA2AInvalida(
                base, f"no es una Agent Card clásica ni un error langgraph reconocible (HTTP {r.status_code})")
    return _cache_dialecto[base]


def _card_clasica(base: str, timeout: float) -> dict:
    """Objetivo: leer la Agent Card de un servidor A2A clásico (sin assistant_id)."""
    return _json(httpx.get, f"{base}/.well-known/agent-card.json", base, timeout=timeout)


def _endpoint_clasico(card: dict, base: str) -> str:
    """Objetivo: sacar la URL del endpoint de mensajes de una card clásica.
    Usa `url` o la primera `supportedInterfaces[].url`; si no hay, la base. Salida: str."""
    card = card if isinstance(card, dict) else {}
    url = card.get("url")
    if not url:
        interfaces = card.get("supportedInterfaces") or card.get("additionalInterfaces") or []
        if isinstance(interfaces, list) and interfaces and isinstance(interfaces[0], dict):
            url = interfaces[0].get("url")
    return (url if isinstance(url, str) and url else base).rstrip("/")


def _cuerpo_message_send(texto: str, context_id: str) -> dict:
    """Objetivo: JSON-RPC estándar `message/send` (langgraph y a2a-protocol.org).
    Entradas: texto, context_id. Salida: dict."""
    return {
        "jsonrpc": "2.0", "id": "1", "method": "message/send",
        "params": {"message": {"role": "user", "kind": "message", "messageId": uuid.uuid4().hex,
                               "contextId": context_id, "parts": [{"kind": "text", "text": texto}]}},
    }


def _cuerpo_sendmessage(texto: str, context_id: str) -> dict:
    """Objetivo: variante `SendMessage` que usa el servidor de un compañero (role ROLE_USER,
    parts sin `kind`). Se usa como FALLBACK cuando `message/send` da -32601 en dialecto clásico.
    Entradas: texto, context_id. Salida: dict."""
    return {
        "jsonrpc": "2.0", "id": "1", "method": "SendMessage",
        "params": {"message": {"role": "ROLE_USER", "messageId": uuid.uuid4().hex,
                               "contextId": context_id, "parts": [{"text": texto}]}},
    }


def _codigo_error(datos) -> int | None:
    """Objetivo: código de un error JSON-RPC, si lo hay. Entradas: datos. Salida: int|None."""
    if isinstance(datos, dict) and isinstance(datos.get("error"), dict):
        cod = datos["error"].get("code")
        return cod if isinstance(cod, int) else None
    return None


def _desanidar(texto: str) -> str:
    """Objetivo: algunos servidores (p. ej. el agente del compañero) devuelven el texto DENTRO
    de un string con un repr de lista/dict: "[{'type':'text','text':'...','extras':{...}}]".
    Si el texto es exactamente eso, se extrae el/los `text` internos; si no, se devuelve igual.
    Entradas: texto (str). Salida: str."""
    t = (texto or "").strip()
    if not (t.startswith("[") or t.startswith("{")):
        return texto
    try:
        import ast  # noqa: PLC0415
        valor = ast.literal_eval(t)
    except (ValueError, SyntaxError):
        return texto
    internos = _textos(valor)  # reutiliza el extractor recursivo de 'text'
    return "\n".join(internos) if internos else texto


def assistant_id(base_url: str, graph: str, timeout: float = 10) -> str:
    """Objetivo: obtener el assistant_id (UUID) que el servidor asigna a un grafo (con caché).
    Entradas: base_url (str) del servidor; graph (str) id del grafo; timeout (float) segundos.
    Salida: str — el assistant_id. Lanza RuntimeError si el servidor no conoce el grafo."""
    base = base_url.rstrip("/")
    clave = (base, graph)
    destino = f"{base} ({graph})"
    if clave not in _cache_aid:
        r = _json(httpx.post, f"{base}/assistants/search", destino,
                  json={"graph_id": graph}, timeout=timeout)
        # Validación estructural: lista NO vacía de dicts con 'assistant_id' str.
        if not isinstance(r, list):
            raise RespuestaA2AInvalida(destino, "la búsqueda de asistentes no devolvió una lista")
        if not r:
            raise AgenteNoDisponible(destino, f"el servidor no conoce el grafo '{graph}'")
        primero = r[0]
        aid = primero.get("assistant_id") if isinstance(primero, dict) else None
        if not isinstance(aid, str) or not aid:
            raise RespuestaA2AInvalida(destino, "la búsqueda no trae un 'assistant_id' válido")
        _cache_aid[clave] = aid
    return _cache_aid[clave]


def invalidar_assistant_id(base_url: str, graph: str) -> None:
    """Objetivo: invalidar SOLO la entrada de caché del assistant_id de un grafo (p. ej. tras un
    404 porque el servidor se reinició). Entradas: base_url, graph. Salida: None."""
    _cache_aid.pop((base_url.rstrip("/"), graph), None)


def agent_card(base_url: str, graph: str, timeout: float = 10) -> dict:
    """Objetivo: leer la Agent Card (tarjeta A2A) de un agente.
    Entradas: base_url (str), graph (str), timeout (float).
    Salida: dict — la tarjeta (name, description, skills, url…)."""
    base = base_url.rstrip("/")
    if dialecto(base, timeout) == "clasico":
        return _card_clasica(base, timeout)
    aid = assistant_id(base, graph, timeout)
    return _json(httpx.get, f"{base}/.well-known/agent-card.json", f"{base} ({graph})",
                 params={"assistant_id": aid}, timeout=timeout)


def nuevo_context_id() -> str:
    """Objetivo: generar un contextId A2A nuevo. Entradas: ninguna. Salida: str — un UUID."""
    return str(uuid.uuid4())


def a_uuid(valor) -> str:
    """Objetivo: coaccionar un contextId arbitrario a un UUID válido y ESTABLE. langgraph dev
    usa el contextId como thread_id y exige un UUID ('Invalid thread ID' si no lo es); un
    cliente A2A externo puede mandar cualquier string. Si ya es UUID se respeta; si no, se
    deriva uuid5 (mismo texto → mismo UUID, así se preserva la memoria del hilo).
    Entradas: valor (str u otro). Salida: str — un UUID."""
    try:
        return str(uuid.UUID(str(valor)))
    except (ValueError, AttributeError, TypeError):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, str(valor)))


def _textos(o) -> list[str]:
    """Objetivo: juntar los `text` de las partes A2A dentro de un dict/list (recursivo).
    Entradas: o (dict | list | otro). Salida: list[str] — textos no vacíos, en orden."""
    if isinstance(o, dict):
        # Una "parte de texto" es cualquier dict con un campo `text` de tipo str: cubre
        # langgraph/a2a estándar ({kind:text,text}), la variante del compañero ({type:text,text})
        # y partes mínimas ({text}). No recurre más dentro de esa parte.
        if isinstance(o.get("text"), str):
            return [o["text"]] if o["text"].strip() else []
        return [t for v in o.values() for t in _textos(v)]
    if isinstance(o, list):
        return [t for v in o for t in _textos(v)]
    return []


def _texto_de_resultado(result, destino: str = "") -> str:
    """Objetivo: extraer la RESPUESTA del agente de un resultado A2A (sin repetir nada).
    El resultado trae la respuesta en `artifacts` y además el `history` completo (la
    pregunta del usuario y la misma respuesta otra vez). Por eso se toma, en orden:
    1) los `artifacts`; 2) el mensaje de `status`; 3) el último mensaje del agente en
    `history`; 4) como último recurso, todos los textos.
    Validación ESTRICTA: tolera que `result`, `status`, `history` o sus elementos vengan como
    listas, cadenas o null sin lanzar AttributeError/TypeError/IndexError/KeyError. Si no hay
    NINGÚN texto extraíble, NO devuelve `str(result)` como si fuera válido: lanza
    RespuestaA2AInvalida (resultado sin texto). Entradas: result (cualquier tipo), destino (str
    etiqueta). Salida: str — el texto de la respuesta."""
    def _d(o):
        return o if isinstance(o, dict) else {}

    historial = _d(result).get("history")
    historial = historial if isinstance(historial, list) else []
    ultimo_agente = next((m for m in reversed(historial)
                          if isinstance(m, dict) and m.get("role") == "agent"), None)
    candidatos = [
        _d(result).get("artifacts"),
        _d(_d(result).get("status")).get("message"),
        ultimo_agente,
        result,
    ]
    for c in candidatos:
        textos = _textos(c) if c else []
        if textos:
            return "\n".join(textos)
    raise RespuestaA2AInvalida(destino, "la respuesta A2A no contiene texto")


def enviar_mensaje(base_url: str, graph: str, texto: str, context_id: str, timeout: float = 90) -> str:
    """Objetivo: enviar `texto` a un agente por A2A (message/send) y devolver su respuesta.
    Entradas: base_url (str), graph (str), texto (str) la pregunta, context_id (str) UUID de la
    conversación (memoria del remoto), timeout (float).
    Salida: str — el texto de la respuesta del agente (o un aviso del propio protocolo A2A).
    Lanza AgenteNoDisponible si el agente no responde (conexión/timeout/HTTP/JSON).
    Habla ambos dialectos: langgraph (`/a2a/<assistant_id>`) y clásico (URL base)."""
    base = base_url.rstrip("/")
    cuerpo = _cuerpo_message_send(texto, context_id)
    destino = f"{base} ({graph})"
    es_clasico = dialecto(base, timeout) == "clasico"

    def _una_vez() -> httpx.Response:
        if es_clasico:
            endpoint = _endpoint_clasico(_card_clasica(base, timeout), base)
        else:
            endpoint = f"{base}/a2a/{assistant_id(base, graph, timeout)}"
        return _pedir(httpx.post, endpoint, destino, json=cuerpo, _lectura=timeout)

    r = _una_vez()
    # Recuperación ACOTADA de assistant_id obsoleto: solo en langgraph y solo ante 404 (el
    # endpoint no existe ⇒ la operación NO se ejecutó, es seguro reintentar). Se invalida SOLO
    # esta entrada, se re-busca y se reintenta como MÁXIMO una vez. Si el id no cambió, la
    # búsqueda queda vacía/ inválida o el 404 persiste, se termina con error controlado y SIN
    # bucles. Un 404 "clásico" o uno no relacionado no dispara reintento de operaciones no
    # idempotentes.
    if r.status_code == 404 and not es_clasico:
        viejo = _cache_aid.get((base, graph))
        invalidar_assistant_id(base, graph)
        nuevo = assistant_id(base, graph, timeout)  # re-búsqueda (lanza si vacía/malformada)
        if nuevo == viejo:
            raise IdentificadorAsistenteObsoleto(destino, "el assistant_id no cambió tras recargar")
        r = _pedir(httpx.post, f"{base}/a2a/{nuevo}", destino, json=cuerpo, _lectura=timeout)
        if r.status_code == 404:
            raise IdentificadorAsistenteObsoleto(destino, "el asistente sigue sin existir tras recargar")
    if r.status_code in (401, 403):
        raise AccesoDenegadoA2A(destino, f"acceso denegado (HTTP {r.status_code})")
    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise AgenteNoDisponible(destino, _motivo(exc)) from exc
    try:
        datos = r.json()
    except ValueError as exc:
        raise RespuestaA2AInvalida(destino, "respuesta ilegible del servidor") from exc
    # Fallback de interoperabilidad: algunos servidores A2A clásicos no implementan
    # `message/send` (responden -32601) sino `SendMessage` (role ROLE_USER, parts sin kind,
    # header A2A-Version). Se reintenta UNA vez con esa variante.
    if es_clasico and _codigo_error(datos) == -32601:
        endpoint = _endpoint_clasico(_card_clasica(base, timeout), base)
        r = _pedir(httpx.post, endpoint, destino, json=_cuerpo_sendmessage(texto, context_id),
                   headers={"A2A-Version": "1.0"}, _lectura=timeout)
        try:
            datos = r.json()
        except ValueError as exc:
            raise RespuestaA2AInvalida(destino, "respuesta ilegible del servidor") from exc

    if isinstance(datos, dict) and datos.get("error"):
        # Error JSON-RPC del servidor remoto: es un error de PROTOCOLO (no de transporte).
        raise ErrorProtocoloA2A(destino, f"error del agente remoto: {datos['error']}")
    bruto = _texto_de_resultado(datos.get("result", datos) if isinstance(datos, dict) else datos, destino)
    # Algunos servidores devuelven el texto dentro de un repr de lista/dict: se desanida.
    return _desanidar(bruto)
