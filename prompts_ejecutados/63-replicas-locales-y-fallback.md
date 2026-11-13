<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/63-replicas-locales-y-fallback.md`  
> **Objetivo:** 63 · Réplicas locales de los agentes del grupo + fallback local en el coordinador  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261113 1135 · **Última modificación:** 20261113 1135
<!--/encabezado-grupo-->

# 63 · Réplicas locales + fallback (remoto → local)

**Fecha:** 2026-11-13 · **Rama:** `integra-agentes-locales` (no se mergea a `main`)

Respuesta: [`../respuestas/63-replicas-locales-y-fallback.md`](../respuestas/63-replicas-locales-y-fallback.md)

## Instrucciones del usuario (textual, en orden)

1. > "necesito que repliques lo que hice yo con Tomas, lo que hizo Gustavo y lo que hizo Fabio. Tu
>    tienes las repo, así que deja esas también como respaldo local de lo que hicimos. Ojo con que no
>    todas las cosas podrás implementar en la máquina ya que es pequeña, por lo que lo que requiera de
>    un docker lo debes reemplazar por una solución local basada en algo alternativo que sea
>    extremadamente liviano."
2. Alcance (Q1): > "integra lo de Tomas, Gustavo y Fabio, como si fuera parte de la misma app, sólo
>    que cuando no esté la url de cloudflare, pueda responder el agente local de los tres."
3. > "si usa la mía" (GOOGLE_API_KEY) · "No" al swapfile · respaldo solo en ramas de mi repo (Mac/Windows).
4. > "debes ser evidente en la app del coordinador el uso del fallback, para que el usuario esté
>    consciente de qué se está utilizando, si el sitio real o el local."

## Qué se hizo

- **Ramas de respaldo** (`respaldo/gustavo`, `respaldo/fabio`): copia fiel de sus repos (sin `.git`).
- **Réplicas locales** como grafos de nuestro langgraph: `agente_meteorologo` (Gustavo), `agente_fabio`
  y `proteinman` (Fabio), portadas de sus repos (mismo stack), con ficha propia.
- **Tomás sin Docker**: RAG con backend local `InMemoryVectorStore` (sin Redis/Docker).
- **Fallback en el coordinador**: si el túnel remoto no responde y hay réplica local del grafo,
  responde la réplica local en proceso, marcando `origen=fallback_local`.
- **Evidencia en la UI**: el panel distingue 🌐 Remoto (sitio real) / 🏠 Local / 🏠 Fallback LOCAL,
  con color y un badge en la burbuja.
- Todo en la rama `integra-agentes-locales`; `main` intacto; nada nuevo al VPS.
