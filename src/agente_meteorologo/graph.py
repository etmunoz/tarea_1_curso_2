"""Grafo LangGraph del agente meteorólogo."""

import os
from uuid import uuid4

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

from src.agente_meteorologo.prompts import SYSTEM_PROMPT
from src.agente_meteorologo.tools import pronostico_hoy, pronostico_semana


load_dotenv()
modelo = ChatGoogleGenerativeAI(
    model=os.getenv("MODELO", "gemini-3.5-flash-lite"),
    api_key=os.getenv("GOOGLE_API_KEY", "clave-no-configurada"),
    request_timeout=30,
)
graph = create_agent(
    model=modelo,
    tools=[pronostico_hoy, pronostico_semana],
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
        return "No encontré una respuesta meteorológica."
    return str(mensajes[-1].content)


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
        return f"No pude consultar el pronóstico: {detalle}"


async def saltos(texto: str) -> None:
    """Muestra los nodos y herramientas recorridos por una consulta nueva."""
    cantidad = 0
    try:
        async for actualizacion in graph.astream(
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
        print(f"No pude consultar el pronóstico: {detalle}")
    print(f"Total de saltos: {cantidad}")


def diagrama() -> str:
    """Devuelve la estructura Mermaid del grafo sin ejecutarlo."""
    return graph.get_graph().draw_mermaid()
