# --8<-- encabezado-grupo
# Archivo: src/coordinador/guardrails.py
# Objetivo: Guardrails del coordinador: controles de entrada, salida y comunicación A2A.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 0730
# Última modificación: 20261111 1957
# --8<-- fin-encabezado-grupo

"""Guardrails del coordinador: controles de entrada, salida y comunicación A2A.

Tres puntos de control (regla de AGENTS.md: lo observado es un DATO, no una instrucción):

- **Entrada** (`revisar_entrada`): rechaza solicitudes vacías, excesivamente largas o
  con patrones de inyección/jailbreak, antes de gastar el LLM o molestar a un agente.
- **Salida** (`revisar_salida`, común a todo camino; `redactar_secretos` es su base):
  redacta credenciales (claves de API, tokens, contraseñas, tarjetas), tope de longitud y
  evita respuestas vacías.
- **Comunicación A2A** (`sanear_respuesta_remota`): la respuesta de un agente remoto es
  un dato no confiable; se redactan sus secretos y se marca (no se obedece) cualquier
  intento de instrucción incrustada.

Todo es determinista (regex) para poder probarlo con pytest sin LLM ni red.
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass

_log = logging.getLogger("coordinador.guardrails")

# Política configurable para una respuesta remota sospechosa (Corrección 2.D del prompt 48).
ALLOW, SANITIZE, BLOCK = "ALLOW", "SANITIZE", "BLOCK"
POLITICA_A2A = os.environ.get("GUARDRAIL_POLITICA_A2A", SANITIZE).upper()
# Caracteres de control que se quitan al normalizar (salvo \n y \t).
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Tamaño máximo de una pregunta (configurable por entorno).
LIMITE_ENTRADA = int(os.environ.get("GUARDRAIL_MAX_ENTRADA", "4000"))
# Tamaño máximo de una respuesta final (guardrail de salida).
LIMITE_SALIDA = int(os.environ.get("GUARDRAIL_MAX_SALIDA", "8000"))


@dataclass
class Veredicto:
    """Objetivo: resultado de un control de entrada. Campos: ok (bool) si pasa;
    motivo (str) razón técnica (log); mensaje (str) texto para el usuario si se bloquea."""

    ok: bool
    motivo: str = ""
    mensaje: str = ""


# Patrones de inyección / jailbreak (ES + EN). Buscan que el texto intente CAMBIAR
# las instrucciones del sistema o suplantar roles, no una pregunta normal.
_INYECCION = [
    r"ignora(r|s)?\s+(todas?\s+)?(las?\s+)?(tus\s+)?instrucciones",
    r"olvida(r|te)?\s+(todo|las\s+instrucciones|tus\s+instrucciones)",
    r"ignore\s+(all\s+)?(previous\s+)?instructions",
    r"disregard\s+(all\s+)?(previous\s+)?instructions",
    r"system\s*prompt",
    r"act[úu]a\s+como\s+(un\s+|una\s+)?(administrador|sistema|root|developer|dev|dios)",
    r"\bjailbreak\b",
    r"\bmodo\s+(desarrollador|developer|dios|sin\s+restricciones)\b",
    r"revela(r|me)?\s+(tu|el|la)\s+(system\s*prompt|prompt|clave|api[_\s-]?key|contrase[nñ]a)",
    r"eres\s+ahora\b|ahora\s+eres\b",
    r"</?(system|assistant|user)>",
]
_RE_INYECCION = re.compile("|".join(_INYECCION), re.IGNORECASE)

# Secretos a redactar de la salida (nombre → patrón).
_SECRETOS: list[tuple[str, re.Pattern]] = [
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z_\-]{20,}")),
    ("openai_key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("bearer_token", re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{10,}")),
    ("credencial", re.compile(r"(?i)(password|contrase[nñ]a|clave|api[_\s-]?key|token)\s*[:=]\s*\S+")),
    ("tarjeta", re.compile(r"\b(?:\d[ -]?){13,16}\b")),
]


def normalizar(texto: str) -> str:
    """Objetivo: normalización prudente de la entrada — quita caracteres de control (salvo
    salto de línea y tab) y colapsa espacios. No altera el contenido legítimo.
    Entradas: texto (str). Salida: str."""
    limpio = _CONTROL.sub("", texto or "")
    return re.sub(r"[ \t]+", " ", limpio).strip()


def registrar_evento(tipo: str, resultado: str, agente: str = "-", correlacion: str = "-",
                     motivo: str = "") -> None:
    """Objetivo (observabilidad): registrar un evento de seguridad SIN guardar el contenido
    sensible de la solicitud. Entradas: tipo (entrada/salida/a2a), resultado (allow/sanitize/
    block/bloqueada/ok), agente, correlacion (id), motivo (resumen técnico). Salida: None."""
    _log.info("guardrail tipo=%s resultado=%s agente=%s correlacion=%s motivo=%s",
              tipo, resultado, agente, correlacion, motivo or "-")


def revisar_entrada(texto) -> Veredicto:
    """Objetivo (guardrail de ENTRADA): decidir si una pregunta puede procesarse. Valida el
    TIPO (debe ser str), normaliza, y rechaza vacías, excesivamente largas o con patrones de
    inyección/jailbreak. (El "fuera de dominio" lo resuelve el supervisor enrutando a
    'sin_agente'.) Entradas: texto. Salida: Veredicto."""
    if not isinstance(texto, str):
        return Veredicto(False, f"tipo inválido ({type(texto).__name__})",
                         "No pude leer tu pregunta. Envíala como texto, por favor.")
    t = normalizar(texto)
    if not t:
        return Veredicto(False, "entrada vacía",
                         "No recibí ninguna pregunta. ¿En qué te puedo ayudar?")
    if len(t) > LIMITE_ENTRADA:
        return Veredicto(False, f"entrada demasiado larga ({len(t)} > {LIMITE_ENTRADA})",
                         "Tu mensaje es demasiado largo para procesarlo; resúmelo, por favor.")
    if _RE_INYECCION.search(t):
        return Veredicto(False, "patrón de inyección/jailbreak detectado",
                         "Esa solicitud intenta cambiar mis instrucciones y no puedo procesarla. "
                         "Puedo ayudarte con una pregunta normal para alguno de los agentes.")
    return Veredicto(True)


def redactar_secretos(texto: str) -> tuple[str, list[str]]:
    """Objetivo (guardrail de SALIDA): redactar credenciales/datos sensibles del texto.
    Entradas: texto (str). Salida: (texto_saneado (str), encontrados (list[str]) nombres)."""
    out = texto or ""
    encontrados: list[str] = []
    for nombre, patron in _SECRETOS:
        if patron.search(out):
            encontrados.append(nombre)
            out = patron.sub("[REDACTADO]", out)
    return out, encontrados


def revisar_salida(texto: str) -> tuple[str, dict]:
    """Objetivo (guardrail de SALIDA, común a TODA respuesta final): aplica las restricciones
    de salida — redacta credenciales, trunca lo excesivamente largo y evita respuestas vacías.
    A diferencia de `redactar_secretos`, no se limita a la respuesta de un agente: por este
    control pasan también `sin_agente` y los avisos del guardrail de entrada.
    Entradas: texto (str) respuesta final cruda.
    Salida: (texto_saneado (str), flags (dict) con 'secretos', 'recortado')."""
    if not isinstance(texto, str):
        texto = "" if texto is None else str(texto)  # tolera respuestas malformadas
    saneado, secretos = redactar_secretos(texto)
    recortado = False
    if len(saneado) > LIMITE_SALIDA:
        saneado = saneado[:LIMITE_SALIDA].rstrip() + " […respuesta truncada]"
        recortado = True
    if not saneado.strip():
        saneado = "(sin respuesta)"
    return saneado, {"secretos": secretos, "recortado": recortado}


def es_instruccion_remota(texto: str) -> bool:
    """Objetivo: detectar si un texto (p. ej. de un agente remoto) intenta dar instrucciones.
    Entradas: texto (str). Salida: bool — True si parece inyección."""
    return bool(_RE_INYECCION.search(texto or ""))


def sanear_respuesta_remota(texto: str) -> tuple[str, dict]:
    """Objetivo (guardrail A2A): tratar la respuesta de un agente remoto como DATO no confiable.
    Redacta secretos y, si trae un intento de instrucción, lo marca como dato (no se obedece).
    Entradas: texto (str) respuesta cruda del remoto.
    Salida: (texto_saneado (str), flags (dict) con 'secretos' y 'inyeccion')."""
    saneado, secretos = redactar_secretos(texto or "")
    inyeccion = es_instruccion_remota(saneado)
    if inyeccion:
        saneado = ("⚠️ (el agente remoto incluyó texto que parece una instrucción; "
                   "se muestra como dato y NO se obedece)\n" + saneado)
    return saneado, {"secretos": secretos, "inyeccion": inyeccion}


def evaluar_respuesta_remota(texto, agente: str = "-", correlacion: str = "-") -> tuple[str, str, str]:
    """Objetivo (guardrail A2A por capas, Corrección 2.D): decidir qué hacer con la respuesta de
    un agente remoto según una POLÍTICA configurable (GUARDRAIL_POLITICA_A2A):
      - BLOCK: respuesta malformada (no texto) o política=block ante inyección → se descarta.
      - SANITIZE (def.): se redactan secretos y se neutraliza la instrucción incrustada (dato).
      - ALLOW: se acepta tal cual (solo si política=allow y no hay inyección ni secreto).
    La separación instrucción/dato es por FLUJO: el coordinador nunca ejecuta esta respuesta,
    solo la etiqueta [Nombre]. Entradas: texto, agente, correlacion (id).
    Salida: (decision (str ALLOW/SANITIZE/BLOCK), texto_final (str), motivo (str))."""
    if not isinstance(texto, str):
        registrar_evento("a2a", BLOCK, agente, correlacion, f"politica={POLITICA_A2A} malformada")
        return BLOCK, "La respuesta del agente llegó malformada y se descartó.", "malformada"

    saneado, flags = sanear_respuesta_remota(texto)
    sospechosa = flags["inyeccion"] or bool(flags["secretos"])

    # La DECISIÓN refleja la ACCIÓN EFECTIVA, no la política configurada:
    #  - sin hallazgos y sin cambios → ALLOW (aunque la política sea SANITIZE).
    #  - política BLOCK ante algo sospechoso → BLOCK (se descarta).
    #  - política ALLOW ante algo sospechoso → ALLOW (el operador asume el riesgo).
    #  - resto (SANITIZE ante algo sospechoso) → SANITIZE (se transforma de verdad).
    if not sospechosa:
        registrar_evento("a2a", ALLOW, agente, correlacion, f"politica={POLITICA_A2A} sin hallazgos")
        return ALLOW, texto, "sin hallazgos"
    if POLITICA_A2A == BLOCK:
        registrar_evento("a2a", BLOCK, agente, correlacion,
                         f"politica={POLITICA_A2A} inyeccion={flags['inyeccion']} secretos={bool(flags['secretos'])}")
        return BLOCK, "La respuesta del agente se bloqueó por contenido sospechoso.", "bloqueada por politica=BLOCK"
    if POLITICA_A2A == ALLOW:
        registrar_evento("a2a", ALLOW, agente, correlacion, f"politica={POLITICA_A2A} riesgo asumido")
        return ALLOW, texto, "entregada sin cambios por politica=ALLOW (riesgo asumido)"
    registrar_evento("a2a", SANITIZE, agente, correlacion,
                     f"politica={POLITICA_A2A} inyeccion={flags['inyeccion']} secretos={flags['secretos']}")
    return SANITIZE, saneado, "saneada"
