# --8<-- encabezado-grupo
# Archivo: src/agente_cocina/graph.py
# Objetivo: Agente de cocina chilena · expuesto por A2A NATIVO (molde de viajes/Ezequiel).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2013
# Última modificación: 20261111 1205
# --8<-- fin-encabezado-grupo

"""Agente de cocina chilena · expuesto por A2A NATIVO (molde de viajes/Ezequiel)."""
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from src.agente_cocina.herramientas import HERRAMIENTAS
from src.agente_cocina.prompts import SYSTEM_COCINA

load_dotenv()

modelo = ChatGoogleGenerativeAI(model=os.environ.get("MODELO", "gemini-3.5-flash-lite"))

graph = create_agent(
    model=modelo,
    tools=HERRAMIENTAS,
    system_prompt=SYSTEM_COCINA,
    name="agente_cocina",
)
