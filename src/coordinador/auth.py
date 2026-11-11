# --8<-- encabezado-grupo
# Archivo: src/coordinador/auth.py
# Objetivo: Autenticación y autorización A2A — alcance académico (prompt 48, Corrección 3).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 1405
# Última modificación: 20261111 1438
# --8<-- fin-encabezado-grupo

"""Autenticación y autorización A2A — alcance académico (prompt 48, Corrección 3).

HONESTO (lee esto): un **allow-list NO es autenticación**. Aquí se implementan los controles
**verificables** que sí son posibles sin montar infraestructura de identidad fuera del
repositorio, y se documentan explícitamente los límites:

- **Cliente (verificable):** adjunta `Authorization: Bearer <A2A_TOKEN>` si está configurado
  (`encabezados_auth`). Las credenciales vienen de variables de entorno, nunca hardcodeadas,
  y nunca se registran completas (`enmascarar_token`).
- **Autorización (verificable, mínimo privilegio):** `autorizar(graph, operacion)` separa la
  AUTORIZACIÓN de la autenticación: el grafo debe estar en el allow-list y la operación debe
  estar permitida.
- **Identidad (referencia):** `cargar_identidades()` vincula grafo → {endpoint, capacidades}
  desde `A2A_IDENTIDADES` (JSON); valida configuración incompleta.
- **Servidor (referencia, NO exigido por defecto):** `validar_token()` es la pieza que un
  middleware o el *custom auth* de LangGraph usaría para EXIGIR el token en el **receptor**.
  Montarla efectivamente requiere habilitar auth en el servidor (fuera del alcance por
  defecto para no romper la demo). **Limitación registrada:** sin esa validación en el
  receptor, el token del cliente no constituye autenticación fuerte; es un modo de
  demostración local (`A2A_MODO_DEMO`).
"""
from __future__ import annotations

import json
import os
from urllib.parse import urlparse

# Operaciones A2A que el coordinador puede ejecutar (para el control de autorización).
OPERACIONES = {"agent_card", "message_send"}


def _hosts_confiables() -> set[str]:
    """Objetivo: hosts a los que SÍ se envía nuestro token (prompt 48b). El token es una
    credencial propia: NO debe mandarse a servidores de terceros (p. ej. el de Gustavo) solo
    porque estén en el catálogo. Confiables = host de `A2A_BASE` + `A2A_HOSTS_CONFIABLES` +
    localhost. Entradas: ninguna. Salida: set[str] de hostnames."""
    confiables = {"127.0.0.1", "localhost", "::1"}
    base = os.environ.get("A2A_BASE", "http://127.0.0.1:2024")
    h = urlparse(base).hostname
    if h:
        confiables.add(h)
    confiables |= (_conjunto("A2A_HOSTS_CONFIABLES") or set())
    return confiables


def token_para(url: str) -> str:
    """Objetivo: token a enviar a `url` SOLO si su host es confiable; si no, '' (no se envía).
    Evita filtrar la credencial a endpoints arbitrarios. Entradas: url (str). Salida: str."""
    host = urlparse(url or "").hostname
    return token_cliente() if host in _hosts_confiables() else ""


def token_cliente() -> str:
    """Objetivo: token Bearer del cliente (de A2A_TOKEN, nunca hardcodeado). Salida: str (o '')."""
    return os.environ.get("A2A_TOKEN", "").strip()


def enmascarar_token(token: str) -> str:
    """Objetivo: enmascarar un token para logs/evidencias (nunca el valor completo).
    Entradas: token (str). Salida: str — p. ej. 'abcd…(12)'."""
    if not token:
        return "(sin token)"
    return f"{token[:4]}…({len(token)})"


def encabezados_auth(url: str | None = None) -> dict:
    """Objetivo: encabezados de autenticación para una petición A2A saliente. Si se pasa `url`,
    el token se adjunta SOLO cuando el host es confiable (token por destino, prompt 48b); sin
    `url` usa el token global (compatibilidad). Entradas: url (str|None).
    Salida: dict — {'Authorization': 'Bearer …'} o {} si no corresponde."""
    t = token_para(url) if url is not None else token_cliente()
    return {"Authorization": f"Bearer {t}"} if t else {}


def _conjunto(nombre: str) -> set[str] | None:
    """Objetivo: leer una variable coma-separada a set, o None si no está definida."""
    v = os.environ.get(nombre, "").strip()
    s = {x.strip() for x in v.split(",") if x.strip()}
    return s or None


def autorizar(graph: str, operacion: str) -> tuple[bool, str]:
    """Objetivo (autorización, mínimo privilegio): decidir si se permite `operacion` sobre `graph`.
    Reglas: el grafo debe estar en `A2A_AGENTES_PERMITIDOS` (si está definido), la operación en
    `A2A_OPERACIONES_PERMITIDAS` (si está definido), y ser una operación conocida.
    Entradas: graph (str), operacion (str). Salida: (ok (bool), motivo (str))."""
    if operacion not in OPERACIONES:
        return False, f"operación desconocida '{operacion}'"
    permitidos = _conjunto("A2A_AGENTES_PERMITIDOS")
    if permitidos is not None and graph not in permitidos:
        return False, f"grafo '{graph}' no autorizado"
    ops = _conjunto("A2A_OPERACIONES_PERMITIDAS")
    if ops is not None and operacion not in ops:
        return False, f"operación '{operacion}' no autorizada"
    return True, ""


def validar_token(token: str) -> bool:
    """Objetivo (lado SERVIDOR, referencia): validar un Bearer contra `A2A_TOKENS_VALIDOS`
    (coma-separada). Para constituir autenticación debe ejecutarse en el RECEPTOR (middleware o
    custom auth de langgraph); por sí sola, en el cliente, no es seguridad efectiva.
    Entradas: token (str). Salida: bool."""
    validos = _conjunto("A2A_TOKENS_VALIDOS") or set()
    return bool(token) and token in validos


def cargar_identidades() -> dict:
    """Objetivo (identidad, referencia): mapear grafo → {endpoint, capacidades} desde
    `A2A_IDENTIDADES` (JSON). Valida que sea JSON y un objeto; {} si no está configurado.
    Entradas: ninguna. Salida: dict. Lanza ValueError si la config está malformada."""
    crudo = os.environ.get("A2A_IDENTIDADES", "").strip()
    if not crudo:
        return {}
    try:
        data = json.loads(crudo)
    except ValueError as exc:
        raise ValueError(f"A2A_IDENTIDADES no es JSON válido: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("A2A_IDENTIDADES debe ser un objeto {graph: {...}}")
    return data


def modo_demo() -> bool:
    """Objetivo: True si corre en modo demo local (sin exigencia de token en el receptor).
    Entradas: ninguna. Salida: bool (def. True si no hay tokens válidos configurados)."""
    return os.environ.get("A2A_MODO_DEMO", "").strip().lower() in {"1", "true", "si", "sí"} \
        or _conjunto("A2A_TOKENS_VALIDOS") is None
