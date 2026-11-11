<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/29-corrida-real-2-pc.md`  
> **Objetivo:** 21 · Corrida real entre 2 computadores (Mac ↔ Windows por Cloudflare)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2225 · **Última modificación:** 20261111 1406
<!--/encabezado-grupo-->

# 21 · Corrida real entre 2 computadores (Mac ↔ Windows por Cloudflare)

**Fecha:** 2026-11-11

## Prompt

> Dejá el Mac listo y corré la prueba real entre los 2 PC cuando llegue la URL del Windows.
> Ir dejando las evidencias.

## Qué se hizo (lado Mac)

- `langgraph dev` (Ezequiel, cocina, viajes) + fichas configuradas.
- `cloudflared` instalado; túnel HTTP del Mac abierto y verificado.
- Con la URL del túnel del Windows (Tomás), se corrió `mac_coordinador.sh`:
  local[ezequiel, cocina] + remoto[tomas por el túnel del Windows].

## Evidencia (evidencias/05-ronda-mac.md) — enrutamiento real cross-machine

```text
> ¿Qué técnica uso si tengo desbalance de clases?   -> [Agente de Ezequiel]        (local, Mac)
> ¿Qué símbolos se aprenden en el nivel 2 de Reiki? -> [Agente de Tomás]           (REMOTO, Windows; vía RAG)
> ¿Cuánto cuesta un pastel de choclo para 4?        -> [Agente de cocina chilena]  (local, Mac) → $8.976 CLP ($2.244/persona)
> ¿Quién ganó el mundial de 1962?                   -> sin_agente
```

Archivos: `evidencias/04-catalogo-mac.txt`, `evidencias/05-ronda-mac.md`,
`evidencias/02-ficha-agente_{ezequiel,cocina,viajes}.json`.

## Pendiente (lado Windows)

El Windows corre `win_coordinador.ps1 "<tunel-mac>"` para generar `04-catalogo-windows.txt`
y `05-ronda-windows.md` (Reiki local, ML/cocina remotos en el Mac) y las sube.
