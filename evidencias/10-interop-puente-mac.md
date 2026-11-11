<!--encabezado-grupo-->
> **Archivo:** `evidencias/10-interop-puente-mac.md`  
> **Objetivo:** Interoperabilidad A2A: puente al formato clásico · evidencia (mac)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1342 · **Última modificación:** 20261111 1343
<!--/encabezado-grupo-->

# Interoperabilidad A2A: puente al formato clásico · evidencia (mac)

Prompt 49. Conecta nuestro `agente_ezequiel` (langgraph dev) con un cliente A2A estándar
(SDK a2a-protocol.org, como el de Gustavo) mediante un puente adaptador.

## 1. El problema (dos dialectos A2A)

| | Nosotros (langgraph dev) | Compañero (SDK a2a-protocol.org) |
|---|---|---|
| Agent Card | `/.well-known/agent-card.json?**assistant_id=<uuid>**` | `/.well-known/agent-card.json` (sin parámetro) |
| Mensajes | `POST /a2a/<assistant_id>` | `POST /` (URL base) |

- Gustavo → nosotros: su cliente pide la card sin `assistant_id` → langgraph responde
  `{"error":{"code":-32602,"message":"Missing required query parameter: assistant_id"}}`.
- Nosotros → Gustavo: su endpoint rechaza nuestro `message/send` con `-32601`.

## 2. La solución: puente A2A clásico (`src/puente_a2a/`)

Un `http.server` de stdlib (sin dependencias nuevas) que expone `agente_ezequiel` en
formato clásico y traduce al flujo langgraph. Card por el túnel del puente:

```
GET /.well-known/agent-card.json   (SIN assistant_id)
{"name": "agente_ezequiel", "url": "https://manufacturers-berkeley-lightning-big.trycloudflare.com", "iface": "https://manufacturers-berkeley-lightning-big.trycloudflare.com"}
```

`message/send` por el túnel (formato clásico, POST a la URL base):

```
> ¿Qué técnica uso si tengo desbalance de clases?
Te recomiendo usar class weights, técnicas de resampleo como SMOTE o undersampling, y métricas orientadas a la clase minoritaria como F1-score o PR-AUC. Esto evita que la accuracy te engañe cuando una clase es muy rara frente a la otra.
```

URL pública del puente (para pasar a Gustavo): `https://manufacturers-berkeley-lightning-big.trycloudflare.com`

## 3. Experiencia fallida y cómo se arregló

**Primer intento (falló):** al hacer `message/send` con un `contextId` arbitrario del
cliente (p. ej. `"c1"` / `"gustavo-hilo-1"`), el puente lo reenviaba tal cual a langgraph y
este respondía:

```
[error del agente remoto: {'code': -32602, 'message': 'Failed to create run: Invalid thread ID'}]
```

**Causa:** langgraph dev usa el `contextId` como `thread_id` y **exige que sea un UUID**.
Nuestro coordinador siempre manda UUIDs, pero un cliente A2A externo puede mandar cualquier
string.

**Arreglo:** `a2a.a_uuid()` coacciona el `contextId` a un UUID **válido y estable**: si ya
es UUID se respeta; si no, se deriva `uuid5` (mismo texto → mismo UUID, preservando la
memoria del hilo). El puente lo aplica en `extraer_texto_y_ctx`. Tras el fix, el mismo
`message/send` con `contextId` no-UUID responde correctamente (ver §2).

**Segundo detalle:** la primera card salió con el nombre genérico (`agente_ezequiel`) porque
el hot-reload de langgraph había borrado las fichas; se recuperó con `configurar_fichas.py`
y la card pasó a mostrar «Agente de Ezequiel».

## 4. Pruebas

`tests/test_interop_a2a.py` (10): `a_uuid`, detección de dialecto, cliente en modo clásico
(postea a la URL base), funciones de traducción del puente y un **end-to-end real** del
puente (servidor en un puerto libre, langgraph simulado). Suite completa: 80 passed, 1 skipped.

## 5. Límite

El sentido inverso (nuestro coordinador → agente de Gustavo) requiere que su servidor
acepte `message/send`: hoy responde `-32601`. Nuestro cliente ya habla el dialecto clásico
(leería su card sin `assistant_id` y postearía a su URL base), pero no se puede validar de
extremo a extremo hasta que su endpoint responda.
