"""CrewAI del agente de restaurantes con memoria manual por conversación."""

import asyncio
import inspect
import os
from uuid import uuid4

from crewai import Agent, Crew, LLM, Task
from crewai.agents.parser import AgentAction, AgentFinish
from dotenv import load_dotenv

from src.agente_restaurantes.prompts import HISTORIA, OBJETIVO, ROL
from src.agente_restaurantes.tools import buscar_restaurantes, detalle_restaurante


load_dotenv()
MODELO = os.getenv("MODELO", "gemini-3.5-flash-lite")
LLM_RESTAURANTES = LLM(
    model=f"gemini/{MODELO}",
    api_key=os.getenv("GOOGLE_API_KEY", "clave-no-configurada"),
    timeout=30,
)
HISTORIAL: dict[str, list[str]] = {}


def _crear_crew(
    pregunta: str,
    historial: list[str],
    verbose: bool = False,
    step_callback=None,
) -> Crew:
    """Arma un crew de una tarea con el contexto de la conversación."""
    agente = Agent(
        role=ROL,
        goal=OBJETIVO,
        backstory=HISTORIA,
        tools=[buscar_restaurantes, detalle_restaurante],
        llm=LLM_RESTAURANTES,
        verbose=verbose,
        step_callback=step_callback,
        allow_delegation=False,
    )
    contexto = "\n".join(historial) or "No hay conversaciones anteriores."
    tarea = Task(
        description=(
            f"Pregunta actual del usuario: {pregunta}\n\n"
            f"Conversación anterior:\n{contexto}\n\n"
            "Usa las herramientas cuando necesites datos del catálogo."
        ),
        expected_output="Una respuesta breve en español basada solo en las herramientas.",
        agent=agente,
    )
    return Crew(agents=[agente], tasks=[tarea], verbose=verbose)


async def _ejecutar(crew: Crew):
    """Ejecuta el crew sin bloquear el servidor asíncrono."""
    if hasattr(crew, "kickoff_async"):
        resultado = crew.kickoff_async()
        if inspect.isawaitable(resultado):
            return await resultado
        return resultado
    return await asyncio.to_thread(crew.kickoff)


async def responder(texto: str, context_id: str | None) -> str:
    """Responde y conserva el intercambio en el historial de la conversación."""
    identificador = context_id or str(uuid4())
    historial = HISTORIAL.setdefault(identificador, [])
    crew = _crear_crew(texto, historial)
    try:
        resultado = await _ejecutar(crew)
        respuesta = str(getattr(resultado, "raw", resultado))
        historial.extend([f"Usuario: {texto}", f"Agente: {respuesta}"])
        return respuesta
    except Exception as error:
        detalle = str(error).splitlines()[0] or error.__class__.__name__
        return f"No pude consultar restaurantes: {detalle}"


async def saltos(texto: str) -> None:
    """Ejecuta el crew e imprime los pasos y herramientas utilizadas."""
    herramientas_usadas = 0

    def mostrar_paso(paso) -> None:
        """Muestra cada pensamiento, llamada de herramienta y resultado."""
        nonlocal herramientas_usadas
        if isinstance(paso, AgentAction):
            herramientas_usadas += 1
            print(f"Pensamiento: {paso.thought}")
            print(f"Herramienta: {paso.tool}")
            print(f"Argumentos: {paso.tool_input}")
            if paso.result:
                print(f"Resultado: {paso.result}")
        elif isinstance(paso, AgentFinish):
            print(f"Respuesta: {paso.output}")

    crew = _crear_crew(texto, [], verbose=True, step_callback=mostrar_paso)
    try:
        await _ejecutar(crew)
    except Exception as error:
        detalle = str(error).splitlines()[0] or error.__class__.__name__
        print(f"No pude consultar restaurantes: {detalle}")
    print(f"Total de herramientas usadas: {herramientas_usadas}")


def diagrama() -> str:
    """Devuelve una representación Mermaid de la estructura del crew."""
    return """graph TD
    Tarea[Tarea] --> Agente[Agente de restaurantes]
    Agente --> Buscar[buscar_restaurantes]
    Agente --> Detalle[detalle_restaurante]"""
