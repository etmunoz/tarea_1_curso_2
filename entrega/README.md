# Grupo ⟨GRUPO⟩ · Taller 05 · Crea tu agente y ponlo a conversar por A2A

## Contexto
El taller pide transformar el proyecto base `agente-viajes-a2a` en un agente especialista propio, probarlo desde un notebook y hacerlo conversar por el protocolo **A2A (Agent2Agent)** con un segundo agente. Elegimos un caso de **bioinformática**: diseñar un flujo para clasificar proteínas por familia funcional. Hacen falta dos especialidades:

| Agente | Especialidad | Autor | Carpeta · puerto · grafo |
|---|---|---|---|
| **Agente Fabio** | Bioinformática: conceptos, herramientas y bases de datos (BLAST, UniProt, NCBI), pipelines reproducibles | Fabio Durán Verdugo | `mi-agente/` · 2025 · `agente_fabio` |
| **ProteinMAN** | IA y Data Science aplicada a bioinformática: técnica, métricas y modelo según el dato biológico | Fabio Durán Verdugo | `segundo-agente/` · 2026 · `proteinman` |

Cada agente es un grafo ReAct de LangGraph con Gemini, publicado por A2A de forma nativa con `langgraph dev`. Un **supervisor** (Gemini con salida estructurada) lee las tarjetas A2A de los dos agentes y decide a cuál enviar cada pregunta. Los agentes también conversan entre sí en tres turnos (A → B → A).

El comportamiento de cada agente está escrito en su `prompts.py` como **requisitos funcionales (RF)** y **no funcionales (RNF)** con identificadores estables, que se citan en los blueprints y en el documento de entrega.

## Integrantes
| Nombre | Aporte en este taller |
|---|---|
| Fabio Durán Verdugo | Creador de los dos agentes: Agente Fabio y ProteinMAN (blueprints, especificación por requisitos, herramientas y grafos). Notebooks `a2a-test.ipynb` (reconstrucción), pruebas, ajustes y documento de entrega. |
| Ezequiel Muñoz | ⟨APORTE EZEQUIEL⟩ |
| Gustavo Reyes | ⟨APORTE GUSTAVO⟩ |

## Origen del segundo agente
`segundo-agente/` contiene ProteinMAN, creado por Fabio Durán Verdugo a partir del agente de IA y Data Science del repositorio del grupo `tarea_1_curso_2` (`src/agente_ezequiel/`). Se pasó al formato `agente-viajes-a2a` y se adaptó a ML aplicado a bioinformática. Cada cambio está en `segundo-agente/README.md`.

## Contenido del zip
| Ruta | Qué es |
|---|---|
| `documento-entrega.ipynb` | Identificación, blueprint, requisitos, evidencias de cada etapa, ajustes, reto, conversación y comentarios. |
| `blueprint.md` | Blueprint del Agente Fabio, con su tabla de requisitos. |
| `mi-agente/` | Proyecto completo `agente-viajes-a2a` con el Agente Fabio, sin `src/swarm/`. `notebooks/a2a-test.ipynb` va ejecutado (etapas 2 y 3). |
| `segundo-agente/` | Proyecto completo con ProteinMAN y su `blueprint.md`. `notebooks/a2a-test.ipynb` va ejecutado y actualiza su tarjeta. |
| `preguntar.py` | Cliente de terminal: pregunta a un agente por A2A o deja que el supervisor elija. El `contextId` siempre es un UUID. |

Ninguna carpeta incluye `.env`, `.venv` ni `.langgraph_api`. Cada proyecto trae su `.env.example`.

## Cómo ejecutar
```bash
# 1. En mi-agente/ y en segundo-agente/ (Python 3.11 o superior; se probó con 3.13)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # pegar GOOGLE_API_KEY

# 2. Dos terminales
cd mi-agente      && langgraph dev --port 2025
cd segundo-agente && langgraph dev --port 2026

# 3. Notebooks (en este orden)
#    segundo-agente/notebooks/a2a-test.ipynb  → actualiza la tarjeta «ProteinMAN»
#    mi-agente/notebooks/a2a-test.ipynb       → etapas 2 y 3: preguntas, A2A, supervisor y conversación

# 4. (opcional) Preguntar desde la terminal, con los servidores arriba
python preguntar.py fabio "¿Qué diferencia hay entre FASTA y FASTQ?"
python preguntar.py proteinman "¿Qué modelo uso para clasificar secuencias de proteínas?"
python preguntar.py supervisor "Tengo lecturas FASTQ con baja calidad, ¿cómo las reviso?"
python preguntar.py fabio "Mi gen favorito es BRCA1" --hilo mi-proyecto     # conversación con memoria
python preguntar.py fabio "¿Cuál es mi gen favorito?" --hilo mi-proyecto
python preguntar.py fabio "Hola" --url https://xxxx.trycloudflare.com      # a través de un túnel
```
