# --8<-- encabezado-grupo
# Archivo: src/agente_viajes/herramientas.py
# Objetivo: Herramientas del agente de viajes. Datos simulados: en producción serían APIs reales (Amadeus, Booking...).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1514
# Última modificación: 20261111 1857
# --8<-- fin-encabezado-grupo

"""Herramientas del agente de viajes. Datos simulados: en producción serían APIs reales (Amadeus, Booking...)."""
from langchain_core.tools import tool

VUELOS = {
    ("SCL", "LIM"): [{"aerolinea": "LATAM", "sale": "08:10", "llega": "10:05", "precio_clp": 189990},
                     {"aerolinea": "SKY", "sale": "15:40", "llega": "17:35", "precio_clp": 142990}],
    ("SCL", "BOG"): [{"aerolinea": "Avianca", "sale": "07:30", "llega": "12:15", "precio_clp": 329990},
                     {"aerolinea": "LATAM", "sale": "22:50", "llega": "03:40", "precio_clp": 298990}],
    ("SCL", "EZE"): [{"aerolinea": "JetSMART", "sale": "06:00", "llega": "08:15", "precio_clp": 99990}],
}
HOTELES = {
    "LIM": [{"hotel": "Hotel B", "zona": "Barranco", "estrellas": 5, "noche_clp": 210000},
            {"hotel": "Selina Miraflores", "zona": "Miraflores", "estrellas": 3, "noche_clp": 58000}],
    "BOG": [{"hotel": "Four Seasons Casa Medina", "zona": "Chapinero", "estrellas": 5, "noche_clp": 320000},
            {"hotel": "Hotel 93 Luxury Suites", "zona": "Parque 93", "estrellas": 4, "noche_clp": 95000}],
    "EZE": [{"hotel": "Palacio Duhau", "zona": "Recoleta", "estrellas": 5, "noche_clp": 390000},
            {"hotel": "Hotel Madero", "zona": "Puerto Madero", "estrellas": 4, "noche_clp": 120000}],
}
ACTIVIDADES = {
    "LIM": [{"actividad": "Tour gastronómico en Barranco", "tipo": "gastronomía", "horas": 4, "precio_clp": 45000},
            {"actividad": "City tour Centro Histórico", "tipo": "cultural", "horas": 3, "precio_clp": 28000}],
    "BOG": [{"actividad": "Cerro de Monserrate", "tipo": "naturaleza", "horas": 3, "precio_clp": 32000},
            {"actividad": "Museo del Oro + La Candelaria", "tipo": "cultural", "horas": 4, "precio_clp": 25000}],
    "EZE": [{"actividad": "Show de tango en San Telmo", "tipo": "espectáculo", "horas": 3, "precio_clp": 60000},
            {"actividad": "Tour por Recoleta y Palermo", "tipo": "cultural", "horas": 4, "precio_clp": 38000}],
}


@tool
def buscar_vuelos(origen: str, destino: str, fecha: str) -> list[dict]:
    """Busca vuelos entre dos aeropuertos (códigos IATA, ej. SCL, LIM, BOG, EZE) para una fecha AAAA-MM-DD.
    Devuelve aerolínea, horarios y precio en CLP. Lista vacía si no hay ruta."""
    return [dict(v, origen=origen.upper(), destino=destino.upper(), fecha=fecha) for v in VUELOS.get((origen.upper(), destino.upper()), [])]


@tool
def buscar_hoteles(ciudad: str, noches: int = 1) -> list[dict]:
    """Busca hoteles en una ciudad (código IATA: LIM, BOG, EZE). Devuelve hotel, zona, estrellas, precio por noche y total en CLP."""
    return [dict(h, noches=noches, total_clp=h["noche_clp"] * noches) for h in HOTELES.get(ciudad.upper(), [])]


@tool
def buscar_actividades(ciudad: str) -> list[dict]:
    """Busca actividades y panoramas en una ciudad (código IATA: LIM, BOG, EZE).
    Devuelve actividad, tipo, duración en horas y precio en CLP. Lista vacía si no hay."""
    return list(ACTIVIDADES.get(ciudad.upper(), []))


# El agente de viajes nativo sigue siendo vuelos + hoteles; `buscar_actividades`
# la usa el agente de actividades del swarm (no se agrega aquí para no cambiarlo).
HERRAMIENTAS = [buscar_vuelos, buscar_hoteles]
