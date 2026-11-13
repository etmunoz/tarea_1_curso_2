# --8<-- encabezado-grupo
# Archivo: src/agente_meteorologo/herramientas.py
# Objetivo: Herramientas del meteorólogo: pronóstico ficticio (Santiago, Concepción, Valdivia).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261113 1130
# Última modificación: 20261113 1130
# --8<-- fin-encabezado-grupo

"""Herramientas con pronósticos meteorológicos ficticios de Chile."""

from langchain_core.tools import tool


PRONOSTICO_HOY = {
    "santiago": {
        "temperatura_minima_celsius": 10,
        "temperatura_maxima_celsius": 27,
        "pronostico_hoy": "Nubosidad parcial al amanecer, despejado al mediodía y nublado con lluvia en la noche.",
    },
    "concepción": {
        "temperatura_minima_celsius": 8,
        "temperatura_maxima_celsius": 18,
        "pronostico_hoy": "Nublado al amanecer, lloviznas durante la mañana y lluvia débil en la noche.",
    },
    "valdivia": {
        "temperatura_minima_celsius": 7,
        "temperatura_maxima_celsius": 16,
        "pronostico_hoy": "Lluvia intermitente al amanecer, nublado durante la tarde y chubascos en la noche.",
    },
}

PRONOSTICO_SEMANA = {
    "santiago": [
        {"dia": "Día 1", "min_c": 10, "max_c": 27, "pronostico": "Nubosidad parcial y despejado."},
        {"dia": "Día 2", "min_c": 11, "max_c": 28, "pronostico": "Despejado y cálido."},
        {"dia": "Día 3", "min_c": 12, "max_c": 25, "pronostico": "Nublado parcial."},
        {"dia": "Día 4", "min_c": 9, "max_c": 21, "pronostico": "Nublado con lluvia débil nocturna."},
        {"dia": "Día 5", "min_c": 8, "max_c": 20, "pronostico": "Nublado y fresco."},
        {"dia": "Día 6", "min_c": 9, "max_c": 23, "pronostico": "Nubosidad parcial."},
        {"dia": "Día 7", "min_c": 10, "max_c": 25, "pronostico": "Despejado durante la tarde."},
    ],
    "concepción": [
        {"dia": "Día 1", "min_c": 8, "max_c": 18, "pronostico": "Nublado con lloviznas."},
        {"dia": "Día 2", "min_c": 7, "max_c": 17, "pronostico": "Lluvia débil en la mañana."},
        {"dia": "Día 3", "min_c": 8, "max_c": 19, "pronostico": "Nublado parcial."},
        {"dia": "Día 4", "min_c": 9, "max_c": 20, "pronostico": "Chubascos aislados."},
        {"dia": "Día 5", "min_c": 8, "max_c": 18, "pronostico": "Nublado durante el día."},
        {"dia": "Día 6", "min_c": 7, "max_c": 17, "pronostico": "Lluvia intermitente."},
        {"dia": "Día 7", "min_c": 8, "max_c": 19, "pronostico": "Nubosidad parcial en la tarde."},
    ],
    "valdivia": [
        {"dia": "Día 1", "min_c": 7, "max_c": 16, "pronostico": "Lluvia intermitente."},
        {"dia": "Día 2", "min_c": 6, "max_c": 15, "pronostico": "Nublado con chubascos."},
        {"dia": "Día 3", "min_c": 7, "max_c": 17, "pronostico": "Lluvia débil en la mañana."},
        {"dia": "Día 4", "min_c": 8, "max_c": 18, "pronostico": "Nublado parcial."},
        {"dia": "Día 5", "min_c": 7, "max_c": 16, "pronostico": "Chubascos durante la tarde."},
        {"dia": "Día 6", "min_c": 6, "max_c": 15, "pronostico": "Lluvia continua."},
        {"dia": "Día 7", "min_c": 7, "max_c": 17, "pronostico": "Nublado con claros ocasionales."},
    ],
}


CIUDADES = {"concepcion": "concepción"}


def _normalizar_ciudad(ciudad: str) -> str:
    """Normaliza nombres de ciudades para buscar los datos disponibles."""
    nombre = ciudad.strip().lower()
    return CIUDADES.get(nombre, nombre)


@tool
def pronostico_hoy(ciudad: str) -> dict | str:
    """Entrega el pronóstico ficticio de hoy para Santiago, Concepción o Valdivia."""
    pronostico = PRONOSTICO_HOY.get(_normalizar_ciudad(ciudad))
    if pronostico is None:
        return f"No hay pronóstico disponible para {ciudad}."
    return pronostico


@tool
def pronostico_semana(ciudad: str) -> list[dict] | str:
    """Entrega el pronóstico ficticio de los próximos siete días para una ciudad."""
    pronostico = PRONOSTICO_SEMANA.get(_normalizar_ciudad(ciudad))
    if pronostico is None:
        return f"No hay pronóstico semanal disponible para {ciudad}."
    return pronostico


HERRAMIENTAS = [pronostico_hoy, pronostico_semana]
