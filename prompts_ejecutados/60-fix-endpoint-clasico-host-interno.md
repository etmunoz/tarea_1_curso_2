<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/60-fix-endpoint-clasico-host-interno.md`  
> **Objetivo:** 60 · Levantar Ezequiel (Mac), sumar Gustavo y arreglar endpoint clásico con host interno  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1642 · **Última modificación:** 20261112 1642
<!--/encabezado-grupo-->

# 60 · Ezequiel (Mac) + Gustavo + fix de endpoint clásico

**Fecha:** 2026-11-12 · **Equipo:** Mac (Ezequiel) + VPS `coordinador.etmk.cl` + Gustavo (remoto)

Respuesta: [`../respuestas/60-fix-endpoint-clasico-host-interno.md`](../respuestas/60-fix-endpoint-clasico-host-interno.md)

## Instrucciones del usuario (textual)

1. > "necesito que levantes la URL de Ezequiel en el Mac"
2. > "actualiza la config del VPS con la nueva URL y revisa la de gustavo que me dio:
>    https://devon-harris-retain-shoe.trycloudflare.com"

## Qué se hizo

- Se levantó un túnel Cloudflare nuevo para el Ezequiel del Mac (el anterior quedó zombie) y se
  actualizó la config del coordinador del VPS con esa URL; verificado (responde ML).
- Se sondeó la URL de Gustavo: es `agente_meteorologo` (A2A clásico, SDK a2a-protocol.org). Se
  agregó a la config.
- **Bug encontrado y corregido:** la ficha de Gustavo anuncia su endpoint como `http://127.0.0.1:8003`
  (su bind interno). Al consumirlo por túnel, el cliente A2A intentaba conectarse a ese host local
  → `Connection refused`. Se corrigió `_endpoint_clasico` en `src/coordinador/a2a.py`: si el host
  anunciado es local/privado, se usa la `base` (el túnel por el que se llegó) conservando el path.
