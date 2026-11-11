<!--encabezado-grupo-->
> **Archivo:** `respuestas/39-chequeo-seguridad-antes-de-publicar.md`  
> **Objetivo:** 39 · Respuesta — Chequeo de seguridad antes de publicar  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2306 · **Última modificación:** 20261110 2322
<!--/encabezado-grupo-->

# 39 · Respuesta — Chequeo de seguridad antes de publicar

Prompt: [`../prompts_ejecutados/39-chequeo-seguridad-antes-de-publicar.md`](../prompts_ejecutados/39-chequeo-seguridad-antes-de-publicar.md)

## Escaneo de lo versionado

| Qué | Resultado |
|---|---|
| `.env` real (con la clave) | ✅ NO versionado (gitignored) |
| `.env.example` | ✅ `GOOGLE_API_KEY=` vacío |
| Claves `AIza…` de Google | ✅ ninguna |
| Tokens GitHub / `sk-` / `Bearer` | ✅ ninguno |
| `firebase_api_key` / password / secret | ✅ ninguno |
| URLs `trycloudflare.com` | túneles efímeros (ya muertos), no secretos |
| Email personal | ⚠️ `noreply@tarea1-curso2.invalid` en `pyproject.toml` |

Las coincidencias de "GOOGLE_API_KEY=…" eran docs/scripts que nombran la variable, no valores.

## Acción

- Se quitó el email de `pyproject.toml` (autor → "Grupo: Fabio Durán · Gustavo Reyes · Ezequiel Muñoz").
- El email **sigue en un commit viejo del historial** (ccf63ae): para purgarlo del todo hay que
  reescribir el historial (force-push), lo que rompe los clones existentes (el del Windows).

## Decisión pendiente

Publicar ahora (email solo en historial) vs. reescribir el historial antes de publicar.
