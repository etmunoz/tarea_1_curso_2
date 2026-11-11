# --8<-- encabezado-grupo
# Archivo: src/agente_cocina/herramientas.py
# Objetivo: Herramientas del agente de cocina chilena (recetas + costeo desde SQLite).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2013
# Última modificación: 20261111 2016
# --8<-- fin-encabezado-grupo

"""Herramientas del agente de cocina chilena (recetas + costeo desde SQLite)."""
from __future__ import annotations

from langchain_core.tools import tool

from src.agente_cocina import bd_recetas


@tool
def listar_recetas() -> list[dict]:
    """Lista las recetas chilenas disponibles (nombre, porciones base y descripción)."""
    return bd_recetas.listar_recetas()


@tool
def ver_receta(nombre: str) -> dict:
    """Muestra una receta: sus ingredientes con cantidad y unidad. Acepta nombre parcial."""
    return bd_recetas.ver_receta(nombre)


@tool
def costear_receta(nombre: str, personas: int = 4) -> dict:
    """Calcula cuánto cuesta producir una receta para `personas` (por defecto 4).
    Devuelve el costo por ingrediente (cantidad escalada × precio por su unidad, sin
    conversión), el costo total y el costo por persona, todo en CLP."""
    return bd_recetas.costear_receta(nombre, personas=personas)


HERRAMIENTAS = [listar_recetas, ver_receta, costear_receta]
