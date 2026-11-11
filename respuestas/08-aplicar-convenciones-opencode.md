<!--encabezado-grupo-->
> **Archivo:** `respuestas/08-aplicar-convenciones-opencode.md`  
> **Objetivo:** 08 · Respuesta — Aplicar las convenciones OpenCode  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1923 · **Última modificación:** 20261111 1224
<!--/encabezado-grupo-->

# 08 · Respuesta — Aplicar las convenciones OpenCode

Prompt: [`../prompts_ejecutados/08-aplicar-convenciones-opencode.md`](../prompts_ejecutados/08-aplicar-convenciones-opencode.md)

## Qué se hizo

- `notebooks/ezequiel_paso_a_paso.ipynb` (nbformat) — 3 pasos: herramientas · el
  agente por A2A nativo (assistant_id + tarjeta) · consumo por message/send.
- `notebooks/swarm_paso_a_paso.ipynb` (nbformat) — 3 pasos: herramientas · el swarm
  de 3 agentes · conversación con handoffs vuelos→hoteles→actividades.
- `plan.json` — campo `descripcion` en e01, c01–c03, s01; tareas-notebook `e02`, `s02`.

## Salida

```text
notebooks/ezequiel_paso_a_paso.ipynb  ok  8 celdas
notebooks/swarm_paso_a_paso.ipynb     ok  8 celdas
tools/aplicar_encabezados.py --check  →  OK · 63 archivos con encabezado
```

## Nota sobre spec.md / implementador.md

Son las definiciones de los agentes OpenCode del proyecto (modelo, reglas de
construcción LangGraph, formato de tareas). Sí están consideradas: el código ya
sigue sus reglas (prompts separados, herramientas con docstring, A2A nativo por
`langgraph.json`, `contextId` UUID, notebooks con `nbformat`). Ambos archivos
tienen el encabezado de grupo.

## Estado

Hecho y verificado.
