"""Servidor A2A del coordinador."""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

from src.coordinador.graph import responder
from src.coordinador.catalogo import descubrir
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta


load_dotenv()
URL_COORDINADOR = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8002")


@asynccontextmanager
async def ciclo_vida(app):
    """Descubre los agentes disponibles al iniciar el servidor."""
    agentes = await descubrir()
    print(f"Supervisor con {len(agentes)} agentes")
    yield


tarjeta = crear_tarjeta(
    "Coordinador",
    "Delega consultas de viajes al agente de viajes mediante A2A.",
    URL_COORDINADOR,
    [
        (
            "consultar-viajes",
            "Consultar viajes",
            "Envía una consulta al agente de viajes y repite su respuesta.",
            "Busca vuelos de LIM a SCL para el 15 de diciembre.",
        ),
        (
            "continuar-conversacion",
            "Continuar conversación",
            "Mantiene el identificador de contexto al delegar a viajes.",
            "Muéstrame la alternativa más económica de las opciones anteriores.",
        ),
    ],
)
app = crear_app(tarjeta, responder, lifespan=ciclo_vida)
