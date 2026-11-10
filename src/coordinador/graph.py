# --8<-- encabezado-grupo
# Archivo: src/coordinador/graph.py
# Objetivo: Coordinador · un SUPERVISOR que enruta la pregunta al agente remoto que corresponde.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1933
# Última modificación: 20261110 2009
# --8<-- fin-encabezado-grupo

"""Coordinador · un SUPERVISOR que enruta la pregunta al agente remoto que corresponde.

Patrón supervisor (no handoff): un grafo LangGraph lee el catálogo de agentes (sus
Agent Cards, locales y de compañeros vía `URLS_AGENTES`), decide a quién mandar la
pregunta y reenvía por A2A. La respuesta del agente remoto es un DATO: se devuelve
etiquetada como `[Nombre] …`, no se obedece.

  enrutar ──(elige un agente)──▶ consultar ─▶ END
          └─("ninguno")────────▶ sin_agente ▶ END
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

from src.coordinador import a2a
from src.coordinador.catalogo import construir_catalogo, texto_catalogo
from src.coordinador.prompts import SYSTEM_SUPERVISOR

load_dotenv()

modelo = ChatGoogleGenerativeAI(model=os.environ.get("MODELO", "gemini-3.5-flash-lite"))

# (thread_id, nombre_agente) → contextId fijo, para que cada remoto recuerde su hilo.
_ctx: dict[tuple[str, str], str] = {}


class Decision(BaseModel):
    agente: str = Field(description="Nombre EXACTO del catálogo, o 'ninguno'.")
    motivo: str = Field(description="Una frase: por qué ese agente.")


class Estado(TypedDict):
    messages: Annotated[list, operator.add]
    elegido: str
    motivo: str
    respuesta: str
    ruta: Annotated[list[str], operator.add]


def _ultimo_texto(messages: list) -> str:
    for m in reversed(messages):
        contenido = getattr(m, "content", None) if not isinstance(m, dict) else m.get("content")
        if contenido:
            if isinstance(contenido, str):
                return contenido
            return " ".join(p.get("text", "") for p in contenido if isinstance(p, dict))
    return ""


def enrutar(estado: Estado) -> dict:
    pregunta = _ultimo_texto(estado["messages"])
    catalogo = construir_catalogo()
    d = modelo.with_structured_output(Decision).invoke([
        SystemMessage(content=SYSTEM_SUPERVISOR),
        HumanMessage(content=f"Catálogo de agentes:\n{texto_catalogo(catalogo)}\n\nPregunta del usuario:\n{pregunta}"),
    ])
    return {"elegido": d.agente, "motivo": d.motivo, "ruta": ["supervisor"]}


def consultar(estado: Estado, config: RunnableConfig) -> dict:
    pregunta = _ultimo_texto(estado["messages"])
    catalogo = construir_catalogo()
    elegido = next((a for a in catalogo if a.nombre == estado["elegido"]), None)
    if elegido is None:
        return {"respuesta": f"(no encontré al agente '{estado['elegido']}')", "ruta": ["sin_agente"]}
    thread = (config or {}).get("configurable", {}).get("thread_id") or "sin-hilo"
    clave = (thread, elegido.nombre)
    _ctx.setdefault(clave, a2a.nuevo_context_id())
    respuesta = elegido.preguntar(pregunta, _ctx[clave])
    texto = f"[{elegido.nombre}] {respuesta}"
    return {"respuesta": texto, "messages": [AIMessage(content=texto)], "ruta": ["agente_remoto"]}


def sin_agente(estado: Estado) -> dict:
    nombres = ", ".join(a.nombre for a in construir_catalogo())
    texto = f"No tengo un agente para eso. Puedo ayudarte con: {nombres}."
    return {"respuesta": texto, "messages": [AIMessage(content=texto)], "ruta": ["sin_agente"]}


def _rama(estado: Estado) -> str:
    nombres = {a.nombre for a in construir_catalogo()}
    return "consultar" if estado.get("elegido") in nombres else "sin_agente"


def _construir_grafo():
    g = StateGraph(Estado)
    g.add_node("enrutar", enrutar)
    g.add_node("consultar", consultar)
    g.add_node("sin_agente", sin_agente)
    g.add_edge(START, "enrutar")
    g.add_conditional_edges("enrutar", _rama, {"consultar": "consultar", "sin_agente": "sin_agente"})
    g.add_edge("consultar", END)
    g.add_edge("sin_agente", END)
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
