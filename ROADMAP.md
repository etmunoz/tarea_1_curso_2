<!--encabezado-grupo-->
> **Archivo:** `ROADMAP.md`  
> **Objetivo:** ROADMAP · Taller A2A (Curso 2 · Sesión 1)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1928 · **Última modificación:** 20261111 1957
<!--/encabezado-grupo-->

# ROADMAP · Taller A2A (Curso 2 · Sesión 1)

Todo lo que hay que hacer, desde el principio, para completar la tarea
**"tu skill es un agente y habla por A2A"**. El contenido del taller (10 páginas)
está en [`taller-a2a/`](taller-a2a/index.md).

**Leyenda de estado:** ✅ hecho · 🟡 parcial (falta la corrida en vivo) · ⬜ pendiente

## Nota importante: taller vs. base real

El **texto del taller** describe un molde anterior: cada agente con su `server.py`
expuesto por `uvicorn` en `:8003`, una ficha hecha con `crear_tarjeta`, un
`coordinador` en `:8002` con `URLS_AGENTES`, y comandos `python main.py NOMBRE`.

El **proyecto base real** que bajamos (`agente-viajes-a2a`) usa la versión más
nueva: A2A **nativo** con `langgraph dev` (`:2024`), la Agent Card la **publica el
servidor** (se ajusta con `PATCH /assistants/<id>` o `a2a-sdk`), y los grafos se
registran en `langgraph.json`. Este roadmap sigue el **stack real** y traduce cada
paso del taller a él.

---

## Fase 0 · Entorno y base  ✅

| # | Qué | Estado | Dónde |
|---|-----|--------|-------|
| 0.1 | Repo + material del taller en Markdown | ✅ | `taller-a2a/`, prompts `01`–`02` |
| 0.2 | Proyecto base con uv + Python 3.13, dependencias | ✅ | `pyproject.toml`, `uv.lock`, prompt `03` |
| 0.3 | Agente de viajes (A2A nativo) · molde | ✅ | `src/agente_viajes/`, `langgraph.json` |
| 0.4 | Swarm vuelos + hoteles + **actividades** | ✅ | `src/swarm/`, prompt `07` |
| 0.5 | Agente conversacional (consume viajes por A2A) | ✅ | `src/consumidor/`, prompt `05` |
| 0.6 | Regla de encabezado de archivos del grupo | ✅ | `CONVENCIONES.md`, `tools/aplicar_encabezados.py`, prompt `06` |
| 0.7 | Registro de prompts (secuencia desde el inicio) | ✅ | `prompts_ejecutados/`, `respuestas/` |

---

## Fase 1 · Tu agente (Parte 1 del taller, pasos 1–5)

| # | Paso del taller | Qué entrega | Estado | Dónde / Nota |
|---|-----------------|-------------|--------|--------------|
| 1.1 | **Paso 2 · Blueprint** | `blueprint-ezequiel.md` (qué hace / qué no / herramienta) | ✅ | [`blueprint-ezequiel.md`](blueprint-ezequiel.md) |
| 1.2 | **Paso 3 · Mi agente con mi skill** | `src/agente_ezequiel/` (herramientas, prompt, grafo) + registro | ✅ | `src/agente_ezequiel/`, `langgraph.json`, prompt `04` |
| 1.3 | **Paso 4 · Probarlo solo** | el agente responde y rechaza lo ajeno; evidencia | 🟡 | tests ✅ (`tests/test_agente_ezequiel.py`); falta captura en vivo (`langgraph dev` + `GOOGLE_API_KEY`) |
| 1.4 | **Paso 4 · Notebook paso a paso** | notebook nbformat | ✅ | `notebooks/ezequiel_paso_a_paso.ipynb` |
| 1.5 | **Paso 5 · La ficha (Agent Card)** | descripción "sé/no hago"; `evidencias/02-ficha-<grafo>.json` | ✅ | aplicada en vivo; 4 fichas guardadas en `evidencias/` |

---

## Fase 2 · Internet (Parte 2 del taller, paso 6)

| # | Paso del taller | Qué entrega | Estado | Dónde / Nota |
|---|-----------------|-------------|--------|--------------|
| 2.1 | **Paso 6 · Salir a internet con Cloudflare** | túnel https a tu agente; `evidencias/03-tunel.png` | ⬜ | `cloudflared tunnel --url http://127.0.0.1:2024`. Compartir en el chat: `Ezequiel · IA/Data Science · https://…` |

---

