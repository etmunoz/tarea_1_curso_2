<!--encabezado-grupo-->
> **Archivo:** `respuestas/14-agente-cocina-recetas-chilenas.md`  
> **Objetivo:** 14 · Respuesta — Agente de cocina chilena con costeo  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2013 · **Última modificación:** 20261110 2306
<!--/encabezado-grupo-->

# 14 · Respuesta — Agente de cocina chilena con costeo

Prompt: [`../prompts_ejecutados/14-agente-cocina-recetas-chilenas.md`](../prompts_ejecutados/14-agente-cocina-recetas-chilenas.md)

## Archivos creados

- `src/agente_cocina/bd_recetas.py` — SQLite `data/recetas_cl.sqlite` (se crea sola) con:
  `recetas(nombre, porciones_base, descripcion)`, `ingredientes(nombre, unidad, precio_clp)`
  (precio **por la unidad usada en la receta**, sin conversión) y `receta_items(receta, ingrediente, cantidad)`.
  **20 recetas** chilenas clásicas. `costear_receta` escala por `personas/porciones_base` y
  calcula costo por ingrediente (`cantidad × precio`), **total** y **por persona** en CLP.
- `src/agente_cocina/herramientas.py` — `listar_recetas`, `ver_receta`, `costear_receta`.
- `src/agente_cocina/prompts.py`, `graph.py` (grafo `agente_cocina`, registrado en `langgraph.json`).
- `src/fichas.py` (ficha) y `src/coordinador/catalogo.py`/`.env.example` (sumado al catálogo local).
- `tests/test_bd_recetas.py` (5), `notebooks/cocina_paso_a_paso.ipynb`.

## Salida de la verificación

```text
$ costear_receta('Pastel de choclo', personas=4)
  choclo            6.0 unidad  x 500.0 = 3000 CLP
  carne molida    400.0 g       x   8.0 = 3200 CLP
  trutro de pollo 300.0 g       x   4.5 = 1350 CLP
  cebolla           2.0 unidad  x 300.0 =  600 CLP
  huevo             3.0 unidad  x 200.0 =  600 CLP
  albahaca         10.0 g       x  20.0 =  200 CLP
  azúcar           20.0 g       x   1.3 =   26 CLP
  TOTAL: 8976 CLP · por persona: 2244 CLP

$ costear_receta('Empanadas de pino', 4)  -> total 3607 CLP · por persona 902 (base 6, escalado)
$ uv run pytest tests/test_bd_recetas.py -q  -> 5 passed
$ uv run pytest -q  -> 31 passed, 6 skipped
```

## Estado

Agente de cocina ✅ (verificado sin key). Integrado al coordinador (lo enruta ante
preguntas de recetas/costos). Ejecución en vivo por A2A requiere `GOOGLE_API_KEY`.
