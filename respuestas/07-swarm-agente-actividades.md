<!--encabezado-grupo-->
> **Archivo:** `respuestas/07-swarm-agente-actividades.md`  
> **Objetivo:** 07 · Respuesta — Swarm con el agente de actividades  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1920 · **Última modificación:** 20261111 0735
<!--/encabezado-grupo-->

# 07 · Respuesta — Swarm con el agente de actividades

Prompt: [`../prompts_ejecutados/07-swarm-agente-actividades.md`](../prompts_ejecutados/07-swarm-agente-actividades.md)

## Archivos modificados / creados

- `src/agente_viajes/herramientas.py` — catálogo `ACTIVIDADES` (LIM/BOG/EZE) y
  herramienta `buscar_actividades(ciudad)`. El agente de viajes nativo sigue siendo
  vuelos + hoteles (no se tocó su lista de herramientas).
- `src/swarm/prompts.py` — `SYSTEM_ACTIVIDADES`; vuelos y hoteles ahora pueden
  transferir también a actividades.
- `src/swarm/graph.py` — handoff `a_actividades`, agente `actividades` (transfiere de
  vuelta a vuelos y hoteles) y `create_swarm([vuelos, hoteles, actividades])`.
- `tests/test_swarm.py` — pruebas de `buscar_actividades` (sin key) + swarm (skip sin key).
- `plan.json` — grupo `swarm` HECHO, tarea `s01`.

## Salida de la verificación

```text
$ uv run python -c "from src.agente_viajes.herramientas import buscar_actividades; print(buscar_actividades.invoke({'ciudad':'LIM'}))"
[{'actividad': 'Tour gastronómico en Barranco', 'tipo': 'gastronomía', 'horas': 4, 'precio_clp': 45000},
 {'actividad': 'City tour Centro Histórico', 'tipo': 'cultural', 'horas': 3, 'precio_clp': 28000}]

$ uv run pytest -q
11 passed, 4 skipped
```

(Los 4 saltados requieren `langgraph dev` o `GOOGLE_API_KEY`.)

## Cómo probarlo en vivo (requiere GOOGLE_API_KEY)

```bash
uv run python -m src.swarm.graph
# > ¿Qué actividades puedo hacer en Lima?
# [actividades] ... Tour gastronómico en Barranco, City tour Centro Histórico ...
```

## Estado

Hecho y verificado sin API key. Falta la corrida en vivo del swarm con Gemini.
