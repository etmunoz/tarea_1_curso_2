<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/07-swarm-agente-actividades.md`  
> **Objetivo:** 07 · Swarm con el agente de actividades  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1920 · **Última modificación:** 20261110 2227
<!--/encabezado-grupo-->

# 07 · Swarm con el agente de actividades

**Fecha:** 2026-11-10
**Objetivo:** sumar un tercer agente (actividades) al swarm vuelos + hoteles, con
handoff entre los tres.

## Prompt

> Agrega al swarm (vuelos + hoteles) un tercer agente de **actividades**:
>
> 1. Una herramienta `buscar_actividades(ciudad)` con datos simulados (LIM, BOG, EZE:
>    actividad, tipo, duración, precio). No cambies el agente de viajes nativo.
> 2. Un `SYSTEM_ACTIVIDADES` en `src/swarm/prompts.py`, y actualiza los prompts de
>    vuelos y hoteles para que puedan transferir también a actividades.
> 3. En `src/swarm/graph.py`: una herramienta de handoff a `actividades`, el agente
>    `actividades` (con sus transferencias de vuelta a vuelos y hoteles) y súmalo a
>    `create_swarm`. Cualquiera puede transferir a cualquiera de los otros dos.
> 4. Un test de `buscar_actividades` sin API key, y uno del swarm que se salte sin clave.

## Verificación pedida

- `uv run pytest tests/test_swarm.py` → actividades en verde sin key.
- `buscar_actividades('LIM')` devuelve 2 panoramas.
- El swarm tiene 3 agentes y transfiere a `actividades` ante un panorama (en vivo).
