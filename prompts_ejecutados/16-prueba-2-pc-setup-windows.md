<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/16-prueba-2-pc-setup-windows.md`  
> **Objetivo:** 16 · Prueba entre 2 computadores: setup del Windows  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2113 · **Última modificación:** 20261111 1343
<!--/encabezado-grupo-->

# 16 · Prueba entre 2 computadores: setup del Windows

**Fecha:** 2026-11-10

## Prompt

> Seguir con la prueba entre mis 2 computadores. El otro computador no tiene nada:
> necesito que todo esté commiteado y pusheado, y un paso a paso para que allá descargue
> el repo, actualice y configure. Dejar además un `.ps1` para el otro equipo con lo necesario.

## Verificación pedida

- Repo limpio y pusheado; un clon limpio tiene todo lo necesario (incluidos los fixes de hoy).
- `scripts/setup_windows.ps1` que instala prerrequisitos, hace `uv sync`, configura `.env`,
  valida la clave y (opcional) levanta Redis + RAG.
- Guía con el arranque desde cero (clonar repo privado) referenciando el script.