## Fase 3 · Hablar entre agentes (Parte 3 del taller, pasos 7–9)

| # | Paso del taller | Qué entrega | Estado | Dónde / Nota |
|---|-----------------|-------------|--------|--------------|
| 3.1 | **Paso 7 · Sumar a los compañeros** | un **coordinador/supervisor** que lee las fichas y enruta; `compañeros.md`; `evidencias/04-catalogo.png` | 🟡 | ✅ construido: [`src/coordinador/`](src/coordinador/) (catálogo desde `URLS_AGENTES`, supervisor LangGraph). Falta corrida en vivo + `compañeros.md`/evidencia. |
| 3.2 | **Paso 8 · La ronda de preguntas** | 3 preguntas por integrante con su camino; `evidencias/05-ronda.png` | ⬜ | Actividad en vivo con los agentes del grupo (Fabio, Gustavo, Ezequiel) sumados al coordinador. |
| 3.3 | **Paso 9 · Entrega y evaluación** | zip del grupo: documento, blueprints, `companeros.md`, proyecto completo, `evidencias/` | 🟡 | ✅ esqueleto: `entrega/documento-entrega.md`, `entrega/companeros.md`, `evidencias/README.md` y `tools/empaquetar_entrega.py` (arma el zip con `git ls-files`, sin `.env`). Falta completar ⟨pendiente⟩, PNGs y exportar el PDF. |

---

## Fase 3.bis · Prueba 2 computadores (Ezequiel Mac ↔ Tomás Windows)

| # | Qué | Estado | Dónde |
|---|-----|--------|-------|
| B.1 | **Agente Tomás** (Maestro Reiki) | ✅ | `src/agente_tomas/`, registrado en `langgraph.json` |
| B.2 | **Fichas** de Ezequiel y Tomás | 🟡 | `src/fichas.py`, `tools/configurar_fichas.py` (aplicar en vivo) |
| B.3 | **Guardar evidencias** (catálogo, ronda, fichas) | 🟡 | `tools/guardar_evidencias.py` |
| B.4 | **Guía end-to-end + scripts** Mac/Windows | ✅ | `guia_ezequiel_tomas.md`, `scripts/*.sh` y `*.ps1` |
| B.5 | **Corrida real entre tus 2 equipos** | ⬜ | ejecutar la guía con `GOOGLE_API_KEY` + túneles |

---

## Conocimiento conectado (prompt 13)

| # | Qué | Estado | Dónde |
|---|-----|--------|-------|
| C.1 | **Ezequiel · BD SQLite** de modelos (sup./no sup./refuerzo) + `consultar_modelos` | ✅ | `src/agente_ezequiel/bd_modelos.py` |
| C.2 | **Tomás · RAG Reiki** (Redis dockerizado) + `buscar_reiki` + docs niveles 1-4 | ✅ | `src/agente_tomas/rag.py`, `data/reiki/`; ingesta en vivo OK (9 fragmentos), buscar_reiki responde |
| C.3 | **Agente de cocina chilena** · ~20 recetas + costeo SQLite (`costear_receta`) | ✅ | `src/agente_cocina/` |

---

## Fase 4 · Verificación en vivo (transversal)

| # | Qué | Estado | Nota |
|---|-----|--------|------|
| 4.1 | `cp .env.example .env` + GOOGLE_API_KEY | ✅ | clave con saldo; probar_gemini.py → OK |
| 4.2 | `uv run langgraph dev` publica los 4 agentes | ✅ | corrida en vivo OK (prompt 15) |
| 4.3 | Correr los notebooks de arriba abajo (ezequiel, consumidor, swarm) | ⬜ | Sirve de evidencia del Paso 4. |
| 4.4 | `uv run pytest` con langgraph dev | ✅ | 36 passed, 1 skipped (prompt 15) |

---

## Extra (Paso 10 · no se evalúa)

- Datos reales en una herramienta (en vez del catálogo simulado).
- Un segundo agente tuyo con otra especialidad.
- Que un compañero ponga tu URL en su coordinador y te pregunte desde su equipo.

---

## Próximo paso sugerido

1. **Blueprint** (`1.1`) — rápido y es la base de la ficha.
2. **Prueba en vivo** (`4.1`–`4.4`) cuando tengas `GOOGLE_API_KEY`.
3. **Ficha** (`1.5`) y **túnel** (`2.1`).
4. **Coordinador/supervisor** (`3.1`) — es la pieza grande que falta para la Parte 3.
5. **Empaquetado de entrega** (`3.3`).
