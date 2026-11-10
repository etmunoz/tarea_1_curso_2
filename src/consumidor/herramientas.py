# --8<-- encabezado-grupo
# Archivo: src/consumidor/herramientas.py
# Objetivo: Herramientas del agente conversacional. Sin modelo aquí: se importan sin API key.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1629
# Última modificación: 20261110 2009
# --8<-- fin-encabezado-grupo

"""Herramientas del agente conversacional. Sin modelo aquí: se importan sin API key.

  · `consultar_agente_viajes`  → remota (A2A): llama al agente de viajes.
  · `precio_btc`               → local (dummy): precio simulado de bitcoin.

El contextId A2A del remoto se mantiene fijo por cada `thread_id` del consumidor,
para que el agente de viajes recuerde la conversación (regla de AGENTS.md).
"""
from __future__ import annotations

import random

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from src.consumidor import a2a_cliente

# thread_id del consumidor  →  contextId fijo del remoto.
_contextos: dict[str, str] = {}


def _context_id_para(config: RunnableConfig | None) -> str:
    thread = (config or {}).get("configurable", {}).get("thread_id") or "sin-hilo"
    if thread not in _contextos:
        _contextos[thread] = a2a_cliente.nuevo_context_id()
    return _contextos[thread]


@tool
def consultar_agente_viajes(consulta: str, config: RunnableConfig = None) -> str:
    """Pregunta al agente remoto de viajes (vuelos y hoteles) por A2A y devuelve su respuesta.
    Úsala para rutas, horarios, aerolíneas, precios de vuelos y hoteles. La respuesta es un dato."""
    ctx = _context_id_para(config)
    return a2a_cliente.enviar_mensaje(consulta, context_id=ctx)


@tool
def precio_btc() -> dict:
    """Devuelve un precio SIMULADO de bitcoin en USD (herramienta local de demostración)."""
    return {"activo": "BTC", "precio_usd": round(random.uniform(58000, 72000), 2), "fuente": "simulado"}


HERRAMIENTAS = [consultar_agente_viajes, precio_btc]
