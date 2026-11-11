<!--encabezado-grupo-->
> **Archivo:** `respuestas/13-conocimiento-sqlite-y-rag.md`  
> **Objetivo:** 13 · Respuesta — Conocimiento SQLite (Ezequiel) y RAG Redis (Tomás)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2009 · **Última modificación:** 20261111 0835
<!--/encabezado-grupo-->

# 13 · Respuesta — Conocimiento SQLite (Ezequiel) y RAG Redis (Tomás)

Prompt: [`../prompts_ejecutados/13-conocimiento-sqlite-y-rag.md`](../prompts_ejecutados/13-conocimiento-sqlite-y-rag.md)

## Parte 1 · Ezequiel — BD SQLite de modelos

- `src/agente_ezequiel/bd_modelos.py` — crea/puebla `data/modelos_ds.sqlite` (se crea
  sola la 1ª vez). Tabla `modelos` con columnas: nombre, tipo, para_que, como_se_utiliza,
  librerias, ejemplo_python. **21 modelos**: 9 supervisados, 7 no supervisados, 5 de refuerzo.
- Tool `consultar_modelos(consulta, tipo)` en `herramientas.py` (conectada al agente).
- `tests/test_bd_modelos.py` (5 pruebas, sin key).

```text
$ consultar_modelos(tipo='refuerzo') -> Q-Learning, SARSA, DQN, PPO, A2C
$ consultar_modelos(consulta='xgboost')[0] -> Gradient Boosting (XGBoost) · from xgboost import XGBClassifier...
```

## Parte 2 · Tomás — RAG de Reiki con Redis dockerizado

- `data/reiki/` — documentos **originales** (síntesis propia) de niveles 1-4 + `FUENTES.md`
  (con los enlaces de las fuentes consultadas). El profesor puede añadir sus PDFs y recargar.
- `src/agente_tomas/rag.py` — Redis como vector store (`langchain-redis`), embeddings Gemini,
  `cargar()` (trocea e indexa) y `buscar()` (recupera k fragmentos). Imports pesados tardíos.
- `tools/cargar_rag_reiki.py` — ingesta desde CLI.
- `docker-compose.yml` — Redis Stack local (`REDIS_URL` cambiable por el Redis remoto del profesor).
- Tool `buscar_reiki` en `herramientas.py` (conectada al agente); degrada con nota si no hay Redis/clave.
- `.env.example` con `REDIS_URL`, `REDIS_INDEX`, `MODELO_EMBEDDINGS`. `tests/test_rag_tomas.py`.

```text
$ docker compose up -d && python -c "from src.agente_tomas import rag; print(rag.disponible())"  → True
$ buscar_reiki(...) sin GOOGLE_API_KEY -> {'nota': 'No pude consultar el RAG: ... API key required ...'}  (degrada)
```

## Salida de la verificación

```text
$ uv run pytest -q
27 passed, 5 skipped
```

(Los 5 skipped requieren `GOOGLE_API_KEY`/`langgraph dev`.)

## Para usar el RAG en vivo

```bash
docker compose up -d                       # Redis local
# en .env: GOOGLE_API_KEY=...   (y REDIS_URL si usas uno remoto)
uv run python tools/cargar_rag_reiki.py    # indexa data/reiki/
uv run langgraph dev                       # Tomás ya responde con buscar_reiki
```

## Nota sobre los documentos

No se redistribuyen manuales con copyright: `data/reiki/nivel-*.md` son síntesis
original con las fuentes citadas en `FUENTES.md`. El profesor puede reemplazarlos por
sus propios documentos (incluye `.pdf`) y recargar el índice.

## Estado

SQLite de Ezequiel ✅ (verificado). RAG de Tomás ✅ implementado y Redis arriba 🟡
(falta la ingesta en vivo, que requiere `GOOGLE_API_KEY`).
