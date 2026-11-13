"""Cliente A2A reutilizable para comunicarse con otros agentes."""

import asyncio

import httpx
from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers.proto_helpers import (
    get_artifact_text,
    get_message_text,
    new_text_message,
)
from a2a.types import GetTaskRequest, Role, SendMessageRequest, TaskState
from a2a.utils.constants import TransportProtocol


CLIENTES: dict[str, object] = {}
TARJETAS: dict[str, object] = {}
TIEMPO_ESPERA = 30.0


async def obtener_cliente(url: str):
    """Descarga la ficha A2A una vez y crea un cliente JSON-RPC sin streaming."""
    if url in CLIENTES:
        return CLIENTES[url]

    async with httpx.AsyncClient(timeout=10.0) as cliente_http:
        resolver = A2ACardResolver(cliente_http, url)
        tarjeta = await resolver.get_agent_card()
    TARJETAS[url] = tarjeta

    configuracion = ClientConfig(
        streaming=False,
        httpx_client=httpx.AsyncClient(timeout=10.0),
        supported_protocol_bindings=[TransportProtocol.JSONRPC],
    )
    cliente = await create_client(tarjeta, client_config=configuracion)
    CLIENTES[url] = cliente
    return cliente


def _texto_tarea(tarea) -> str:
    """Une los textos de los artefactos o del mensaje de estado de una tarea."""
    textos = [get_artifact_text(artefacto) for artefacto in tarea.artifacts]
    textos = [texto for texto in textos if texto]
    if textos:
        return "\n".join(textos)
    if tarea.status.HasField("message"):
        return get_message_text(tarea.status.message)
    return "El agente no devolvió texto."


async def preguntar(cliente, texto: str, context_id: str) -> str:
    """Envía un mensaje A2A y devuelve el texto directo o el de su tarea."""
    solicitud = SendMessageRequest(
        message=new_text_message(
            text=texto,
            context_id=context_id,
            role=Role.ROLE_USER,
        )
    )
    async for respuesta in cliente.send_message(solicitud):
        if respuesta.HasField("message"):
            return get_message_text(respuesta.message)
        if not respuesta.HasField("task"):
            continue

        tarea = respuesta.task
        for _ in range(60):
            if tarea.status.state == TaskState.TASK_STATE_COMPLETED:
                return _texto_tarea(tarea)
            await asyncio.sleep(0.5)
            tarea = await cliente.get_task(GetTaskRequest(id=tarea.id))
        return "El agente no terminó la tarea dentro del tiempo esperado."
    return "El agente no devolvió una respuesta."
