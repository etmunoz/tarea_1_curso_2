"""Servidor A2A del agente de viajes."""

import os

from dotenv import load_dotenv

from src.agente_viajes.graph import responder
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta


load_dotenv()
URL_VIAJES = os.getenv("URL_VIAJES", "http://127.0.0.1:8080")
tarjeta = crear_tarjeta(
    "Agente de viajes",
    "Busca vuelos y hoteles entre SCL, LIM, BOG y EZE con precios en CLP. No reserva ni cobra.",
    URL_VIAJES,
    [
        (
            "buscar-vuelos",
            "Buscar vuelos",
            "Busca vuelos ficticios entre SCL, LIM, BOG y EZE.",
            "Busca un vuelo de SCL a LIM para el 15 de diciembre.",
        ),
        (
            "buscar-hoteles",
            "Buscar hoteles",
            "Busca hoteles ficticios en las ciudades disponibles.",
            "Busca hoteles en Lima para 3 noches.",
        ),
    ],
)
app = crear_app(tarjeta, responder)
