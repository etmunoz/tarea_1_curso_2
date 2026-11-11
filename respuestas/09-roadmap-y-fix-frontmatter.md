<!--encabezado-grupo-->
> **Archivo:** `respuestas/09-roadmap-y-fix-frontmatter.md`  
> **Objetivo:** 09 · Respuesta — ROADMAP + fix frontmatter  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1928 · **Última modificación:** 20261111 1957
<!--/encabezado-grupo-->

# 09 · Respuesta — ROADMAP + fix frontmatter

Prompt: [`../prompts_ejecutados/09-roadmap-y-fix-frontmatter.md`](../prompts_ejecutados/09-roadmap-y-fix-frontmatter.md)

## Qué se hizo

- `ROADMAP.md`: fases 0–4 + extra, con estado por paso del taller y el próximo paso sugerido.
- `tools/aplicar_encabezados.py`: soporte de frontmatter YAML. Para archivos que
  empiezan con `---`, el encabezado se inserta **dentro** del frontmatter como
  comentarios `#` (no rompe el `---` inicial ni la config de OpenCode). El `Objetivo`
  de esos archivos toma el campo `description:`.

## Salida

```text
.opencode/agents/implementador.md → keys: ['description','mode','model','temperature','tools','write']
.opencode/agents/spec.md          → keys: ['description','mode','model','tools','write','edit']
tools/aplicar_encabezados.py --check  →  OK · 66 archivos con encabezado
uv run pytest -q  →  11 passed, 4 skipped
```

## Nota

El bug afectaba solo a los 2 archivos con frontmatter (los agentes OpenCode); el
resto de los `.md` siempre tuvo su encabezado (comentario `<!-- -->`, invisible al
renderizar pero presente en el archivo).

## Estado

Hecho y verificado.
