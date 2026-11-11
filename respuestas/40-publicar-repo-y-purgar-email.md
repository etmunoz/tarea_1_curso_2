<!--encabezado-grupo-->
> **Archivo:** `respuestas/40-publicar-repo-y-purgar-email.md`  
> **Objetivo:** 40 · Respuesta — Repo público y email purgado  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2312 · **Última modificación:** 20261111 0829
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

## Corrección pendiente (requiere decisión)

Para quitarlo hay que reescribir el historial otra vez (mailmap + force-push), lo que
cambia los hashes y **obliga a re-clonar en el Windows**. Además, el git del Windows debe
fijar `git config user.email "noreply@tarea1-curso2.invalid"` para no reintroducirlo.

## Acción requerida en el Windows (tras cualquier reescritura)

Re-clonar el repo (el historial cambia de hashes).
