# --8<-- encabezado-grupo
# Archivo: src/agente_tomas/graph.py
# Objetivo: Agente de Tomás (Maestro Reiki) · expuesto por A2A NATIVO.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1952
# Última modificación: 20261111 1738
# --8<-- fin-encabezado-grupo

"""Agente de Tomás (Maestro Reiki) · expuesto por A2A NATIVO.

Mismo molde que el agente de viajes/Ezequiel: no hay código de servidor aquí.
`langgraph dev` lee `langgraph.json`, levanta este grafo y publica la Agent Card y
`POST /a2a/agente_tomas`. El estado trae `messages` (requisito de A2A nativo).

Pensado para correr en el **segundo computador** (Windows) mientras Ezequiel corre
en el MacOS; el coordinador los suma a ambos. Ver `guia_ezequiel_tomas.md`.
"""
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from src.agente_tomas.herramientas import HERRAMIENTAS
from src.agente_tomas.prompts import SYSTEM_TOMAS

load_dotenv()

modelo = ChatGoogleGenerativeAI(model=os.environ.get("MODELO", "gemini-3.5-flash-lite"))

graph = create_agent(
    model=modelo,
    tools=HERRAMIENTAS,
    system_prompt=SYSTEM_TOMAS,
    name="agente_tomas",
)
