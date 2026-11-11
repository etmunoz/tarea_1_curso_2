<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/03-montar-proyecto-base-uv.md`  
> **Objetivo:** 03 · Montar el proyecto base A2A con uv + Python 3.13  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1620 · **Última modificación:** 20261111 1210
<!--/encabezado-grupo-->

# 03 · Montar el proyecto base A2A con uv + Python 3.13

**Fecha:** 2026-11-10
**Objetivo:** dejar listo en `tarea_1_curso_2` el proyecto base del taller (agente
de viajes expuesto por A2A nativo, swarm y consumidor por construir) con entorno
uv y Python 3.13, para empezar a crear el código.

## Prompt

> En `tarea_1_curso_2` vamos a crear todo el código. Usa como molde el proyecto base
> oficial del taller (`agente-viajes-a2a.zip`, ya descargado en el mirror): incorpóralo,
> configúralo como proyecto **uv con Python 3.13** (pyproject consolidado con todas las
> dependencias de `requirements.txt`, sin instalar el proyecto como paquete porque el
> código corre desde la raíz con imports `src.*`), instala las dependencias y verifica
> lo que no requiera API key. Deja `.env` y `.venv` fuera de git.

## Verificación pedida

- `uv run python -V` → 3.13.x.
- Herramientas del agente de viajes funcionan sin API key.
- `uv run langgraph --version` disponible.
