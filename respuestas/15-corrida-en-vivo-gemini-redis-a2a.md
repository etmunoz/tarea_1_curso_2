<!--encabezado-grupo-->
> **Archivo:** `respuestas/15-corrida-en-vivo-gemini-redis-a2a.md`  
> **Objetivo:** 15 · Respuesta — Corrida en vivo y correcciones  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2041 · **Última modificación:** 20261110 2136
<!--/encabezado-grupo-->

# 15 · Respuesta — Corrida en vivo y correcciones

Prompt: [`../prompts_ejecutados/15-corrida-en-vivo-gemini-redis-a2a.md`](../prompts_ejecutados/15-corrida-en-vivo-gemini-redis-a2a.md)

Registro de lo que falló y cómo quedó bien (orden cronológico de la corrida).

## Problemas encontrados y su solución

| # | Síntoma (MAL) | Causa | Solución (BIEN) |
|---|---------------|-------|-----------------|
| 1 | `402 RESOURCE_EXHAUSTED` al llamar a Gemini | proyecto sin saldo de prepago | el usuario agregó saldo → la clave responde |
| 2 | `find_dotenv() AssertionError` al correr `-` | `load_dotenv()` sin frame (stdin) | `tools/probar_gemini.py` usa `load_dotenv(RAIZ/".env")` |
| 3 | `No module named 'langchain_text_splitters'` | dependencia faltante | se agregó `langchain-text-splitters` al `pyproject.toml` |
| 4 | `404 NOT_FOUND models/text-embedding-004` | ese modelo no está en la clave | se cambió a `models/gemini-embedding-001` |
| 5 | fragmentos del RAG traían el encabezado de grupo | se indexaba el header del `.md` | `rag._sin_encabezado()` lo quita antes de trocear |
| 6 | coordinador: Reiki → `sin_agente` | Tomás no estaba en el catálogo local | se sumó `agente_tomas` a `A2A_GRAFOS_LOCALES` |
| 7 | `test_a2a_viajes::test_agent_card` falla | la ficha cambió el nombre de la tarjeta | el test ahora acepta nombre por defecto o de ficha |
| 8 | la ronda acumulaba la `ruta` entre preguntas | mismo `thread_id` para todas | `guardar_evidencias.py` usa un hilo nuevo por pregunta |
| 9 | ronda enruta a ciegas (nombres = id de grafo) | `langgraph dev` recargaba en caliente al editar | se reinició el servidor estable antes de la ronda |

## Resultado final (BIEN)

Clave:
```text
$ uv run python tools/probar_gemini.py
✓ Gemini respondió: 'OK'  ·  La API key funciona.
```

RAG de Reiki:
```text
$ uv run python tools/cargar_rag_reiki.py
✓ 9 fragmentos indexados.
$ buscar_reiki('símbolos del nivel 2') -> nivel-2-okuden.md: "...tres símbolos: Cho Ku Rei, Sei He Ki, Hon Sha Ze Sho Nen..."
```

Coordinador enrutando a los 4 agentes (ronda, `evidencias/05-ronda.md`):
```text
> ¿Qué técnica uso si tengo desbalance de clases?   -> [Agente de Ezequiel]
> ¿Qué símbolos se aprenden en el nivel 2 de Reiki? -> [Agente de Tomás]   (vía RAG)
> ¿Cuánto cuesta un pastel de choclo para 4?        -> [Agente de cocina chilena]
> ¿Cuánto cuesta un vuelo de Santiago a Lima?       -> [Agente de viajes]
> ¿Quién ganó el mundial de 1962?                   -> sin_agente (rechazado)
```

Suite completa con `langgraph dev` arriba:
```text
$ uv run pytest -q
36 passed, 1 skipped
```
(el único skipped es el test de degradación del RAG, que se salta porque Redis está arriba.)

## Evidencias generadas (automáticas)

- `evidencias/02-ficha-agente_{ezequiel,tomas,viajes,cocina}.json` — Agent Cards reales.
- `evidencias/04-catalogo.txt` — catálogo del coordinador con las 4 fichas.
- `evidencias/05-ronda.md` — la ronda enrutando a cada agente.

Quedan manuales (capturas de pantalla): `01-saltos.png` y `03-tunel.png`.

## Estado

Todo funciona end-to-end en vivo (Gemini + Redis + A2A + coordinador). Pendiente solo
la prueba entre los 2 computadores (guia_ezequiel_tomas.md) y las 2 capturas manuales.
