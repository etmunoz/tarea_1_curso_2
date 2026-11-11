<!--encabezado-grupo-->
> **Archivo:** `respuestas/06-regla-encabezado-archivos.md`  
> **Objetivo:** 06 · Respuesta — Regla: encabezado de archivos del grupo  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1746 · **Última modificación:** 20261111 1413
<!--/encabezado-grupo-->

# 06 · Respuesta — Regla: encabezado de archivos del grupo

Prompt: [`../prompts_ejecutados/06-regla-encabezado-archivos.md`](../prompts_ejecutados/06-regla-encabezado-archivos.md)

## Qué se hizo

- `CONVENCIONES.md` — regla del encabezado (campos, formato por tipo, qué queda fuera).
- `tools/aplicar_encabezados.py` — script idempotente que inserta/actualiza el encabezado
  (conserva Creación, refresca Última modificación). Soporta `--check`.
- Se aplicó a todos los archivos que admiten comentarios.

## Salida

```text
$ uv run python tools/aplicar_encabezados.py
Encabezado aplicado/actualizado en 60 archivos (+ notebooks). Modificación: 20261110 1748

$ uv run python tools/aplicar_encabezados.py --check
OK · 60 archivos con encabezado.

$ uv run pytest -q
8 passed, 3 skipped
```

Cubre `.py`, `.md`, `.toml`, `.txt`, `.env.example`, `.gitignore`, `.html` y el
`.ipynb` (como primera celda Markdown). Quedan fuera, por no admitir comentarios:
`langgraph.json`, `plan.json`, `bruno/*`, `uv.lock` y `.python-version`.

## Nota de implementación

La primera versión del script se autocorrompía al procesarse a sí misma (su cuerpo
contiene los centinelas como texto). Se corrigió anclando la detección y el borrado
al **inicio** del archivo; ahora es seguro e idempotente (conserva `Creación`, solo
refresca `Última modificación`).

## Estado

Hecho y verificado.
