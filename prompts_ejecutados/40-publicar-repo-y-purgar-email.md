<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/40-publicar-repo-y-purgar-email.md`  
> **Objetivo:** 40 · Hacer público el repo y purgar el email del historial  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2312 · **Última modificación:** 20261111 1343
<!--/encabezado-grupo-->

# 40 · Hacer público el repo y purgar el email del historial

**Fecha:** 2026-11-11 · **Equipo:** Mac (nodo Ezequiel)

## Prompt

> Hacer público el repo para compartirlo con los compañeros. Antes, borrar el email
> personal también del historial (commit ccf63ae y autores).

## Qué se hizo

- `git-filter-repo` reescribió TODO el historial: reemplazó `etmunoz@gmail.com` por
  `noreply@tarea1-curso2.invalid` en el contenido (pyproject) y en el autor/committer de
  los 33 commits. Config local de git ajustada para que los commits futuros no lo re-agreguen.
- `git push --force` del historial reescrito.
- Repo cambiado a **PÚBLICO**.

## Verificación

```text
$ git log -S 'etmunoz@gmail.com' --all   -> (vacío)
$ git log --format='%an <%ae>' | sort -u -> Ezequiel Muñoz Krsulovic <noreply@tarea1-curso2.invalid>
$ gh repo view --json visibility          -> PUBLIC · private=false
```

## IMPORTANTE para el nodo Windows

El historial cambió (hashes nuevos). El clon del Windows **debe re-clonar**:

```powershell
cd "$env:USERPROFILE\proyectos"; Rename-Item tarea_1_curso_2 tarea_1_curso_2_old
gh repo clone etmunoz/tarea_1_curso_2
```

(o `git fetch origin && git reset --hard origin/main` si no hay cambios locales sin pushear).
