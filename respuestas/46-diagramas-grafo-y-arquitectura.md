<!--encabezado-grupo-->
> **Archivo:** `respuestas/46-diagramas-grafo-y-arquitectura.md`  
> **Objetivo:** Respuesta 46 · Diagramas: grafo del coordinador y arquitectura de agentes  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 0743 · **Última modificación:** 20261111 0743
<!--/encabezado-grupo-->

# Respuesta 46 · Diagramas: grafo del coordinador y arquitectura de agentes

## Qué se generó (en `evidencias/`)

- **`07-grafo-coordinador.svg`** — grafo del coordinador: `__start__ → guardia_entrada
  → enrutar → {consultar | sin_agente} → __end__`, con el guardrail de entrada, el
  saneo de salida/A2A y la rama de estado controlado (`agente_no_disponible`).
- **`08-arquitectura.svg`** — arquitectura completa: Mac (Ezequiel, cocina, viajes +
  SQLite) y Windows (Tomás + RAG en Redis), cada uno con `langgraph dev :2024`,
  coordinador con guardrails y app web, unidos por túneles HTTP de Cloudflare (A2A
  bidireccional, sin LAN ni TCP). Modelo: Gemini.
- **`09-diagramas.md`** — índice que embebe el **mermaid auténtico** del grafo
  (`graph.get_graph().draw_mermaid()`, se renderiza en GitHub) y enlaza ambos SVG.

## Grafo auténtico (del grafo compilado)

```
__start__ → guardia_entrada
guardia_entrada -. ok .-> enrutar
guardia_entrada -. bloqueado .-> __end__
enrutar -.-> consultar
enrutar -.-> sin_agente
consultar → __end__
sin_agente → __end__
```

Ambos diagramas se mostraron al usuario y se incluyen en la entrega.
