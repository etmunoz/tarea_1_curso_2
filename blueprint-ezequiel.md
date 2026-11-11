<!--encabezado-grupo-->
> **Archivo:** `blueprint-ezequiel.md`  
> **Objetivo:** Blueprint · Agente de Ezequiel  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1933 · **Última modificación:** 20261111 1741
<!--/encabezado-grupo-->

# Blueprint · Agente de Ezequiel

| Qué definir | Mi agente |
|-------------|-----------|
| Quién soy | Ezequiel · IA Engineer y Data Scientist |
| Hace | Recomienda técnicas de ML/Data Science para un problema, qué métricas mirar y qué modelo elegir según el tipo de dato. |
| No hace | No programa por ti, no gestiona infraestructura ni entrena modelos reales; no responde temas fuera de IA/Data Science. |
| Herramientas | `recomendar_tecnica(problema)`, `metricas_recomendadas(tipo_problema)`, `elegir_modelo(tipo_de_dato)` — datos simulados dentro de `src/agente_ezequiel/herramientas.py`. |
| Decide solo | Qué herramienta usar y qué recomendar, a partir de lo que devuelven las herramientas. |
| Nunca sin persona | No toma decisiones de negocio ni ejecuta cambios; solo recomienda. |
| Deriva a otro | Cuando la pregunta es de vuelos/hoteles/actividades → lo dice en una frase y no responde (eso es del agente de viajes / swarm). |
| Dónde se ejecuta | `http://127.0.0.1:2024` (A2A nativo de `langgraph dev`) · grafo `agente_ezequiel` · `src/agente_ezequiel/` |
| Dirección pública | (se completa en el Paso 6 con la URL del túnel de Cloudflare) |

## Herramientas · de dónde salen los datos

- `recomendar_tecnica`: catálogo `TECNICAS` (problema → técnica + por qué). Hoy simulado; mañana podría salir de una guía interna o un tracking de experimentos (MLflow / W&B).
- `metricas_recomendadas`: catálogo `METRICAS` (tipo de problema → métricas).
- `elegir_modelo`: catálogo `MODELOS` (tipo de dato → modelo de arranque + nota).

Si piden algo fuera del catálogo, la herramienta responde en una línea con lo que sí cubre; nunca lanza un error.
