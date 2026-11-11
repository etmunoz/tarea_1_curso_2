<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/09-roadmap-y-fix-frontmatter.md`  
> **Objetivo:** 09 · ROADMAP del taller + encabezado en archivos con frontmatter  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1928 · **Última modificación:** 20261110 2147
<!--/encabezado-grupo-->

# 09 · ROADMAP del taller + encabezado en archivos con frontmatter

**Fecha:** 2026-11-10

## Prompt

> De acuerdo a la tarea, crea un `ROADMAP.md` con todo lo que hay que hacer desde el
> principio. (Y: los agentes OpenCode `spec.md`/`implementador.md` quedaron sin
> encabezado visible.)

## Qué se hizo

- `ROADMAP.md`: todo el trabajo, desde el inicio, mapeado a las 10 páginas del taller
  y al estado real del repo (✅/🟡/⬜), con la nota taller-viejo vs. base-real.
- Corrección del encabezado en archivos con **frontmatter YAML** (los agentes
  OpenCode): el encabezado iba **antes** del `---`, lo que rompe el frontmatter
  (OpenCode lo exige en la línea 1) y no se ve al renderizar. Ahora va **dentro** del
  frontmatter como comentarios `#`.

## Verificación pedida

- `ROADMAP.md` creado.
- `.opencode/agents/*.md` empiezan con `---` y su YAML parsea (description, mode, model…).
- `tools/aplicar_encabezados.py --check` → OK.
