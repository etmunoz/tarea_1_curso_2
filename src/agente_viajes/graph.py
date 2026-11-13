"""Grafo LangGraph del agente de viajes."""

import os
from uuid import uuid4

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

from src.agente_viajes.prompts import SYSTEM_PROMPT
from src.agente_viajes.tools import buscar_hoteles, buscar_vuelos


load_dotenv()
modelo = ChatGoogleGenerativeAI(
    model=os.getenv("MODELO", "gemini-3.5-flash-lite"),
    request_timeout=30,
    api_key=os.getenv("GOOGLE_API_KEY", "clave-no-configurada"),
)
graph = create_agent(
    model=modelo,
    tools=[buscar_vuelos, buscar_hoteles],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=MemorySaver(),
)


def _configuracion(context_id: str | None) -> dict:
    """Prepara el identificador de memoria de la conversación."""
    return {"configurable": {"thread_id": context_id or str(uuid4())}}


def _texto_final(resultado: dict) -> str:
    """Extrae el contenido de la última respuesta del agente."""
    mensajes = resultado.get("messages", [])
    if not mensajes:
        return "No encontré una respuesta de viajes."
    contenido = mensajes[-1].content
    if isinstance(contenido, str):
        return contenido
    return str(contenido)


async def responder(texto: str, context_id: str | None) -> str:
    """Consulta el grafo y conserva la memoria del identificador indicado."""
    try:
        resultado = await graph.ainvoke(
            {"messages": [{"role": "user", "content": texto}]},
            config=_configuracion(context_id),
        )
        return _texto_final(resultado)
    except Exception as error:
        detalle = str(error).splitlines()[0] or error.__class__.__name__
        return f"No pude consultar viajes: {detalle}"


def saltos(texto: str) -> None:
    """Muestra los nodos y herramientas recorridos por una consulta nueva."""
    cantidad = 0
    try:
        for actualizacion in graph.stream(
            {"messages": [{"role": "user", "content": texto}]},
            config=_configuracion(None),
            stream_mode="updates",
        ):
            for nodo, estado in actualizacion.items():
                cantidad += 1
                print(f"Salto {cantidad}: nodo {nodo}")
                for mensaje in estado.get("messages", []):
                    for llamada in getattr(mensaje, "tool_calls", []):
                        print(f"  Herramienta: {llamada['name']}")
                    if (
                        isinstance(mensaje, AIMessage)
                        and not mensaje.tool_calls
                        and mensaje.content
                    ):
                        print(f"  Respuesta: {mensaje.content}")
    except Exception as error:
        detalle = str(error).splitlines()[0] or error.__class__.__name__
        print(f"No pude consultar viajes: {detalle}")
    print(f"Total de saltos: {cantidad}")


def diagrama() -> str:
    """Devuelve la estructura Mermaid del grafo sin ejecutarlo."""
    return graph.get_graph().draw_mermaid()
