<!--encabezado-grupo-->
> **Archivo:** `respuestas/29-corrida-real-2-pc.md`  
> **Objetivo:** 21 · Respuesta — Corrida real entre 2 computadores  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2225 · **Última modificación:** 20261111 1205
<!--/encabezado-grupo-->

# 21 · Respuesta — Corrida real entre 2 computadores

Prompt: [`../prompts_ejecutados/29-corrida-real-2-pc.md`](../prompts_ejecutados/29-corrida-real-2-pc.md)

## Resultado (lado Mac) — ✅ cross-machine operativo

El coordinador del Mac enrutó, por túneles HTTP de Cloudflare:
- **local** → Ezequiel (ML) y cocina (costeo).
- **remoto** → Tomás, corriendo en el **Windows**, que respondió con su **RAG** (símbolos del nivel 2).

Evidencias guardadas en el Mac:
- `evidencias/04-catalogo-mac.txt` — catálogo (2 locales + 1 remoto).
- `evidencias/05-ronda-mac.md` — la ronda completa (ver prompt).
- `evidencias/02-ficha-agente_{ezequiel,cocina,viajes}.json`.

## Siguiente

Desde el Windows: `./scripts/win_coordinador.ps1 "https://<tunel-mac>"` genera
`05-ronda-windows.md` (Reiki local → Tomás; ML/cocina remoto → Mac). Con ambas rondas
(`*-mac` y `*-windows`) queda demostrada la operatividad en los dos sentidos.
