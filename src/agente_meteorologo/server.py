"""Servidor A2A del agente meteorólogo."""

import os

from dotenv import load_dotenv

from src.agente_meteorologo.graph import responder
from src.comun.servidor import crear_app
from src.comun.tarjeta import crear_tarjeta


load_dotenv()
URL_NOMBRE = os.getenv("URL_NOMBRE", "http://127.0.0.1:8003")
tarjeta = crear_tarjeta(
    "agente_meteorologo",
    "Entrego pronosticos ficticios del clima de hoy y de los proximos siete doas para Santiago, Concepcion y Valdivia, con temperaturas y condiciones meteorologicas. No respondo preguntas fuera de la Meteorologia ni pronosticos para otras ciudades, o para plazos superiores a siete dias.",
    URL_NOMBRE,
    [
        (
            "pronostico-hoy",
            "Clima de hoy",
            "Informa el pronostico del clima para hoy solo en Santiago, Concepcion o Valdivia.",
            "Dame el pronostico del tiempo para hoy en Valdivia.",
        ),
        (
            "pronostico-semana",
            "Clima semanal",
            "Informa el pronostico de los proximos siete dias solo para Santiago, Concepcion o Valdivia.",
            "Dame el pronostico del tiempo para la semana en Santiago.",
        ),
    ],
)
app = crear_app(tarjeta, responder)
