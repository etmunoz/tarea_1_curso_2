<!--encabezado-grupo-->
> **Archivo:** `respuestas/03-montar-proyecto-base-uv.md`  
> **Objetivo:** 03 · Respuesta — Montar el proyecto base A2A con uv + Python 3.13  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1620 · **Última modificación:** 20261110 2147
<!--/encabezado-grupo-->

# 03 · Respuesta — Montar el proyecto base A2A con uv + Python 3.13

Prompt: [`../prompts_ejecutados/03-montar-proyecto-base-uv.md`](../prompts_ejecutados/03-montar-proyecto-base-uv.md)

## Qué se hizo

- Se extrajo el proyecto base (`agente-viajes-a2a.zip`) a la raíz del repo:
  `src/agente_viajes/`, `src/swarm/`, `src/consumidor/`, `bruno/`, `tests/`,
  `AGENTS.md`, `plan.json`, `langgraph.json`.
- Se escribió `pyproject.toml` consolidado (todas las deps de `requirements.txt`)
  con `[tool.uv] package = false`, `.python-version = 3.13` y `.gitignore`
  (ignora `.env`, `.venv/`, `.langgraph_api/`).
- `uv sync` creó `.venv` con Python 3.13 e instaló todo (`uv.lock` versionado).

## Salida de la verificación

```text
$ uv run python -V
Python 3.13.15

$ uv run python -c "from src.agente_viajes.herramientas import buscar_vuelos; print(len(buscar_vuelos.invoke({'origen':'SCL','destino':'LIM','fecha':'2026-11-10'})))"
2

$ uv run langgraph --version
LangGraph CLI, version 0.4.42
```

Los grafos (`agente_viajes`, `swarm`) importan correctamente salvo la instanciación
de Gemini, que pide `GOOGLE_API_KEY` — esperado: la clave va en `.env`.

## Estado

Hecho. Entorno uv + Python 3.13 listo; falta `GOOGLE_API_KEY` para ejecución en vivo.
