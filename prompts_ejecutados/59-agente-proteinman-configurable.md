<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/59-agente-proteinman-configurable.md`  
> **Objetivo:** 59 · Agregar ProteinMAN como 5º agente configurable + fix de chips vacíos  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1624 · **Última modificación:** 20261112 1624
<!--/encabezado-grupo-->

# 59 · ProteinMAN configurable + fix de chips

**Fecha:** 2026-11-12 · **Equipo:** VPS `coordinador.etmk.cl` + ProteinMAN (remoto, langgraph)

Respuesta: [`../respuestas/59-agente-proteinman-configurable.md`](../respuestas/59-agente-proteinman-configurable.md)

## Instrucciones del usuario (textual)

1. > "agrega otro además de Ezequiel, Tomas, Fabio y Gustavo, a uno que se llame Proteinman, para
>    que en la configuración pueda agregarlos."
2. > "https://founded-mandatory-examined-nominated.trycloudflare.com/" (la URL de Proteinman)

## Qué se hizo

- Se agregó **ProteinMAN** como 5º agente configurable del coordinador web: entrada en
  `AGENTES_CFG`, campo `🦸 Proteinman` en el ⚙️, icono en `meta()` y en la lista `CLAVES` del JS.
- Se **sondeó** la URL: es langgraph nativo, su `graph_id` real es **`proteinman`** (no
  `agente_proteinman`); se corrigió el catálogo.
- Se dejó la URL cargada en la config del VPS.
- Se corrigió un bug latente: `_agentes()` usaba `a.descripcion` (método) sin llamar → `_agentes()`
  reventaba y los **chips de agentes** salían vacíos. Ahora llama `a.descripcion()`.
