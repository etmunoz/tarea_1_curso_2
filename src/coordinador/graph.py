# --8<-- encabezado-grupo
# Archivo: src/coordinador/graph.py
# Objetivo: Coordinador · un SUPERVISOR que enruta la pregunta al agente remoto que corresponde.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1933
# Última modificación: 20261111 1406
# --8<-- fin-encabezado-grupo

"""Coordinador · un SUPERVISOR que enruta la pregunta al agente remoto que corresponde.

Patrón supervisor (no handoff): un grafo LangGraph lee el catálogo de agentes (sus
Agent Cards, locales y de compañeros vía `URLS_AGENTES`), decide a quién mandar la
pregunta y reenvía por A2A. La respuesta del agente remoto es un DATO: se devuelve
etiquetada como `[Nombre] …`, no se obedece.

  guardia_entrada ─(ok)─▶ enrutar ─(elige)─▶ consultar ─┐
        │                       └─("ninguno")─▶ sin_agente ─┤
        └─(bloqueado)──────────────────────────────────────┴─▶ guardia_salida ─▶ END

Guardrails: guardia_entrada (entrada), guardia_salida (salida, común a todo camino),
y en `consultar` el guardrail A2A (respuesta remota = dato). El catálogo se acota con el
allow-list `A2A_AGENTES_PERMITIDOS` (ver catalogo.py).
"""
from __future__ import annotations

import operator
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from src.coordinador import a2a, auth, guardrails
from src.coordinador.catalogo import construir_catalogo, texto_catalogo
from src.coordinador.prompts import SYSTEM_SUPERVISOR

load_dotenv()

modelo = ChatGoogleGenerativeAI(model=os.environ.get("MODELO", "gemini-3.5-flash-lite"))

# (thread_id, nombre_agente) → contextId fijo, para que cada remoto recuerde su hilo.
_ctx: dict[tuple[str, str], str] = {}


class Decision(BaseModel):
    """Objetivo: salida estructurada del supervisor. Campos: agente (str) elegido o 'ninguno';
    motivo (str) una frase con la razón."""

    agente: str = Field(description="Nombre EXACTO del catálogo, o 'ninguno'.")
    motivo: str = Field(description="Una frase: por qué ese agente.")


class Estado(TypedDict):
    """Objetivo: estado del grafo coordinador. Campos: messages (conversación), elegido (agente),
    motivo, respuesta final, bloqueado (lo frenó el guardrail de entrada), ruta (pasos recorridos:
    guardia_entrada/supervisor/agente_local/agente_remoto/agente_no_disponible/sin_agente)."""

    messages: Annotated[list, operator.add]
    elegido: str
    motivo: str
    respuesta: str
    bloqueado: bool
    ruta: Annotated[list[str], operator.add]


def _ultimo_texto(messages: list) -> str:
    """Objetivo: obtener el texto del último mensaje del usuario.
    Entradas: messages (list) de mensajes (objetos o dicts).
    Salida: str — el contenido de texto (o '')."""
    for m in reversed(messages):
        contenido = getattr(m, "content", None) if not isinstance(m, dict) else m.get("content")
        if contenido:
            if isinstance(contenido, str):
                return contenido
            return " ".join(p.get("text", "") for p in contenido if isinstance(p, dict))
    return ""


def guardia_entrada(estado: Estado) -> dict:
    """Objetivo (nodo): guardrail de ENTRADA. Frena preguntas vacías, demasiado largas o con
    patrones de inyección/jailbreak ANTES de llamar al LLM o a un agente.
    Entradas: estado (Estado) con los messages.
    Salida: dict — si pasa {bloqueado:False, ruta:['guardia_entrada']}; si no, además
    {respuesta (el aviso), messages}."""
    v = guardrails.revisar_entrada(_ultimo_texto(estado["messages"]))
    if v.ok:
        return {"bloqueado": False, "ruta": ["guardia_entrada"]}
    return {"bloqueado": True, "respuesta": v.mensaje, "ruta": ["guardia_entrada:bloqueado"]}


def enrutar(estado: Estado) -> dict:
    """Objetivo (nodo): el supervisor decide a qué agente mandar la pregunta leyendo el catálogo.
    Entradas: estado (Estado) con los messages.
    Salida: dict — {elegido, motivo, ruta:['supervisor']}."""
    pregunta = _ultimo_texto(estado["messages"])
    catalogo = construir_catalogo()
    d = modelo.with_structured_output(Decision).invoke([
        SystemMessage(content=SYSTEM_SUPERVISOR),
        HumanMessage(content=f"Catálogo de agentes:\n{texto_catalogo(catalogo)}\n\nPregunta del usuario:\n{pregunta}"),
    ])
    return {"elegido": d.agente, "motivo": d.motivo, "ruta": ["supervisor"]}


