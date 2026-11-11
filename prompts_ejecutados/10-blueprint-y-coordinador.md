<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/10-blueprint-y-coordinador.md`  
> **Objetivo:** 10 · Blueprint + coordinador (supervisor)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1933 · **Última modificación:** 20261111 1224
<!--/encabezado-grupo-->

# 10 · Blueprint + coordinador (supervisor)

**Fecha:** 2026-11-10

## Prompt

> Arranquemos por el blueprint y el coordinador.

## Qué se pidió

1. **Blueprint** del agente de Ezequiel (tabla del Paso 2 del taller).
2. **Coordinador/supervisor** (Paso 7): lee las fichas de varios agentes remotos
   (locales + compañeros vía `URLS_AGENTES`) y enruta la pregunta al que corresponde,
   reenviando por A2A; la respuesta remota es un dato etiquetado `[Nombre] …`.

## Verificación pedida

- `blueprint-ezequiel.md` creado.
- `src/coordinador/` con cliente A2A general, catálogo desde el entorno, supervisor
  LangGraph (decisión con `with_structured_output`) y notebook paso a paso.
- Tests sin API key en verde; grafo y demo en vivo documentados.
