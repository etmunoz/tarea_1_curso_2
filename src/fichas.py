# --8<-- encabezado-grupo
# Archivo: src/fichas.py
# Objetivo: Fichas (Agent Card) de los agentes locales: nombre y descripción.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1952
# Última modificación: 20261111 2049
# --8<-- fin-encabezado-grupo

"""Fichas (Agent Card) de los agentes locales: nombre y descripción.

Con A2A nativo de `langgraph dev`, la tarjeta la publica el servidor a partir del
`name` y la `description` del assistant. Aquí se definen esos textos (qué sé / qué no
hago) y `tools/configurar_fichas.py` los aplica con `PATCH /assistants/<id>`.
"""
from __future__ import annotations

FICHAS: dict[str, dict[str, str]] = {
    "agente_ezequiel": {
        "name": "Agente de Ezequiel",
        "description": (
            "Ingeniero de IA y Data Scientist: recomienda qué técnica de machine learning usar "
            "para un problema, qué métricas mirar y qué modelo elegir según el tipo de dato. "
            "No programa por ti, no entrena modelos reales y no responde temas fuera de IA/Data Science."
        ),
    },
    "agente_tomas": {
        "name": "Agente de Tomás",
        "description": (
            "Maestro Reiki: explica los cinco principios (Gokai), las posiciones de manos para "
            "autotratamiento, los símbolos y los niveles de la práctica. Es bienestar complementario: "
            "no da consejo médico ni diagnósticos; para temas de salud deriva a un profesional."
        ),
    },
    "agente_viajes": {
        "name": "Agente de viajes",
        "description": (
            "Busca vuelos y hoteles (SCL, LIM, BOG, EZE) con precios en CLP. No gestiona pagos ni seguros."
        ),
    },
    "agente_cocina": {
        "name": "Agente de cocina chilena",
        "description": (
            "Conoce recetas chilenas clásicas y calcula cuánto cuesta producir una receta "
            "(costo por ingrediente, total y por persona, en CLP). No responde temas fuera de cocina."
        ),
    },
}
