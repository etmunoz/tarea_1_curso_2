<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/18-coordinador-bidireccional-evidencias.md`  
> **Objetivo:** 18 · Coordinador bidireccional y evidencias en ambos PC (todo por túnel HTTP)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2136 · **Última modificación:** 20261110 2322
<!--/encabezado-grupo-->

# 18 · Coordinador bidireccional y evidencias en ambos PC (todo por túnel HTTP)

**Fecha:** 2026-11-10

## Prompt

> Tomás no expone ningún Redis, solo su RAG por Cloudflare (a través de su agente); nada por
> TCP/LAN. La misma repo sirve para ambos casos. Debe ser bidireccional y transparente: desde
> el Mac uso el coordinador con acceso a lo local y lo remoto, y desde el Windows igual. La
> prueba concluye con consultas en ambos lados y respuestas con evidencias registradas en ambos
> PC (Mac y Windows). Registrar todos los prompts.

## Verificación pedida

- Sin scripts TCP/LAN; Redis local a Tomás (no se expone por red).
- Coordinadores en ambos equipos: Mac (local ezequiel,cocina · remoto tomas) y Windows
  (local tomas · remoto ezequiel,cocina), ambos por túnel HTTP de Cloudflare.
- Evidencias etiquetadas por equipo (`*-mac`, `*-windows`).
