<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/13-conocimiento-sqlite-y-rag.md`  
> **Objetivo:** 13 · Conocimiento conectado: SQLite (Ezequiel) y RAG Redis (Tomás)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2009 · **Última modificación:** 20261111 0829
<!--/encabezado-grupo-->

# 13 · Conocimiento conectado: SQLite (Ezequiel) y RAG Redis (Tomás)

**Fecha:** 2026-11-10

## Prompt

> 1. A Ezequiel: conéctale una tool que use una BD SQLite con modelos de ciencia de
>    datos (supervisados, no supervisados y refuerzo), con columnas: para qué sirve,
>    cómo se utiliza, librerías requeridas y ejemplo de uso en Python. Implementa el
>    acceso a ese conocimiento en SQLite.
> 2. A Tomás: conéctale un RAG con un Redis local dockerizado (que el profesor pueda
>    cambiar por su Redis remoto) con documentos de Reiki. Busca en internet documentos
>    de Reiki niveles 1-4, déjalos en una carpeta para cargarlos al RAG, e implementa el
>    acceso a ese conocimiento. Todo documentado.

## Verificación pedida

- SQLite de modelos creada/poblada sola; `consultar_modelos` (tipo + texto) devuelve las columnas.
- Documentos de Reiki (niveles 1-4) en `data/reiki/`; RAG con Redis dockerizado (`REDIS_URL` cambiable); `buscar_reiki` recupera fragmentos y degrada sin Redis/clave.
- Tests sin key/servidor en verde.
