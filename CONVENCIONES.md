<!--encabezado-grupo-->
> **Archivo:** `CONVENCIONES.md`  
> **Objetivo:** Convenciones de desarrollo  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1746 · **Última modificación:** 20261110 2306
<!--/encabezado-grupo-->

# Convenciones de desarrollo

## Encabezado de archivos (obligatorio)

Todo archivo que generemos y que admita comentarios (`.py`, `.md`, `.ps1`, `.sh`,
`.toml`, `.txt`, `.env.example`, `.gitignore`, `.html`, `.ipynb`) lleva al inicio un
encabezado con estos campos:

- **Archivo:** ruta del archivo en el repo.
- **Objetivo:** para qué sirve el archivo (una línea).
- **Grupo del curso:** `Fabio Durán - Gustavo Reyes - Ezequiel Muñoz`.
- **Creación:** fecha de creación en formato `yyyymmdd HHMM`.
- **Última modificación:** fecha de última modificación en formato `yyyymmdd HHMM`.

### Formato según el tipo de archivo

En archivos con comentarios de almohadilla (`.py`, `.toml`, `.txt`, `.sh`, `.ps1`,
`.env.example`, `.gitignore`):

```text
# --8<-- encabezado-grupo
# Archivo: <ruta>
# Objetivo: <una línea>
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: <yyyymmdd HHMM>
# Última modificación: <yyyymmdd HHMM>
# --8<-- fin-encabezado-grupo
```

En archivos Markdown/HTML (`.md`, `.html`) el encabezado es **visible** al renderizar:
un blockquote entre centinelas HTML invisibles `<!--encabezado-grupo-->` … `<!--/encabezado-grupo-->`:

```text
<!--encabezado-grupo-->
> **Archivo:** `<ruta>`  
> **Objetivo:** <una línea>  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** <yyyymmdd HHMM> · **Última modificación:** <yyyymmdd HHMM>
<!--/encabezado-grupo-->
```

En notebooks (`.ipynb`) ese mismo bloque va como primera celda Markdown. En archivos con frontmatter YAML (p. ej. `.opencode/agents/*.md`) va DENTRO del frontmatter como comentarios `#`.

### Qué queda fuera

Los formatos que **no** admiten comentarios: `*.json` (`langgraph.json`, `plan.json`,
`bruno/*.bru`, `bruno/bruno.json`), `uv.lock` (autogenerado) y `.python-version`
(solo la versión).

### Cómo se aplica

El encabezado se inserta y actualiza con
[`tools/aplicar_encabezados.py`](tools/aplicar_encabezados.py), que es **idempotente**:
conserva la fecha de **Creación** y solo refresca la de **Última modificación**.

```bash
uv run python tools/aplicar_encabezados.py           # aplica/actualiza en todo el repo
uv run python tools/aplicar_encabezados.py --check    # falla si algún archivo no tiene encabezado
```
