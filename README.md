<!--encabezado-grupo-->
> **Archivo:** `README.md`  
> **Objetivo:** tarea_1_curso_2 · Taller A2A  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1450 · **Última modificación:** 20261110 2009
<!--/encabezado-grupo-->

# tarea_1_curso_2 · Taller A2A

Proyecto del **Taller · tu skill es un agente y habla por A2A** (Curso 2 · Sesión 1).
Base: un agente de viajes (LangGraph) expuesto por **A2A de forma nativa** con el
servidor de LangGraph, un **swarm** (vuelos + hoteles) y un **agente conversacional**
pendiente de construir. Entorno con **uv + Python 3.13**.

- Material del taller (10 páginas, lectura): [`taller-a2a/`](taller-a2a/index.md)
- Guía del proyecto base original: [`README_proyecto_base.md`](README_proyecto_base.md)
- Reglas de arquitectura y flujo de trabajo: [`AGENTS.md`](AGENTS.md)

## Puesta en marcha

```bash
uv sync                       # crea .venv con Python 3.13 e instala todo
cp .env.example .env          # pega tu GOOGLE_API_KEY (Gemini)
uv run langgraph dev          # levanta el agente de viajes en http://127.0.0.1:2024
```

> Sin `GOOGLE_API_KEY` el entorno se instala igual, pero los grafos no arrancan:
> el agente se construye con Gemini al importar. La clave va **solo** en `.env`
> (ignorado por git); nunca en el código ni en `.env.example`.

## Comandos útiles (con uv)

```bash
# Verificar las herramientas (no requiere API key)
uv run python -c "from src.agente_viajes.herramientas import buscar_vuelos; print(buscar_vuelos.invoke({'origen':'SCL','destino':'LIM','fecha':'2026-11-10'}))"

# Demo del swarm (vuelos ↔ hoteles en un mismo hilo) — requiere API key
uv run python -m src.swarm.graph

# Pruebas del A2A del agente de viajes (con `uv run langgraph dev` corriendo en otra terminal)
uv run pytest tests/test_a2a_viajes.py
```

Obtener el `assistant_id`, la Agent Card y mandar un `message/send` por A2A: ver los
`curl` en [`README_proyecto_base.md`](README_proyecto_base.md) o la colección
[`bruno/`](bruno/) (entorno `local`).

## Estructura

```
src/agente_viajes/   graph.py · herramientas.py · prompts.py   (A2A nativo · hecho)
src/swarm/           graph.py · prompts.py                     (vuelos+hoteles · hecho)
src/consumidor/      README.md                                 (agente conversacional · por construir)
bruno/               colección para probar tarjeta y message/send
tests/               test_a2a_viajes.py
plan.json            grupos y tareas (viajes · agente-conversacional · swarm)
langgraph.json       grafos que publica `langgraph dev`
taller-a2a/          las 10 páginas del taller, en Markdown (referencia)
```

## Qué sigue (según `plan.json`)

1. **Agente conversacional** (`src/consumidor/`): consume al de viajes por A2A; se
   construye con OpenCode (`@spec` crea tareas, `@implementador` las ejecuta) — ver
   sección 2 de `README_proyecto_base.md`.
2. **Swarm · actividades:** agregar un tercer agente al swarm (tareas `s01…s05`).
3. **Tu propio agente** (lo que pide el taller): tu skill real, su ficha, su túnel.

## Nota

Material de curso para uso personal/educativo. Pertenece a sus autores.
