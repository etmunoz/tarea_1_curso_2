<!-- --8<-- encabezado-grupo
Archivo: README_proyecto_base.md
Objetivo: agente-viajes-a2a
Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
Creación: 20261110 1514
Última modificación: 20261110 1935
--8<-- fin-encabezado-grupo -->

# agente-viajes-a2a

Un agente de viajes (LangGraph) expuesto por **A2A de forma nativa**, un consumidor pendiente de construir con OpenCode, y un **swarm** vuelos + hoteles al que se le agrega un tercer agente.

## 1. Levantar el agente de viajes (A2A nativo, sin código de servidor)
```bash
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate   (Python 3.11+)
pip install -r requirements.txt
cp .env.example .env                                   # pega tu GOOGLE_API_KEY
langgraph dev                                          # http://127.0.0.1:2024
```
El servidor asigna a cada grafo un `assistant_id` (UUID). Se obtiene así, y con él la tarjeta y el endpoint:
```bash
AID=$(curl -s -X POST http://127.0.0.1:2024/assistants/search -H "Content-Type: application/json" -d '{"graph_id":"agente_viajes"}' | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['assistant_id'])")
curl -s "http://127.0.0.1:2024/.well-known/agent-card.json?assistant_id=$AID" | python3 -m json.tool
CTX=$(python3 -c "import uuid; print(uuid.uuid4())")     # contextId = UUID = thread del agente remoto
curl -s -X POST "http://127.0.0.1:2024/a2a/$AID" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":\"1\",\"method\":\"message/send\",\"params\":{\"message\":{\"role\":\"user\",\"messageId\":\"m1\",\"contextId\":\"$CTX\",\"parts\":[{\"kind\":\"text\",\"text\":\"Quiero un vuelo de Santiago a Lima el 2026-11-10 y un hotel por 2 noches\"}]}}}"
```
### En Windows (PowerShell)
```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1        # si da error de permisos: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements.txt
copy .env.example .env             # pega tu GOOGLE_API_KEY
langgraph dev                      # mismo comando; la primera vez Windows pregunta por el firewall: permitir solo redes privadas
```
Para probar usa **Bruno** (los `curl` de arriba son de bash: en PowerShell `curl` es otro comando). Si insistes con la terminal, usa `curl.exe` y comillas dobles.

### Mejorar la Agent Card (nombre, descripción y el texto de la skill)
La tarjeta la genera el servidor a partir del **nombre y la descripción del assistant**. Por defecto salen `agente_viajes` y `agente_viajes assistant`, y la única skill se llama `<nombre> Capabilities`. Para que diga algo útil:
```bash
curl -s -X PATCH "http://127.0.0.1:2024/assistants/$AID" -H "Content-Type: application/json" \
  -d '{"name": "Agente de viajes", "description": "Busca vuelos y hoteles (SCL, LIM, BOG, EZE) con precios en CLP. No gestiona pagos ni seguros."}'
```
En Bruno es el request `1-configurar-tarjeta`. El cambio queda guardado en `.langgraph_api/` (local). La palabra "Capabilities" y el hecho de que haya una sola skill los fija el servidor: si necesitas varias skills con ejemplos, hay que exponer el agente con `a2a-sdk` y escribir la tarjeta a mano.

- Bruno: abre la carpeta `bruno/`, elige el entorno `local`, corre `0-assistant-id` (guarda el UUID en el entorno), `1-configurar-tarjeta` (nombre y descripción reales) y luego `agent-card` y `message-send`.
- Pruebas: `pytest tests/test_a2a_viajes.py` (con `langgraph dev` arriba).

## 2. Construir el agente conversacional con OpenCode
Con `langgraph dev` corriendo, abre OpenCode en esta carpeta y pega exactamente esto:
```
@spec  quiero crear un agente que consuma el A2A del agente de viajes 

grupo: agente-conversacional
este agente tiene que ser conversacional 
generame el notebook paso a paso

quiero solamente 3 pasos, configuracion base, agentes y consumo de la herramiente dummy precio btc

notebook para revisar el comportamiento
```
`@spec` escribe las tareas del grupo `agente-conversacional` en `plan.json`. Revísalas (cada una con verificación ejecutable) y luego:
```
@implementador toma la primera tarea pendiente del grupo agente-conversacional
```
Repite `@implementador` tarea por tarea hasta que el notebook corra de arriba abajo.

## 3. Swarm
```bash
python -m src.swarm.graph        # demo: vuelos → hoteles → vuelos en un mismo hilo
```
Agregar el agente de actividades: tareas s01 → s05 de `plan.json`, con `@implementador`.
