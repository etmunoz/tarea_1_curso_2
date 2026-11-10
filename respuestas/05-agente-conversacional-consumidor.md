<!--encabezado-grupo-->
> **Archivo:** `respuestas/05-agente-conversacional-consumidor.md`  
> **Objetivo:** 05 · Respuesta — Agente conversacional (consumidor)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1629 · **Última modificación:** 20261110 2013
<!--/encabezado-grupo-->

# 05 · Respuesta — Agente conversacional (consumidor)

Prompt: [`../prompts_ejecutados/05-agente-conversacional-consumidor.md`](../prompts_ejecutados/05-agente-conversacional-consumidor.md)

## Archivos creados / modificados

- `src/consumidor/a2a_cliente.py` — cliente A2A: `assistant_id()`, `agent_card()`,
  `nuevo_context_id()`, `enviar_mensaje(texto, context_id)` (con extractor del texto
  de la respuesta A2A). URLs desde `.env` (`A2A_VIAJES_URL`, `A2A_VIAJES_GRAPH`).
- `src/consumidor/herramientas.py` — `consultar_agente_viajes` (remota) y `precio_btc`
  (local), + mapeo `thread_id → contextId` fijo. Importable sin API key.
- `src/consumidor/prompts.py` — `SYSTEM_CONSUMIDOR`.
- `src/consumidor/graph.py` — `create_agent` (Gemini, `messages`, `InMemorySaver`), demo `__main__`.
- `notebooks/consumidor_paso_a_paso.ipynb` — 3 secciones (config base · agentes · consumo).
- `tests/test_consumidor.py` — precio_btc, contextId estable, A2A (skip si no hay servidor).
- `plan.json` — grupo `agente-conversacional` con tareas `c01`, `c02`, `c03` (hecho).

## Salida de la verificación

```text
$ uv run pytest tests/test_consumidor.py -q
...s                                                                     [100%]
3 passed, 1 skipped in 0.51s

$ uv run pytest -q          # suite completa, sin langgraph dev
ss........s                                                              [100%]
8 passed, 3 skipped in 0.32s

$ uv run python -c "import nbformat; nb=nbformat.read('notebooks/consumidor_paso_a_paso.ipynb',4); nbformat.validate(nb); print('válido', len(nb.cells))"
válido 8

$ uv run python -c "from src.consumidor import a2a_cliente; print(a2a_cliente.BASE, a2a_cliente.GRAPH)"
http://127.0.0.1:2024 agente_viajes
```

(Los 3 tests saltados son los que necesitan `langgraph dev`: 2 del agente de viajes y 1 del A2A del consumidor.)

## Cómo probarlo en vivo (requiere GOOGLE_API_KEY + langgraph dev)

```bash
cp .env.example .env            # pega tu GOOGLE_API_KEY
uv run langgraph dev            # terminal 1 · publica agente_viajes en :2024
uv run python -m src.consumidor.graph   # terminal 2 · demo conversacional
# o abre notebooks/consumidor_paso_a_paso.ipynb y córrelo de arriba abajo
uv run pytest tests/test_consumidor.py  # ahora el test A2A deja de saltarse
```

## Estado

Hecho y verificado sin API key. Falta la prueba en vivo (Gemini + `langgraph dev`).
