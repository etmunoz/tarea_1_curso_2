<!-- --8<-- encabezado-grupo
Archivo: respuestas/10-blueprint-y-coordinador.md
Objetivo: 10 · Respuesta — Blueprint + coordinador
Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
Creación: 20261110 1933
Última modificación: 20261110 1934
--8<-- fin-encabezado-grupo -->

# 10 · Respuesta — Blueprint + coordinador

Prompt: [`../prompts_ejecutados/10-blueprint-y-coordinador.md`](../prompts_ejecutados/10-blueprint-y-coordinador.md)

## Archivos creados

- `blueprint-ezequiel.md` — tabla del blueprint (quién soy, hace/no hace, herramientas, deriva a otro, dónde se ejecuta, dirección pública pendiente).
- `src/coordinador/a2a.py` — cliente A2A general (por `base_url` + `graph`): assistant_id, card, enviar.
- `src/coordinador/catalogo.py` — catálogo desde el entorno (`A2A_BASE`, `A2A_GRAFOS_LOCALES`, `URLS_AGENTES`); cada agente trae su ficha (Agent Card).
- `src/coordinador/prompts.py` — `SYSTEM_SUPERVISOR` (decide a quién enrutar o 'ninguno').
- `src/coordinador/graph.py` — StateGraph `enrutar` (with_structured_output `Decision`) → `consultar`/`sin_agente`; respuesta remota etiquetada `[Nombre] …`.
- `notebooks/coordinador_paso_a_paso.ipynb` — catálogo · supervisor · ronda.
- `tests/test_coordinador.py` — parse de catálogo y texto A2A (sin key) + grafo (skip sin key).
- `.env.example` — variables del coordinador. `plan.json` — grupo `coordinador` (k01–k03).

## Salida de la verificación

```text
$ uv run python -c "from src.coordinador.catalogo import construir_catalogo; print([(a.base_url,a.graph) for a in construir_catalogo()])"
[('http://127.0.0.1:2024', 'agente_viajes'), ('http://127.0.0.1:2024', 'agente_ezequiel')]

$ uv run pytest tests/test_coordinador.py -q
...s   →  3 passed, 1 skipped

$ uv run pytest -q      # suite completa
14 passed, 5 skipped
```

## Cómo probarlo en vivo (requiere GOOGLE_API_KEY)

```bash
uv run langgraph dev                     # publica agente_viajes y agente_ezequiel
uv run python -m src.coordinador.graph   # enruta: IA/DS→ezequiel, viajes→viajes, resto→ninguno
```

Para sumar compañeros: en `.env`, `URLS_AGENTES=https://<túnel>#<grafo>,...`.

## Estado

Blueprint ✅. Coordinador construido y verificado sin key 🟡 (falta corrida en vivo
y `compañeros.md`/evidencia del Paso 7).
