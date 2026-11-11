<!--encabezado-grupo-->
> **Archivo:** `guia_para_gustavo.md`  
> **Objetivo:** Guía para Gustavo · conectar tu coordinador con el agente de Ezequiel (A2A)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1342 · **Última modificación:** 20261111 1438
<!--/encabezado-grupo-->

# Guía para Gustavo · conectar tu coordinador con el agente de Ezequiel (A2A)

Hola Gustavo. Probamos conectar tu `agente_meteorologo` con nuestro coordinador y
encontramos que **usamos dos variantes distintas de A2A**. Esta guía explica el problema,
te deja **una URL lista para que consumas nuestro agente**, y lo que necesitamos de tu lado.

## 1. El problema (no es culpa de nadie: son dos "dialectos" A2A)

| | Tú (SDK a2a-protocol.org) | Nosotros (LangGraph `langgraph dev`) |
|---|---|---|
| Agent Card | `/.well-known/agent-card.json` (sin parámetros) | `/.well-known/agent-card.json?**assistant_id=<uuid>**` |
| Endpoint de mensajes | `POST /` (la URL base) | `POST /a2a/<assistant_id>` |

Por eso:
- Cuando **tú** pides nuestra card sin `assistant_id`, nuestro servidor responde
  `{"error":{"code":-32602,"message":"Missing required query parameter: assistant_id"}}`.
- Cuando **nosotros** te mandamos un `message/send`, tu servidor responde `-32601 Method not found`.

## 2. Solución lista: usa nuestro PUENTE (habla tu mismo dialecto)

Levantamos un **puente A2A clásico** que expone nuestro **Agente de Ezequiel** (IA / Data
Science) en el formato que tu SDK espera: card sin `assistant_id` y mensajes en la URL base.

**Apunta tu cliente/coordinador a esta URL:**

```
https://manufacturers-berkeley-lightning-big.trycloudflare.com
```

Verificación rápida (te debe devolver la card con `"name": "Agente de Ezequiel"`):

```bash
curl https://manufacturers-berkeley-lightning-big.trycloudflare.com/.well-known/agent-card.json

curl -X POST https://manufacturers-berkeley-lightning-big.trycloudflare.com \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":"1","method":"message/send",
       "params":{"message":{"role":"user","kind":"message","messageId":"m1","contextId":"gustavo-1",
       "parts":[{"kind":"text","text":"¿Qué técnica uso si tengo desbalance de clases?"}]}}}'
```

Nota: la URL es un túnel efímero de Cloudflare; si deja de responder, te paso una nueva.

## 3. Lo que necesitamos de tu lado (para que NOSOTROS te llamemos a ti)

Nuestro cliente ya puede hablar tu dialecto clásico (leer tu card sin `assistant_id` y postear
a tu URL base). Pero al enviarte `message/send` (y `tasks/send`, `message/stream`, etc.) tu
servidor devuelve **`-32601 Method not found`**, incluso con una petición conforme al spec.

¿Podrías revisar en tu servidor:
1. **Qué método** registra tu endpoint para recibir mensajes (tu log al recibir nuestra
   petición debería mostrarlo), y/o
2. **En qué ruta** escucha realmente (tu card anuncia la URL base como endpoint JSON-RPC).

Con eso ajustamos nuestro cliente (o tú el método) y probamos el **ida y vuelta** completo.

## 4. Un detalle técnico que te puede pasar a ti también

LangGraph usa el `contextId` como `thread_id` y **exige que sea un UUID**. Si tu cliente manda
un `contextId` que no es UUID, un backend LangGraph responde `Invalid thread ID`. En el puente
lo resolvimos coaccionando el `contextId` a un UUID estable. Si consumes otros agentes
LangGraph, mándales un UUID como `contextId`.

Cualquier duda, me dices. — Ezequiel
