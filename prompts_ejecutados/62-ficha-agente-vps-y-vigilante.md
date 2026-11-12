<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/62-ficha-agente-vps-y-vigilante.md`  
> **Objetivo:** 62 · Corregir la ficha de agente.etmk.cl (descripción) y dejarla persistente (vigilante)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1910 · **Última modificación:** 20261112 1910
<!--/encabezado-grupo-->

# 62 · Ficha correcta en agente.etmk.cl + vigilante persistente

**Fecha:** 2026-11-12 · **Equipo:** VPS (puente `agente.etmk.cl`) + interop con Gustavo

Respuesta: [`../respuestas/62-ficha-agente-vps-y-vigilante.md`](../respuestas/62-ficha-agente-vps-y-vigilante.md)

## Contexto / instrucción del usuario

Al darle a Gustavo el `curl` de `https://agente.etmk.cl`, su coordinador respondía que **la Agent Card
no entregaba info para identificar al agente**: la ficha publicada tenía la descripción genérica de
langgraph (`"agente_ezequiel assistant"`, skill `"agente_ezequiel Capabilities"`, tags
`["assistant","langgraph"]`) y no mencionaba *machine learning / modelos / IA*, así que el supervisor
de Gustavo no tenía evidencia para enrutar.

> "esto le da a Gustavo" / "el curl de tu agente no entrega toda la info que necesita para
> identificarlo."

## Qué se hizo

- Se diagnosticó: el puente (`agente.etmk.cl`) arma su card clásica **desde la card de langgraph**
  (`card_clasica` usa `card_langgraph.get("description")`). El langgraph del VPS había **perdido la
  ficha**: cada deploy (`git reset --hard`) cambia archivos en `src/` y `langgraph dev` hace
  hot-reload, que **borra** las fichas aplicadas.
- Se **re-aplicó** la ficha en el VPS (`configurar_fichas.py --grafos agente_ezequiel,agente_cocina`).
- Se creó un servicio systemd **`agente-fichas`** que corre `configurar_fichas.py --vigilar`
  (re-aplica las fichas apenas langgraph las borra, chequeo cada 5 s), para que la card quede
  **persistente** a través de reloads/deploys.