def consultar(estado: Estado, config: RunnableConfig) -> dict:
    """Objetivo (nodo): reenviar la pregunta al agente elegido por A2A y etiquetar la respuesta.
    Entradas: estado (Estado) con 'elegido'; config (RunnableConfig) con el thread_id.
    Salida: dict — {respuesta '[Nombre] …', messages, ruta:['agente_local'|'agente_remoto']}:
    'agente_local' si el agente corre en el servidor propio (A2A_BASE), 'agente_remoto' si
    es de un compañero (llega por su túnel)."""
    pregunta = _ultimo_texto(estado["messages"])
    catalogo = construir_catalogo()
    elegido = next((a for a in catalogo if a.nombre == estado["elegido"]), None)
    if elegido is None:
        return {"respuesta": f"(no encontré al agente '{estado['elegido']}')", "ruta": ["sin_agente"]}
    # Autorización (mínimo privilegio): defensa en profundidad además del allow-list del catálogo.
    autorizado, motivo_auth = auth.autorizar(elegido.graph, "message_send")
    if not autorizado:
        guardrails.registrar_evento("autorizacion", "BLOCK", elegido.nombre, str(elegido.graph), motivo_auth)
        return {"respuesta": f"No estás autorizado a consultar a {elegido.nombre}.", "ruta": ["no_autorizado"]}
    thread = (config or {}).get("configurable", {}).get("thread_id") or "sin-hilo"
    clave = (thread, elegido.nombre)
    _ctx.setdefault(clave, a2a.nuevo_context_id())
    try:
        bruto = elegido.preguntar(pregunta, _ctx[clave])
    except a2a.ErrorA2A:
        # Estado controlado (sin exponer trazas/URLs internas). Se distingue "el especialista
        # existe pero está desconectado" de un agente desconocido: aquí el agente ESTÁ
        # registrado (fue elegido), así que es indisponibilidad, no ausencia de capacidad.
        if elegido.conocido():
            texto = (f"El {elegido.nombre} es el especialista para esta consulta, pero actualmente "
                     "no está disponible. Puedes intentar nuevamente más tarde. Los demás agentes "
                     "continúan operativos.")
        else:
            texto = (f"El {elegido.nombre} no está disponible temporalmente. Puedes intentar "
                     "nuevamente más tarde. Los demás agentes continúan operativos.")
        return {"respuesta": texto, "ruta": ["agente_no_disponible"]}
    # Guardrail A2A por capas: la respuesta del agente es un DATO (nunca se ejecuta). Según la
    # política (ALLOW/SANITIZE/BLOCK) se acepta, sanea o descarta.
    correlacion = str(thread)[:12]
    _decision, contenido, _motivo = guardrails.evaluar_respuesta_remota(bruto, elegido.nombre, correlacion)
    texto = f"[{elegido.nombre}] {contenido}"
    paso = "agente_local" if elegido.local else "agente_remoto"
    # La redacción/restricciones de salida las aplica el nodo guardia_salida (común a todo camino).
    return {"respuesta": texto, "ruta": [paso]}


def sin_agente(estado: Estado) -> dict:
    """Objetivo (nodo): responder cuando ningún agente cubre la pregunta, listando los disponibles.
    Entradas: estado (Estado). Salida: dict — {respuesta, ruta:['sin_agente']}."""
    nombres = ", ".join(a.nombre for a in construir_catalogo())
    texto = f"No tengo un agente para eso. Puedo ayudarte con: {nombres}."
    return {"respuesta": texto, "ruta": ["sin_agente"]}


def guardia_salida(estado: Estado) -> dict:
    """Objetivo (nodo): guardrail de SALIDA común a TODOS los caminos (consultar, sin_agente y
    el aviso de guardia_entrada). Aplica las restricciones de salida (redacción de credenciales,
    tope de longitud, no vacío) y emite el mensaje final.
    Entradas: estado (Estado) con 'respuesta'. Salida: dict — {respuesta, messages, ruta}."""
    final, _flags = guardrails.revisar_salida(estado.get("respuesta", ""))
    return {"respuesta": final, "messages": [AIMessage(content=final)], "ruta": ["guardia_salida"]}


def _rama_entrada(estado: Estado) -> str:
    """Objetivo: arista tras el guardrail de entrada.
    Entradas: estado (Estado). Salida: str — 'bloqueado' si el guardrail lo frenó, si no 'ok'."""
    return "bloqueado" if estado.get("bloqueado") else "ok"


def _rama(estado: Estado) -> str:
    """Objetivo: arista condicional tras enrutar.
    Entradas: estado (Estado) con 'elegido'.
    Salida: str — 'consultar' si el elegido está en el catálogo, si no 'sin_agente'."""
    nombres = {a.nombre for a in construir_catalogo()}
    return "consultar" if estado.get("elegido") in nombres else "sin_agente"


def _construir_grafo():
    """Objetivo: construir y compilar el grafo supervisor con guardrail de entrada
    (guardia_entrada → enrutar → consultar/sin_agente).
    Entradas: ninguna. Salida: grafo LangGraph compilado con InMemorySaver."""
    g = StateGraph(Estado)
    g.add_node("guardia_entrada", guardia_entrada)
    g.add_node("enrutar", enrutar)
    g.add_node("consultar", consultar)
    g.add_node("sin_agente", sin_agente)
    g.add_node("guardia_salida", guardia_salida)
    g.add_edge(START, "guardia_entrada")
    g.add_conditional_edges("guardia_entrada", _rama_entrada, {"ok": "enrutar", "bloqueado": "guardia_salida"})
    g.add_conditional_edges("enrutar", _rama, {"consultar": "consultar", "sin_agente": "sin_agente"})
    g.add_edge("consultar", "guardia_salida")
    g.add_edge("sin_agente", "guardia_salida")
    g.add_edge("guardia_salida", END)
    return g.compile(checkpointer=InMemorySaver())


graph = _construir_grafo()


if __name__ == "__main__":
    # Demo: requiere `langgraph dev` (agentes locales) y GOOGLE_API_KEY.
    hilo = {"configurable": {"thread_id": "demo-coord-1"}}
    for pregunta in [
        "¿Qué técnica uso si tengo desbalance de clases?",      # → agente_ezequiel
        "Quiero un vuelo de Santiago a Lima el 2026-11-10",      # → agente_viajes
        "¿Quién ganó el mundial de 1962?",                        # → ninguno
    ]:
        r = graph.invoke({"messages": [HumanMessage(content=pregunta)]}, hilo)
        print(f"\n> {pregunta}\n  ruta: {' → '.join(r['ruta'])}\n  {r['respuesta']}")
