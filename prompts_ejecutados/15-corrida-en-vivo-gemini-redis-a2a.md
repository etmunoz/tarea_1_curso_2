<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/15-corrida-en-vivo-gemini-redis-a2a.md`  
> **Objetivo:** 15 · Corrida en vivo (Gemini + Redis + A2A) y correcciones  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2041 · **Última modificación:** 20261111 2016
<!--/encabezado-grupo-->

# 15 · Corrida en vivo (Gemini + Redis + A2A) y correcciones

**Fecha:** 2026-11-10

## Prompt

> Ya hay saldo en la API key. Probar en vivo que todo funciona: validar la clave,
> cargar el RAG, levantar los agentes por A2A y el coordinador. Dejar registro de lo
> que funciona bien y mal, e ir mostrando cuando queda bien.

## Qué se verificó en vivo

- `tools/probar_gemini.py` → la clave responde (`OK`).
- Ingesta del RAG de Reiki en Redis y búsqueda en vivo.
- `langgraph dev` publica los 4 grafos; fichas configuradas; agentes responden por A2A.
- Coordinador enrutando a los 4 agentes + guardado de evidencias.
- Suite completa con el servidor arriba.
