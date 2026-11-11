<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/17-redis-distribuido-cloudflare.md`  
> **Objetivo:** 17 · Reparto Ezequiel(Redis)/Tomás(RAG) — todo por Cloudflare, redes distintas  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2123 · **Última modificación:** 20261111 1406
<!--/encabezado-grupo-->

# 17 · Reparto Ezequiel(Redis)/Tomás(RAG) — todo por Cloudflare, redes distintas

**Fecha:** 2026-11-10

## Prompt

> Repartir la pega: Ezequiel a cargo del Redis, Tomás a cargo del RAG. Todo debe
> funcionar entre redes distintas (sin LAN), TODO por Cloudflare. Dejar absolutamente
> todo en las guías para que sea plug-and-play (otra sesión lo ejecutará).

## Decisión

Los túneles gratis de Cloudflare (`trycloudflare.com`) son solo HTTP; Redis es TCP.
Para exponer Redis entre redes distintas por Cloudflare se usa un **túnel con nombre
(TCP)**, que requiere un **dominio en la cuenta de Cloudflare**. El usuario eligió esta
opción: Mac (Ezequiel) hospeda el Redis y lo expone por túnel TCP; Windows (Tomás) lo
usa de forma remota.

## Verificación pedida

- Scripts del túnel TCP de Redis (Mac expone, Windows accede).
- `setup_windows.ps1` apuntando el RAG al Redis del Mac vía forwarder local.
- Guía end-to-end plug-and-play, todo por Cloudflare, con el reparto y los requisitos.
