"""Herramientas con datos ficticios de vuelos y hoteles."""

from langchain_core.tools import tool


VUELOS = {
    ("SCL", "LIM"): [
        {"aerolinea": "LATAM", "horario": "08:15", "precio_clp": 185000},
        {"aerolinea": "SKY Airline", "horario": "14:40", "precio_clp": 149000},
    ],
    ("SCL", "BOG"): [
        {"aerolinea": "Avianca", "horario": "07:20", "precio_clp": 312000},
        {"aerolinea": "LATAM", "horario": "22:10", "precio_clp": 335000},
    ],
    ("SCL", "EZE"): [
        {"aerolinea": "JetSMART", "horario": "06:50", "precio_clp": 128000},
        {"aerolinea": "Aerolineas Argentinas", "horario": "16:30", "precio_clp": 156000},
    ],
    ("LIM", "SCL"): [
        {"aerolinea": "LATAM", "horario": "09:30", "precio_clp": 192000},
        {"aerolinea": "SKY Airline", "horario": "18:05", "precio_clp": 158000},
    ],
    ("LIM", "BOG"): [
        {"aerolinea": "Avianca", "horario": "10:10", "precio_clp": 221000},
        {"aerolinea": "LATAM", "horario": "19:45", "precio_clp": 247000},
    ],
    ("LIM", "EZE"): [
        {"aerolinea": "LATAM", "horario": "11:25", "precio_clp": 298000},
        {"aerolinea": "JetSMART", "horario": "21:00", "precio_clp": 264000},
    ],
    ("BOG", "SCL"): [
        {"aerolinea": "Avianca", "horario": "08:40", "precio_clp": 325000},
        {"aerolinea": "LATAM", "horario": "15:15", "precio_clp": 348000},
    ],
    ("BOG", "LIM"): [
        {"aerolinea": "Avianca", "horario": "07:10", "precio_clp": 214000},
        {"aerolinea": "LATAM", "horario": "17:55", "precio_clp": 239000},
    ],
    ("BOG", "EZE"): [
        {"aerolinea": "Avianca", "horario": "06:35", "precio_clp": 341000},
        {"aerolinea": "LATAM", "horario": "20:20", "precio_clp": 369000},
    ],
    ("EZE", "SCL"): [
        {"aerolinea": "JetSMART", "horario": "09:00", "precio_clp": 135000},
        {"aerolinea": "LATAM", "horario": "18:20", "precio_clp": 171000},
    ],
    ("EZE", "LIM"): [
        {"aerolinea": "LATAM", "horario": "08:25", "precio_clp": 306000},
        {"aerolinea": "Aerolineas Argentinas", "horario": "19:10", "precio_clp": 279000},
    ],
    ("EZE", "BOG"): [
        {"aerolinea": "Avianca", "horario": "07:45", "precio_clp": 352000},
        {"aerolinea": "LATAM", "horario": "16:50", "precio_clp": 381000},
    ],
}

HOTELES = {
    "santiago": [
        {"nombre": "Hotel Lastarria", "precio_noche_clp": 118000},
        {"nombre": "Casa Providencia", "precio_noche_clp": 84000},
    ],
    "lima": [
        {"nombre": "Miraflores Suites", "precio_noche_clp": 92000},
        {"nombre": "Casa Barranco", "precio_noche_clp": 76000},
    ],
    "bogotá": [
        {"nombre": "Hotel Chapinero", "precio_noche_clp": 71000},
        {"nombre": "Suites Parque 93", "precio_noche_clp": 98000},
    ],
    "buenos aires": [
        {"nombre": "Palermo Central", "precio_noche_clp": 87000},
        {"nombre": "Recoleta Apart", "precio_noche_clp": 109000},
    ],
}


@tool
def buscar_vuelos(origen: str, destino: str, fecha: str) -> list[dict]:
    """Busca vuelos ficticios entre dos aeropuertos para una fecha indicada."""
    del fecha
    return VUELOS.get((origen.upper(), destino.upper()), [])


@tool
def buscar_hoteles(ciudad: str, noches: int) -> list[dict]:
    """Busca hoteles ficticios en una ciudad para la cantidad de noches indicada."""
    del noches
    return HOTELES.get(ciudad.strip().lower(), [])
