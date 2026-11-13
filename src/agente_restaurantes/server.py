"""Servidor A2A del agente de restaurantes."""

import os

from dotenv import load_dotenv

from src.agente_restaurantes.crew import responder
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta


load_dotenv()
URL_RESTAURANTES = os.getenv("URL_RESTAURANTES", "http://127.0.0.1:8001")
tarjeta = crear_tarjeta(
    "Agente de restaurantes",
    "Recomienda restaurantes en LIM, BOG y EZE por zona y tipo de comida. No reserva.",
    URL_RESTAURANTES,
    [
        (
            "buscar-restaurantes",
            "Buscar restaurantes",
            "Busca restaurantes por ciudad y tipo de comida.",
            "Busca restaurantes de comida peruana en LIM.",
        ),
        (
            "detalle-restaurante",
            "Ver detalle de restaurante",
            "Muestra zona, tipo, precio medio y horario de un restaurante.",
            "Dame el detalle de Parrilla Palermo.",
        ),
    ],
)
app = crear_app(tarjeta, responder)
