"""Herramientas con datos ficticios de restaurantes."""

from crewai.tools import tool


RESTAURANTES = {
    "LIM": [
        {"nombre": "Ceviche Miraflores", "zona": "Miraflores", "tipo": "peruana", "precio_medio_clp": 28000, "horario": "12:30-23:00"},
        {"nombre": "Barranco Verde", "zona": "Barranco", "tipo": "vegetariana", "precio_medio_clp": 21000, "horario": "12:00-22:30"},
        {"nombre": "Anticuchos Central", "zona": "San Isidro", "tipo": "peruana", "precio_medio_clp": 24000, "horario": "13:00-23:30"},
        {"nombre": "Pasta Lima", "zona": "Miraflores", "tipo": "italiana", "precio_medio_clp": 26000, "horario": "12:00-22:00"},
    ],
    "BOG": [
        {"nombre": "Ajiaco La Candelaria", "zona": "La Candelaria", "tipo": "colombiana", "precio_medio_clp": 18000, "horario": "12:00-21:30"},
        {"nombre": "Chapinero Bistró", "zona": "Chapinero", "tipo": "internacional", "precio_medio_clp": 25000, "horario": "12:30-23:00"},
        {"nombre": "Arepas 93", "zona": "Parque 93", "tipo": "colombiana", "precio_medio_clp": 16000, "horario": "11:30-22:00"},
        {"nombre": "Verde Usaquén", "zona": "Usaquén", "tipo": "vegetariana", "precio_medio_clp": 22000, "horario": "12:00-22:30"},
    ],
    "EZE": [
        {"nombre": "Parrilla Palermo", "zona": "Palermo", "tipo": "argentina", "precio_medio_clp": 31000, "horario": "12:30-00:00"},
        {"nombre": "Pasta Recoleta", "zona": "Recoleta", "tipo": "italiana", "precio_medio_clp": 27000, "horario": "12:00-23:00"},
        {"nombre": "Puerto Madero Grill", "zona": "Puerto Madero", "tipo": "argentina", "precio_medio_clp": 36000, "horario": "13:00-00:30"},
        {"nombre": "San Telmo Vegano", "zona": "San Telmo", "tipo": "vegetariana", "precio_medio_clp": 20000, "horario": "12:00-22:00"},
    ],
}


@tool
def buscar_restaurantes(ciudad: str, tipo: str) -> list[dict]:
    """Busca restaurantes ficticios por ciudad y tipo de comida."""
    opciones = RESTAURANTES.get(ciudad.strip().upper(), [])
    if not tipo or tipo.strip().lower() in {"todos", "cualquiera"}:
        return opciones
    return [
        restaurante
        for restaurante in opciones
        if restaurante["tipo"].lower() == tipo.strip().lower()
    ]


@tool
def detalle_restaurante(nombre: str) -> dict | list:
    """Entrega el detalle de un restaurante ficticio por su nombre exacto."""
    nombre_buscado = nombre.strip().casefold()
    for restaurantes in RESTAURANTES.values():
        for restaurante in restaurantes:
            if restaurante["nombre"].casefold() == nombre_buscado:
                return restaurante
    return []
