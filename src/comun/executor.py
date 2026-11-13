"""Ejecutor A2A reutilizable para los agentes del proyecto."""

from collections.abc import Awaitable, Callable
from inspect import isawaitable
from uuid import uuid4

from a2a.helpers.proto_helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue


class Executor(AgentExecutor):
    """Conecta los mensajes A2A con la función ``responder`` de un agente."""

    def __init__(
        self, responder: Callable[[str, str], str | Awaitable[str]]
    ) -> None:
        """Guarda la función que implementa el contrato común de los agentes."""
        self._responder = responder

    async def execute(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Procesa un mensaje y publica la respuesta textual del agente."""
        texto = context.get_user_input()
        context_id = context.context_id or str(uuid4())

        try:
            respuesta = self._responder(texto, context_id)
            if isawaitable(respuesta):
                respuesta = await respuesta
        except Exception as error:
            detalle = str(error).splitlines()[0] or error.__class__.__name__
            respuesta = f"El agente no pudo responder: {detalle}"

        await event_queue.enqueue_event(
            new_text_message(
                text=respuesta,
                context_id=context_id,
                task_id=context.task_id,
            )
        )

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Informa que los agentes de esta base todavía no admiten cancelación."""
        context_id = context.context_id or str(uuid4())
        await event_queue.enqueue_event(
            new_text_message(
                text="La cancelación no está soportada por este agente.",
                context_id=context_id,
                task_id=context.task_id,
            )
        )
