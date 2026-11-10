# 01 · Crear el agente de Ezequiel (IA Engineer & Data Scientist)

**Fecha:** 2026-11-10
**Objetivo:** armar el agente propio del taller, con la skill real de Ezequiel, sobre el molde del agente de viajes (A2A nativo de LangGraph).

## Prompt

> Crea un agente nuevo que represente lo que sé hacer: **Ezequiel**, especialidad **IA Engineer y Data Scientist**. Cópialo del molde del agente de viajes, en `src/agente_ezequiel/`, con los mismos tres archivos y siguiendo `AGENTS.md`:
>
> 1. `herramientas.py` — dos o tres herramientas con `@tool` de mi especialidad, con datos inventados pero creíbles dentro del archivo. Para IA/Data Science:
>    - `recomendar_tecnica(problema)`: dado un problema de ML/DS (pocos datos, overfitting, desbalance de clases, datos faltantes, texto, series de tiempo, detección de anomalías, alta dimensionalidad) devuelve la técnica recomendada y por qué.
>    - `metricas_recomendadas(tipo_problema)`: dado el tipo de problema devuelve qué métricas mirar.
>    - `elegir_modelo(tipo_de_dato)`: dado el tipo de dato/caso (tabular, texto, imagen, series temporales, generación, recomendación) sugiere un modelo/enfoque de arranque.
>    Si piden algo que no está en los datos, la herramienta lo dice en una línea, nunca lanza error. El emparejado debe tolerar acentos y raíces de palabra (p. ej. "clasificar" → "clasificacion").
>
> 2. `prompts.py` — un `SYSTEM_EZEQUIEL` que diga: eres Ezequiel, IA Engineer y Data Scientist; responde solo sobre eso, en español y corto, usando las herramientas antes de contestar y sin inventar; si no es de tu tema, dilo en una frase; si preguntan quién eres, di nombre y especialidad.
>
> 3. `graph.py` — igual que el de viajes: `create_agent` con el modelo de Gemini, mis herramientas y el `SYSTEM_EZEQUIEL`, `name="agente_ezequiel"`. Estado con `messages` (A2A nativo).
>
> Regístralo en `langgraph.json` como grafo `agente_ezequiel`. Agrega un test de las herramientas que corra sin API key. No levantes el servidor; dime cómo probarlo.

## Verificación pedida

- Las tres herramientas responden con datos del catálogo y rechazan temas ajenos en una línea.
- `langgraph.json` incluye `agente_ezequiel`.
- `uv run pytest tests/test_agente_ezequiel.py` en verde.
