<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/08-aplicar-convenciones-opencode.md`  
> **Objetivo:** 08 · Aplicar las convenciones de los agentes OpenCode (@spec / @implementador)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1923 · **Última modificación:** 20261111 1857
<!--/encabezado-grupo-->

# 08 · Aplicar las convenciones de los agentes OpenCode (@spec / @implementador)

**Fecha:** 2026-11-10
**Objetivo:** usar lo que corresponde de `.opencode/agents/spec.md` e
`implementador.md` en el trabajo ya hecho.

## Prompt

> Revisa `.opencode/agents/implementador.md` y `.opencode/agents/spec.md` y aplica lo
> que corresponda de ellos al proyecto.

## Qué se aplicó

- Regla de `@spec`: "la última tarea de cada pedido es siempre un notebook en
  `notebooks/` generado con `nbformat`". Faltaban los del agente de Ezequiel y del
  swarm (el del consumidor ya existía).
- Formato de tarea de `@spec`: campo `descripcion` en las tareas de `plan.json`.

## Verificación pedida

- `notebooks/ezequiel_paso_a_paso.ipynb` y `notebooks/swarm_paso_a_paso.ipynb` válidos.
- `plan.json` con `descripcion` en las tareas y las tareas-notebook `e02`/`s02`.
