<!--encabezado-grupo-->
> **Archivo:** `respuestas/40-publicar-repo-y-purgar-email.md`  
> **Objetivo:** 40 · Respuesta — Repo público y email purgado  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2312 · **Última modificación:** 20261111 1738
<!--/encabezado-grupo-->

# 40 · Respuesta — Repo público y email purgado

Prompt: [`../prompts_ejecutados/40-publicar-repo-y-purgar-email.md`](../prompts_ejecutados/40-publicar-repo-y-purgar-email.md)

## Lo que se hizo (en su momento)

- **Purga del email** del historial completo con `git-filter-repo` (`--replace-text` sobre
  el contenido + `--mailmap` mapeando `etmunoz@gmail.com` → `noreply@tarea1-curso2.invalid`
  en autor y committer de los ~33 commits de entonces).
- **Force-push** del historial reescrito. Hubo un `HTTP 400` que se resolvió con
  `git config http.postBuffer 524288000` y `http.version HTTP/1.1`.
- Repo hecho **PÚBLICO**: https://github.com/etmunoz/tarea_1_curso_2
- Chequeo de secretos (prompt 39): sin claves `AIza…`, sin tokens, `.env` fuera de git.
- `git config user.email` del Mac quedó en `noreply@tarea1-curso2.invalid`.

## ⚠️ Regresión detectada después (importante)

Al revisar el historial más tarde se encontró que el email personal **volvió a entrar** en
UN commit posterior:

```text
$ git log --all --format='%h %ae | %ce | %s' | grep etmunoz@gmail.com
4c89013 etmunoz@gmail.com | etmunoz@gmail.com | 42 · Windows: evidencias finales …

$ git log --format='%ae|%ce' origin/main | sort -u
etmunoz@gmail.com|etmunoz@gmail.com            ← presente en lo PÚBLICO
noreply@tarea1-curso2.invalid|noreply@tarea1-curso2.invalid
```

Causa: el commit `4c89013` (prompt 42) se hizo en el **Windows**, cuyo git aún usaba
`etmunoz@gmail.com`. Al integrarlo (prompt 43, fast-forward) y pushear, quedó en el
historial público. La purga del prompt 40 fue correcta para todo lo anterior; esto se
reintrodujo por configuración del otro equipo.

## Decisión tomada

Se evaluó purgarlo de nuevo (mailmap + force-push), pero eso cambia los hashes y obliga a
re-clonar en el Windows. **El grupo decidió dejarlo como está**: el email queda visible en
el commit `4c89013` del repo público y no se reescribe el historial.

Si en el futuro se quiere quitar: reescribir con `git-filter-repo --mailmap`
(`etmunoz@gmail.com` → `noreply@tarea1-curso2.invalid`) + force-push, y en el Windows fijar
`git config user.email "noreply@tarea1-curso2.invalid"` antes de volver a commitear, y
re-clonar el repo.
