<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/37-mac-verificar-arreglos-y-ronda.md`  
> **Objetivo:** 37 · Mac: verificar los arreglos de Tomás y regenerar la ronda real  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2259 · **Última modificación:** 20261110 2259
<!--/encabezado-grupo-->

# 37 · Mac: verificar los arreglos de Tomás y regenerar la ronda real

**Fecha:** 2026-11-11 · **Equipo:** Mac (nodo Ezequiel)

## Prompt

> Tras el aviso de Tomás (Windows) de que registró los arreglos del coordinador en los
> prompts 34/35: hacer `git pull`, reaplicar las fichas (la recarga las borra), verificar
> que los arreglos pasan en el Mac y regenerar la ronda real del Mac con las mejoras.
> (Numeración: Windows usa 36; el Mac usa 37.)

## Verificación pedida

- `uv run pytest` con los arreglos → verde.
- El coordinador del Mac marca `agente_local`/`agente_remoto` y no duplica respuestas.
- `evidencias/05-ronda-mac.md` regenerada contra el túnel real del Windows.
