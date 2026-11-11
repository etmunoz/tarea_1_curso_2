<!--encabezado-grupo-->
> **Archivo:** `respuestas/36-windows-mac-actualizado.md`  
> **Objetivo:** 36 · Respuesta — Windows: el Mac hizo pull y reaplicó sus fichas; verificación  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2256 · **Última modificación:** 20261110 2325
<!--/encabezado-grupo-->

# 36 · Respuesta — Windows: el Mac hizo pull y reaplicó sus fichas; verificación

Prompt: [`../prompts_ejecutados/36-windows-mac-actualizado.md`](../prompts_ejecutados/36-windows-mac-actualizado.md)

## Qué se verificó

```text
Mac  agente_ezequiel  -> 'Agente de Ezequiel'         ✓
Mac  agente_cocina    -> 'Agente de cocina chilena'   ✓
Win  agente_tomas     -> 'agente_tomas'               ✗ ficha perdida otra vez
git fetch             -> sin commits nuevos del Mac (main == origin/main)
```

## Lo malo / lo que se arregló

- La ficha de Tomás **se volvió a perder** en el Windows. En el prompt 35 se reaplicó antes de
  la corrida, pero después se actualizó la fecha del encabezado de 6 archivos `.py`, y eso
  recargó `langgraph dev` otra vez.
- Se reaplicó: `configurar_fichas.py --grafos agente_tomas` → `✓ «Agente de Tomás»`.

## Comprobación: ¿escribir `.md` también recarga el servidor?

Se escribieron estos dos registros (`.md`) y se volvió a leer la ficha de Tomás:

```text
Tomás después de escribir .md: 'Agente de Tomás'   ✓ (sigue)
```

**No:** escribir `.md` no recarga el servidor; solo lo recargan los cambios en `.py`.

## Lección

Mientras los agentes estén corriendo para la prueba, conviene **no editar `.py`** en ese equipo,
o reaplicar las fichas justo antes de correr el coordinador. Un arreglo de fondo sería aplicar
las fichas al arrancar el grafo, en vez de hacer un PATCH externo. Queda como idea, no se hizo.

## Estado

Los dos nodos están listos con las fichas correctas y el mismo código (`7d77cb6`). Faltan las
capturas `01-saltos.png` y `03-tunel.png`, y empaquetar la entrega.
