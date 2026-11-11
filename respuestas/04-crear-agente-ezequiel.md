<!--encabezado-grupo-->
> **Archivo:** `respuestas/04-crear-agente-ezequiel.md`  
> **Objetivo:** 01 · Respuesta — Crear el agente de Ezequiel  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1603 · **Última modificación:** 20261111 1410
<!--/encabezado-grupo-->

# 01 · Respuesta — Crear el agente de Ezequiel

Prompt: [`../prompts_ejecutados/04-crear-agente-ezequiel.md`](../prompts_ejecutados/04-crear-agente-ezequiel.md)

## Archivos creados / modificados

- `src/agente_ezequiel/__init__.py`
- `src/agente_ezequiel/herramientas.py` — `recomendar_tecnica`, `metricas_recomendadas`, `elegir_modelo` (datos simulados; emparejado sin acentos y por raíz de palabra).
- `src/agente_ezequiel/prompts.py` — `SYSTEM_EZEQUIEL`.
- `src/agente_ezequiel/graph.py` — `create_agent` con Gemini, `name="agente_ezequiel"`.
- `langgraph.json` — registrado el grafo `agente_ezequiel`.
- `tests/test_agente_ezequiel.py` — 5 pruebas (sin API key).

## Salida de la verificación

Herramientas (sin API key):

```text
recomendar_tecnica('desbalance de clases') -> {'problema': 'desbalance de clases', 'tecnica': 'class weights, resampleo (SMOTE/undersampling) y métricas tipo F1/PR-AUC', 'por_que': 'la accuracy engaña con clases raras; hay que reponderar y medir sobre la minoritaria'}
metricas_recomendadas('regresion')        -> {'tipo': 'regresion', 'metricas': ['MAE', 'RMSE', 'R²', 'MAPE (si no hay ceros)']}
elegir_modelo('texto')                     -> {'tipo': 'texto', 'modelo': 'embeddings (sentence-transformers) + clasificador, o un LLM para tareas generativas/abiertas', 'nota': 'empieza por embeddings; sube a LLM solo si la tarea lo pide'}
desconocido                                -> {'nota': 'No tengo una técnica catalogada para «cómo hago un asado». Puedo ayudar con: pocos datos, overfitting, ...'}
```

Registro en `langgraph.json`:

```json
"graphs": {
  "agente_viajes": "./src/agente_viajes/graph.py:graph",
  "agente_ezequiel": "./src/agente_ezequiel/graph.py:graph"
}
```

Pruebas:

```text
$ uv run pytest tests/test_agente_ezequiel.py -q
.....                                                                    [100%]
5 passed in 0.21s
```

## Cómo probarlo en vivo (requiere GOOGLE_API_KEY)

```bash
cp .env.example .env          # pega tu GOOGLE_API_KEY
uv run langgraph dev          # publica agente_viajes y agente_ezequiel en :2024

# en otra terminal: assistant_id del agente y un message/send A2A
AID=$(curl -s -X POST http://127.0.0.1:2024/assistants/search -H "Content-Type: application/json" -d '{"graph_id":"agente_ezequiel"}' | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['assistant_id'])")
CTX=$(python3 -c "import uuid; print(uuid.uuid4())")
curl -s -X POST "http://127.0.0.1:2024/a2a/$AID" -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":\"1\",\"method\":\"message/send\",\"params\":{\"message\":{\"role\":\"user\",\"messageId\":\"m1\",\"contextId\":\"$CTX\",\"parts\":[{\"kind\":\"text\",\"text\":\"¿Qué técnica uso si tengo desbalance de clases?\"}]}}}"
```

## Estado

Agente creado y verificado sin API key. Falta la prueba en vivo con Gemini (cuando cargues tu `GOOGLE_API_KEY`).
