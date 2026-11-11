<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/06-regla-encabezado-archivos.md`  
> **Objetivo:** 06 · Regla: encabezado de archivos del grupo  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1746 · **Última modificación:** 20261110 2147
<!--/encabezado-grupo-->

# 06 · Regla: encabezado de archivos del grupo

**Fecha:** 2026-11-10
**Objetivo:** fijar como regla de desarrollo un encabezado estándar en cada archivo
y aplicarlo a todos los archivos actuales.

## Prompt

> Agrega como regla de desarrollo que los comentarios de encabezado de cada archivo
> que generemos (`.py`, `.md`, `.ps1`, `.sh`, etc.) tengan: nombre del archivo,
> objetivo del archivo, grupo del curso (Fabio Durán - Gustavo Reyes - Ezequiel Muñoz),
> fecha de creación (`yyyymmdd HHMM`) y fecha de última modificación (`yyyymmdd HHMM`).
> Procede a modificar todos los archivos actuales.

## Verificación pedida

- Regla escrita en `CONVENCIONES.md`.
- Un script idempotente que inserte/actualice el encabezado.
- Todos los archivos que admiten comentarios, con el encabezado.
- `--check` no reporta faltantes.
