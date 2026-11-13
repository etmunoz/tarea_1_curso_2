"""Fábrica de aplicaciones FastAPI que exponen agentes por A2A."""

from collections.abc import Awaitable, Callable
from typing import AsyncContextManager

from fastapi import FastAPI

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    add_a2a_routes_to_fastapi,
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard

from src.comun.executor import Executor


def crear_app(
    tarjeta: AgentCard,
    responder: Callable[[str, str], str | Awaitable[str]],
    lifespan: Callable[[FastAPI], AsyncContextManager[None]] | None = None,
) -> FastAPI:
    """Devuelve una aplicación FastAPI con el endpoint A2A y su tarjeta."""
    app = FastAPI(lifespan=lifespan)
    manejador = DefaultRequestHandler(
        agent_executor=Executor(responder),
        task_store=InMemoryTaskStore(),
        agent_card=tarjeta,
    )

    add_a2a_routes_to_fastapi(
        app,
        agent_card_routes=create_agent_card_routes(tarjeta),
        jsonrpc_routes=create_jsonrpc_routes(manejador, rpc_url="/"),
    )

    @app.get("/salud")
    @app.get("/health")
    async def salud() -> dict[str, bool]:
        """Confirma que el servidor está en ejecución."""
        return {"ok": True}

    return app
