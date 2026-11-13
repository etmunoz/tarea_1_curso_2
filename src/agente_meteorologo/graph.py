# --8<-- encabezado-grupo
# Archivo: src/agente_meteorologo/graph.py
# Objetivo: Agente meteorólogo (réplica local del agente de Gustavo Reyes), A2A nativo.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261113 1130
# Última modificación: 20261113 1130
# --8<-- fin-encabezado-grupo

"""Agente meteorólogo · réplica local del agente de Gustavo Reyes, expuesto por A2A nativo."""
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from src.agente_meteorologo.herramientas import HERRAMIENTAS
from src.agente_meteorologo.prompts import SYSTEM_METEOROLOGO

load_dotenv()

modelo = ChatGoogleGenerativeAI(model=os.environ.get("MODELO", "gemini-3.5-flash-lite"))

graph = create_agent(
    model=modelo,
    tools=HERRAMIENTAS,
    system_prompt=SYSTEM_METEOROLOGO,
    name="agente_meteorologo",
)
