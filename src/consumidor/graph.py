# --8<-- encabezado-grupo
# Archivo: src/consumidor/graph.py
# Objetivo: Agente conversacional que CONSUME al agente de viajes por A2A.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1629
# Última modificación: 20261110 1934
# --8<-- fin-encabezado-grupo

"""Agente conversacional que CONSUME al agente de viajes por A2A.

Es un agente ReAct (create_agent, estado `messages`) con dos herramientas
(ver `herramientas.py`): una remota (A2A, agente de viajes) y una local dummy
(`precio_btc`). Así se ve al mismo agente usar una herramienta propia y una
remota en la misma conversación. La memoria por conversación la da el
checkpointer (thread_id).
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from src.consumidor.herramientas import HERRAMIENTAS
from src.consumidor.prompts import SYSTEM_CONSUMIDOR

load_dotenv()

modelo = ChatGoogleGenerativeAI(model=os.environ.get("MODELO", "gemini-3.5-flash-lite"))

# Checkpointer local: conversación de varios turnos por thread_id (en el notebook/demo).
# Servido por `langgraph dev`, el servidor aporta su propia persistencia.
graph = create_agent(
    model=modelo,
    tools=HERRAMIENTAS,
    system_prompt=SYSTEM_CONSUMIDOR,
    name="consumidor",
    checkpointer=InMemorySaver(),
)


def texto(msg) -> str:
    """El contenido de Gemini puede venir como lista de partes; esto lo aplana a texto."""
    c = msg.content
    return c if isinstance(c, str) else " ".join(p.get("text", "") for p in c if isinstance(p, dict))


if __name__ == "__main__":
    # Demo: requiere `langgraph dev` corriendo (agente de viajes) y GOOGLE_API_KEY.
    hilo = {"configurable": {"thread_id": "demo-consumidor-1"}}
    for pregunta in [
        "Hola, ¿a cuánto está el bitcoin?",
        "Busco un vuelo de Santiago a Lima el 2026-11-10",
        "Y un hotel ahí por 2 noches",
    ]:
        r = graph.invoke({"messages": [{"role": "user", "content": pregunta}]}, hilo)
        print(f"\n> {pregunta}\n{texto(r['messages'][-1])}")
