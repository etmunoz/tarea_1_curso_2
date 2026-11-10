<!-- --8<-- encabezado-grupo
Archivo: respuestas/02-crear-repo-contenido.md
Objetivo: 02 · Respuesta — Crear el repo de contenido `tarea_1_curso_2`
Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
Creación: 20261110 1620
Última modificación: 20261110 1923
--8<-- fin-encabezado-grupo -->

# 02 · Respuesta — Crear el repo de contenido `tarea_1_curso_2`

Prompt: [`../prompts_ejecutados/02-crear-repo-contenido.md`](../prompts_ejecutados/02-crear-repo-contenido.md)

## Qué se hizo

```bash
cd /Users/ezequielmunoz/proyectos/tarea_1_curso_2
git init -q && git branch -M main
git add -A && git commit -m "Taller A2A (Curso 2 · Sesión 1) extraído a Markdown, 10 páginas"
gh repo create tarea_1_curso_2 --private --source=. --remote=origin --push
```

## Salida

```text
https://github.com/etmunoz/tarea_1_curso_2
 * [new branch]      HEAD -> main
repo: tarea_1_curso_2 · visibilidad: PRIVATE · rama: main
```

Archivos en el remoto: `README.md`, `.gitignore`, `taller-a2a/01…10-*.md`,
`taller-a2a/index.md`, `taller-a2a/clase.html`.

## Estado

Hecho. Repo privado creado y sincronizado.
