<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/49-interop-a2a-clasico-y-puente.md`  
> **Objetivo:** Prompt 49 · Interoperabilidad A2A clásico: cliente generalizado + puente  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1342 · **Última modificación:** 20261111 2016
<!--/encabezado-grupo-->

# Prompt 49 · Interoperabilidad A2A clásico: cliente generalizado + puente

**Pedido del usuario (textual, consolidado):**

> Quiero que vayas por **(B)**: generalizar nuestro cliente A2A para hablar también
> el "A2A clásico" (leer la card sin `assistant_id` y postear a la `url` de
> `supportedInterfaces`). Es una mejora real de interoperabilidad/robustez y encaja con
> el prompt 48 — pero igual necesito su endpoint respondiendo para validarlo de verdad.
>
> Y además: un **puente/adaptador A2A clásico** (`src/puente_a2a/`, un `http.server` de
> stdlib, sin dependencias nuevas) que:
> 1. Sirve `/.well-known/agent-card.json` **sin** `assistant_id` — toma la ficha real de
>    `agente_ezequiel` desde langgraph dev y reescribe la `url` para apuntar al propio puente.
> 2. Acepta `POST /` con JSON-RPC `message/send` y lo traduce al flujo langgraph
>    (`/assistants/search` → `/a2a/<aid>`), devolviendo la respuesta en formato A2A estándar.
>
> Luego levantas un túnel de Cloudflare al puente y esa URL se la pasas a Gustavo.
> Para el sentido inverso (nosotros→Gustavo) él debe revisar su `-32601`.
>
> Todo como prompt 49; luego seguimos con el 48.

**Contexto:** Gustavo corre el SDK oficial de `a2a-protocol.org` (card sin `assistant_id`,
mensajes en la URL base). Nuestro langgraph dev exige `?assistant_id=<uuid>` en la card y
usa `/a2a/<aid>`. Son dos dialectos A2A distintos: no interoperan sin adaptación.

**Tareas:**
1. `src/coordinador/a2a.py`: detectar el dialecto del servidor y hablar también "A2A
   clásico" (card sin `assistant_id`; mensajes a la `url` de `supportedInterfaces`).
2. `src/puente_a2a/`: adaptador stdlib que expone `agente_ezequiel` en formato clásico.
3. Script del puente + túnel. Pruebas deterministas. Evidencia local y por el túnel.
