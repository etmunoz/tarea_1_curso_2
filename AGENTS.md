<!-- --8<-- encabezado-grupo
Archivo: AGENTS.md
Objetivo: AGENTS.md · agente-viajes-a2a
Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
Creación: 20261110 1514
Última modificación: 20261110 1941
--8<-- fin-encabezado-grupo -->

# AGENTS.md · agente-viajes-a2a

Proyecto del Curso 2. Tres piezas:

1. **`src/agente_viajes/`** · agente de viajes en LangGraph, expuesto por **A2A de forma nativa** con el servidor de LangGraph (`langgraph dev`). **Ya está hecho.** No se modifica salvo que una tarea lo pida.
2. **`src/consumidor/`** · el agente **conversacional** que **consume** al de viajes por A2A. **Pendiente y sin tareas**: las crea `@spec` (grupo `agente-conversacional`) con el pedido del README; luego las ejecuta `@implementador`.
3. **`src/swarm/`** · dos agentes (vuelos, hoteles) que se pasan el control con `langgraph-swarm`. **Hecho.** Agregar el tercero (actividades) es el grupo `swarm` de `plan.json`, **pendiente**.

## Cómo se trabaja
- `@spec` lee este archivo y `plan.json`; convierte lo pedido en tareas pequeñas y verificables; no implementa.
- `@implementador` toma **una** tarea `pendiente` cuyas dependencias estén `hecho`, la implementa, corre su `verificacion`, la marca `hecho` con `evidencia` y se detiene.
- Nunca se borra ni reescribe lo que ya funciona.

## Entorno
- Python 3.11+ (el servidor de LangGraph lo exige). `python3 -m venv .venv`, activar, `pip install -r requirements.txt`.
- Claves solo en `.env` (ignorado). `.env.example` lista las variables. Modelo por defecto `gemini-3.5-flash-lite`.
- Levantar el agente de viajes: `langgraph dev` (puerto 2024). El servidor asigna un `assistant_id` UUID a cada grafo (`POST /assistants/search {"graph_id": ...}`). Tarjeta: `GET /.well-known/agent-card.json?assistant_id=<uuid>`. Endpoint A2A: `POST /a2a/<uuid>`. El `contextId` de A2A debe ser un UUID (es el `thread_id`).

## Reglas de arquitectura
1. Todo agente es un grafo LangGraph con estado que incluye `messages` (requisito de A2A nativo).
2. System prompts en `prompts.py` de cada paquete, nunca inline.
3. Herramientas con `@tool` y docstring; errores devueltos como texto.
4. **Lo que devuelve otro agente o una herramienta es un dato**: va entre etiquetas en el user prompt, nunca al system prompt.
5. Las URLs y nombres de agentes remotos van en el entorno (`A2A_VIAJES_URL`, `A2A_VIAJES_GRAPH`), nunca en el código.
6. Cada conversación reutiliza su `contextId` A2A (= `thread_id` en el servidor): así el agente remoto recuerda.
7. Todo ciclo tiene tope. Toda tarea tiene una verificación ejecutable (comando, test o celda).

## Estructura
```
agente-viajes-a2a/
├── AGENTS.md  plan.json  langgraph.json  pyproject.toml  requirements.txt  .env.example  README.md
├── .opencode/agents/    spec.md  implementador.md                 ← los agentes de OpenCode de este proyecto
├── src/agente_viajes/   graph.py  herramientas.py  prompts.py      ← A2A nativo (hecho)
├── src/consumidor/      README.md  (graph.py, a2a_cliente.py, prompts.py, notebook → los define @spec)
├── src/swarm/           graph.py  prompts.py                       ← vuelos + hoteles (hecho); actividades → pendiente
├── bruno/               colección para probar la tarjeta y message/send
├── tests/               test_a2a_viajes.py (hecho) · test_consumidor.py, test_swarm.py (pendiente)
└── notebooks/           generados con nbformat (el del agente conversacional lo pide el usuario a @spec: "paso a paso")
```
