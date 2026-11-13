# Taller 05 · Agentes especialistas que conversan por A2A

**Curso:** Agentes de IA · Curso 2 · Taller 05 «Mi agente especialista habla por A2A»
**Grupo ⟨GRUPO⟩:** Fabio Durán Verdugo · Gustavo Reyes · Ezequiel Muñoz

## Contexto
Este directorio tiene la solución completa del taller y las herramientas que se usaron para probarla y compartirla. El enunciado está en `docs/05-taller-mi-agente-especialista-habla-por-a2a.html`.

**El problema.** Un solo agente generalista responde peor que varios especialistas bien delimitados. El taller pide:
1. construir un agente especialista a partir del proyecto base `agente-viajes-a2a`;
2. publicarlo con el protocolo **A2A (Agent2Agent)**;
3. hacerlo colaborar con un segundo especialista, tanto a través de un supervisor que enruta preguntas como en una conversación directa entre los dos agentes.

**El caso.** Clasificar proteínas por familia funcional a partir de datos de UniProt. Necesita dos especialidades:

| Agente | Especialidad | Autor | Puerto · grafo |
|---|---|---|---|
| **Agente Fabio** | Bioinformática: conceptos, herramientas y bases de datos, pipelines reproducibles | Fabio Durán Verdugo | 2025 · `agente_fabio` |
| **ProteinMAN** | IA y Data Science aplicada a bioinformática: técnica, métricas y modelo | Fabio Durán Verdugo | 2026 · `proteinman` |

**Arquitectura.**
- Cada agente es un grafo ReAct (LangChain/LangGraph + Gemini) que sirve `langgraph dev`. Ese servidor publica de forma nativa la tarjeta A2A (`/.well-known/agent-card.json?assistant_id=…`) y el endpoint `/a2a/<assistant_id>`.
- Un supervisor (Gemini con salida estructurada) lee las tarjetas y elige a qué agente enviar cada pregunta, o responde «ninguno».
- Para compartir los agentes con el curso se usan túneles de Cloudflare. Hay también un puente opcional que publica cada agente como un servicio A2A «clásico».

**Especificación.** Los prompts de los dos agentes están escritos como **requisitos funcionales (RF)** y **no funcionales (RNF)** con identificadores estables, en `entrega/*/src/agente_viajes/prompts.py`. Los blueprints y el documento de entrega los citan por su ID, y las pruebas del notebook comprueban requisitos concretos, por ejemplo la derivación (RF-05) o la trazabilidad (RNF-02).

## Estructura
```
taller1/
├── README.md               este archivo (contexto y uso)
├── requirements.txt        dependencias de las herramientas de la raíz y de los notebooks
├── lanzar.sh               levanta los dos agentes, sus tarjetas y (opcional) túneles y puentes
├── entrega/                lo que se entrega (el zip se arma desde aquí)
│   ├── README.md · blueprint.md · documento-entrega.ipynb
│   ├── mi-agente/          Agente Fabio (proyecto completo, con su .venv local)
│   └── segundo-agente/     ProteinMAN (proyecto completo, con su .venv local)
├── herramientas/
│   ├── preguntar.py        cliente A2A de terminal (un agente o el supervisor)
│   ├── puente.py           publica un agente como A2A clásico (tarjeta sin parámetros y POST /)
│   ├── chat.html           chat web con los dos agentes
│   ├── diagramas.py        genera docs/diagramas.html (los grafos salen del código)
│   └── empaquetar.sh       arma grupo-N-taller-a2a.zip sin secretos
├── docs/
│   ├── 05-taller-…html     enunciado
│   ├── blueprints.md         blueprints de los dos agentes (formato del grupo)
│   ├── blueprint-agentes.md  blueprint del sistema (los dos agentes y cómo colaboran)
│   ├── compartir-con-cloudflare.md
│   └── diagramas.html
├── logs/                   salida de lanzar.sh (servidores, túneles, puentes)
└── innecesario/            material de consulta y versiones anteriores; no se usa ni se sube al repositorio
```

## Puesta en marcha
```bash
# 1. Entorno de cada agente (una vez)
cd entrega/mi-agente      && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cp .env.example .env
cd ../segundo-agente      && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cp .env.example .env
#    → pegar GOOGLE_API_KEY en los dos .env

# 2. Entorno de las herramientas (una vez, en la raíz)
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 3. Levantar los agentes
bash lanzar.sh --sin-tunel        # solo local
bash lanzar.sh                    # + túnel de Cloudflare para cada agente
bash lanzar.sh --puente           # + puente: cualquier cliente A2A estándar, sin assistant_id

# 4. Usarlos
python herramientas/preguntar.py fabio "¿Qué es el e-value de BLAST?"
python herramientas/preguntar.py proteinman "¿Qué métricas uso con familias desbalanceadas?"
python herramientas/preguntar.py supervisor "Tengo lecturas FASTQ de baja calidad, ¿qué hago?"
xdg-open herramientas/chat.html
```
Los notebooks (`entrega/segundo-agente/notebooks/a2a-test.ipynb` y después `entrega/mi-agente/notebooks/a2a-test.ipynb`) recorren las etapas 2 y 3 del taller y quedan ejecutados en la entrega.

## Entrega
```bash
bash herramientas/empaquetar.sh 7     # → grupo-7-taller-a2a.zip (reemplaza 7 por el número de grupo)
```
Antes de entregar, completa los marcadores ⟨GRUPO⟩, ⟨APORTE GUSTAVO⟩ y ⟨APORTE EZEQUIEL⟩ en `entrega/README.md`, `entrega/blueprint.md` y en el documento de entrega.

## Seguridad
- Las claves viven solo en `entrega/*/.env`. Ningún `.env` entra al zip (`empaquetar.sh` lo comprueba).
- Una URL de túnel deja usar tu cuota de Gemini a quien la tenga: compártela solo en clase y detén `lanzar.sh` con Ctrl+C al terminar.
