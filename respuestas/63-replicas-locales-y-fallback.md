<!--encabezado-grupo-->
> **Archivo:** `respuestas/63-replicas-locales-y-fallback.md`  
> **Objetivo:** 63 · Respuesta — Réplicas locales + fallback (remoto→local) + Tomás sin Docker  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261113 1135 · **Última modificación:** 20261113 1135
<!--/encabezado-grupo-->

# 63 · Respuesta — Réplicas locales + fallback

Prompt: [`../prompts_ejecutados/63-replicas-locales-y-fallback.md`](../prompts_ejecutados/63-replicas-locales-y-fallback.md)

> **Todo en la rama `integra-agentes-locales`.** `main` queda intacto (la entrega no cambia) y **nada
> nuevo se desplegó al VPS**. Ramas pusheadas a GitHub para que Windows las tenga al actualizar.

## 1 · Ramas de respaldo (fiel, sin `.git`)

- **`respaldo/gustavo`** ← `github.com/guswolf-007/taller_A2A_uai` @d2565cb
- **`respaldo/fabio`** ← `gitlab.com/fabioduran/taller_agentes2` @fb5602a

Creadas con worktrees aislados (no tocaron `main`). Cada una trae un `RESPALDO.md` con el origen.

## 2 · Réplicas locales (grafos de nuestro langgraph)

Portadas de sus repos (mismo stack `create_agent` + Gemini + langgraph) a `src/`, registradas en
`langgraph.json` y con ficha en `src/fichas.py`:

| Grafo | Origen | Herramientas |
|---|---|---|
| `agente_meteorologo` | Gustavo | `pronostico_hoy`, `pronostico_semana` (Santiago/Concepción/Valdivia) |
| `agente_fabio` | Fabio | `consultar_mis_apuntes` (bioinformática) |
| `proteinman` | Fabio | `recomendar_tecnica`, `metricas_recomendadas`, `elegir_modelo`, `consultar_modelos` (SQLite) |

Smoke-test con nuestra `GOOGLE_API_KEY`: los tres responden correcto (clima de Valdivia; FASTA/FASTQ
desde apuntes; métricas de desbalance + deriva la biología a Fabio).

## 3 · Tomás sin Docker (RAG local ultraliviano)

`src/agente_tomas/rag.py`: dos backends por `RAG_BACKEND`:
- **local** (default en la rama): `InMemoryVectorStore` de `langchain-core` (sin servidor, sin Docker),
  embeddings Gemini calculados una vez y **persistidos** a `logs/reiki_rag.json`. `buscar_reiki`
  construye el índice la primera vez.
- **redis**: se mantiene para el profesor (`RAG_BACKEND=redis`).

Probado end-to-end: Tomás responde citando los documentos, sin Redis.

## 4 · Fallback local en el coordinador

`src/coordinador/graph.py` (nodo `consultar`): si el agente es **remoto** y su `preguntar()` lanza
`ErrorA2A` (túnel caído), y existe réplica local del mismo grafo, se invoca **en proceso**
(`src.<grafo>.graph`) y se responde con ella, marcando `origen='fallback_local'` y
`ruta=[…, 'agente_remoto', 'fallback_local', …]`.

`src/coordinador/catalogo.py`: para que el supervisor **pueda** elegir un remoto caído (y así
disparar el fallback), `nombre`/`descripcion` caen a la **ficha local** (`src/fichas.py`) cuando el
remoto nunca se descubrió, y `texto_catalogo` lo marca elegible ("responderá la réplica LOCAL").

### Evidencia en la UI (`tools/coordinador_web.py`)
El panel "Antecedentes del acceso" ahora muestra la **Fuente** con color:
- 🌐 **Remoto (sitio real)** (verde) · 🏠 **Local (este servidor)** (azul) · 🏠 **Fallback LOCAL**
  (ámbar) — con el remoto que se **intentó** (host/IP) cuando hubo fallback.
Además, un **badge ámbar en la burbuja** del chat: «🏠 Respondió la réplica LOCAL (el remoto no estaba
disponible)».

### Verificación (local, con un remoto caído a propósito)
```
Q: ¿Qué clima hay hoy en Valdivia?   (URLS_AGENTES=<url-muerta>#agente_meteorologo)
  elegido: agente_meteorologo | origen: fallback_local
  ruta: guardia_entrada → supervisor → agente_remoto → fallback_local → guardia_salida
  resp: [agente_meteorologo] Hoy en Valdivia hay lluvia intermitente…   (la réplica local)

Q: ¿qué recetas chilenas tienes?     -> origen: local
```

## 5 · Tests

`pytest` → **149 passed, 1 skipped**. Se actualizaron 2 tests de resiliencia (un agente **sin**
réplica local sigue dando el estado controlado "no disponible") y se agregó
`test_consultar_hace_fallback_local`.

## Archivos (en la rama)

- `src/agente_meteorologo/*`, `src/agente_fabio/*`, `src/proteinman/*` (réplicas) + `langgraph.json` + `src/fichas.py`.
- `src/agente_tomas/rag.py`, `src/agente_tomas/herramientas.py` (RAG local).
- `src/coordinador/graph.py`, `src/coordinador/catalogo.py` (fallback), `tools/coordinador_web.py` (UI).
- `tests/test_resiliencia_a2a.py`.
- Ramas `respaldo/gustavo`, `respaldo/fabio`.

## Cómo validarlo (local, sin tocar el VPS)

1. `git checkout integra-agentes-locales` · `uv sync`.
2. `RAG_BACKEND=local uv run langgraph dev` (publica los 7 grafos).
3. Levantar el coordinador web con una URL **muerta** en algún agente (⚙️) y preguntarle su tema →
   verás el badge y la **Fuente: 🏠 Fallback LOCAL** en el panel.

## Pendientes

- Es una rama de respaldo/experimento: **no** se mergea a `main` ni se despliega al VPS (decisión del
  usuario: mínimo en el VPS).
- Fabio sigue completando su repo; `respaldo/fabio` es la foto `@fb5602a`.
