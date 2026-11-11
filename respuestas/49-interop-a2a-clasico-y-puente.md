<!--encabezado-grupo-->
> **Archivo:** `respuestas/49-interop-a2a-clasico-y-puente.md`  
> **Objetivo:** Respuesta 49 · Interoperabilidad A2A clásico: cliente generalizado + puente  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1343 · **Última modificación:** 20261111 1410
<!--/encabezado-grupo-->

# Respuesta 49 · Interoperabilidad A2A clásico: cliente generalizado + puente

Prompt: [`../prompts_ejecutados/49-interop-a2a-clasico-y-puente.md`](../prompts_ejecutados/49-interop-a2a-clasico-y-puente.md)

## Diagnóstico (dos dialectos A2A)

Al probar la URL de Gustavo descubrimos que corre el **SDK oficial de a2a-protocol.org**,
distinto a nuestro **langgraph dev**:

| | Nosotros (langgraph dev) | Gustavo (SDK a2a-protocol.org) |
|---|---|---|
| Agent Card | `/.well-known/agent-card.json?**assistant_id=<uuid>**` | `/.well-known/agent-card.json` (sin parámetro) |
| Mensajes | `POST /a2a/<assistant_id>` | `POST /` (URL base) |

- Gustavo → nosotros: `-32602 "Missing required query parameter: assistant_id"`.
- Nosotros → Gustavo: `-32601 "Method not found"`.

## (B) Cliente A2A generalizado (`src/coordinador/a2a.py`)

- `dialecto(base)`: detecta (con caché) si un servidor es `clasico` o `langgraph` pidiendo la
  card SIN `assistant_id` (si trae `name` ⇒ clásico; si pide el assistant_id ⇒ langgraph).
- `agent_card` y `enviar_mensaje` ahora **despachan según el dialecto**: en clásico leen la
  card directa y postean a la `url` de `supportedInterfaces`; en langgraph siguen el flujo
  `/assistants/search` → `/a2a/<aid>`.
- `a_uuid(valor)`: coacciona un `contextId` arbitrario a un UUID válido y estable.

## Puente A2A clásico (`src/puente_a2a/servidor.py`)

`http.server` de stdlib (sin dependencias nuevas) que expone `agente_ezequiel` en formato
clásico: sirve `/.well-known/agent-card.json` sin `assistant_id` (reescribiendo la `url` al
puente) y acepta `POST /` con `message/send`, traduciéndolo al flujo langgraph. Script:
`scripts/mac_puente.sh`. **URL pública (para Gustavo):** `https://manufacturers-berkeley-lightning-big.trycloudflare.com`

## ⚠️ Experiencia fallida y cómo la arreglamos

**Falla 1 — `Invalid thread ID`.** El primer `message/send` por el puente, con un `contextId`
del cliente que NO era UUID (p. ej. `"c1"`), devolvió:

```
[error del agente remoto: {'code': -32602, 'message': 'Failed to create run: Invalid thread ID'}]
```

*Causa:* langgraph dev usa el `contextId` como `thread_id` y **exige un UUID**. Nuestro
coordinador siempre manda UUIDs, pero un cliente externo puede mandar cualquier string.
*Arreglo:* `a2a.a_uuid()` — si ya es UUID lo respeta; si no, deriva `uuid5` (mismo texto →
mismo UUID, preservando la memoria del hilo). El puente lo aplica en `extraer_texto_y_ctx`.
Tras el fix, el mismo `message/send` con `contextId` no-UUID responde correctamente.

**Falla 2 — card con nombre genérico.** La primera card salió como `agente_ezequiel` (no
«Agente de Ezequiel») porque el hot-reload de langgraph había borrado las fichas. Se recuperó
con `configurar_fichas.py`.

## Evidencia real (por el túnel del puente)

```
GET https://manufacturers-berkeley-lightning-big.trycloudflare.com/.well-known/agent-card.json
  → name: Agente de Ezequiel · url: https://manufacturers-berkeley-lightning-big.trycloudflare.com (sin assistant_id)

POST https://manufacturers-berkeley-lightning-big.trycloudflare.com  (message/send, contextId "gustavo-demo" NO-UUID)
  → "Para el desbalance de clases te recomiendo usar class weights, SMOTE/undersampling y
     métricas como F1/PR-AUC…"
```

Detalle completo y la narrativa de la falla: `evidencias/10-interop-puente-mac.md`.
Guía para el compañero: `guia_para_gustavo.md`.

## Pruebas

`tests/test_interop_a2a.py` (10): `a_uuid` (respeta UUID / deriva estable), detección de
dialecto (clásico/langgraph), cliente clásico (postea a la URL base), funciones de traducción
del puente y un **end-to-end real** del puente (servidor en puerto libre, langgraph simulado).
Suite completa: **80 passed, 1 skipped**.

## Límite (honesto)

El sentido inverso (nuestro coordinador → agente de Gustavo) necesita que su servidor acepte
`message/send` (hoy `-32601`). Nuestro cliente ya habla el dialecto clásico, pero no se puede
validar de extremo a extremo hasta que su endpoint responda. Pendiente de su lado (ver guía).
