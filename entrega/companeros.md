<!--encabezado-grupo-->
> **Archivo:** `entrega/companeros.md`  
> **Objetivo:** Compañeros · agentes ajenos sumados al coordinador  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1941 · **Última modificación:** 20261112 1508
<!--/encabezado-grupo-->

# Compañeros · agentes ajenos sumados al coordinador

Agentes de otros integrantes/grupos que nuestro coordinador puede invocar por A2A (se suman por
`URLS_AGENTES`). La URL del túnel es efímera: se intercambia al momento de la ronda.

> **Nuestro agente, para que los compañeros lo consuman (URL permanente):**
> `https://agente.etmk.cl` — A2A clásico, `POST /` con `message/send`, ficha en
> `https://agente.etmk.cl/.well-known/agent-card.json`. Reemplaza al túnel efímero del Mac;
> está siempre activo (VPS, HTTPS). Detalle en `documento-entrega.md` §11.1.

## agente_meteorologo — autor: Gustavo Reyes

- **Skill:** pronósticos (ficticios) del clima de hoy y de los próximos 7 días para **Santiago,
  Concepción y Valdivia** (temperaturas y condiciones). No responde fuera de meteorología ni otras
  ciudades/plazos.
- **Repositorio:** https://github.com/guswolf-007/taller_A2A_uai
- **Stack:** FastAPI + SDK **a2a-protocol.org** (`create_jsonrpc_routes(..., rpc_url="/")`).
- **Dialecto A2A:** clásico pero con **método `SendMessage`** (no `message/send`), `role
  ROLE_USER`, parts sin `kind`, header `A2A-Version: 1.0`; respuesta en *content blocks*
  (`[{'type':'text','text':…}]`). Nuestro cliente lo maneja con el fallback + desanidado (prompt 51)
  y recuerda el método por host (prompt 52).
- **Entrada en `.env`:** `URLS_AGENTES=https://<tunel-de-gustavo>.trycloudflare.com#agente_meteorologo`
- **Ficha (Agent Card) — formato clásico, sin `assistant_id`:**

```json
{
  "name": "agente_meteorologo",
  "description": "Entrego pronosticos ficticios del clima de hoy y de los proximos siete dias para Santiago, Concepcion y Valdivia, con temperaturas y condiciones meteorologicas. No respondo preguntas fuera de la Meteorologia ni pronosticos para otras ciudades, o para plazos superiores a siete dias.",
  "version": "1.0.0",
  "capabilities": {"streaming": false},
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "skills": ["Clima de hoy", "Clima semanal"],
  "supportedInterfaces": [{"url": "https://<tunel>/", "protocolBinding": "JSONRPC", "protocolVersion": "1.0"}]
}
```

- **Evidencia de la interoperación:** `evidencias/13-interop-gustavo-mac.md` (nuestro cliente →
  su agente, y la ronda end-to-end del coordinador con `agente_meteorologo` en el catálogo).

## agente_fabio — autor: Fabio Durán

Lo **consumimos en vivo** durante la sesión. Esto es exactamente lo que observamos:

- Su endpoint es **LangGraph nativo**: `GET /.well-known/agent-card.json` **sin** `assistant_id`
  devolvió `{"error":{"code":-32602,"message":"Missing required query parameter: assistant_id"}}`.
- `POST /assistants/search` → **`graph_id = agente_fabio`**, **`assistant_id =
  61ac3d13-9376-5266-a91e-23c8d9c1b340`**.
- Consumido con nuestro cliente (`a2a.enviar_mensaje`), respondió sobre **bioinformática**. Textual:
  *"Puedes preguntarme sobre análisis de secuencias de ADN y proteínas, consulta en bases de datos
  públicas como UniProt o NCBI, y sobre cómo armar flujos de análisis (pipelines) reproducibles."* y
  *"uso principalmente UniProt, distinguiendo entre Swiss-Prot (revisada por curadores) y TrEMBL
  (anotaciones automáticas)…"*.

- **Nombre / skill:** `agente_fabio` — **bioinformática**: secuencias de ADN/proteínas, consulta a
  **UniProt** (Swiss-Prot/TrEMBL) y **NCBI**, y **pipelines reproducibles**.
- **Autor:** Fabio Durán.
- **URL:** túnel de Cloudflare **efímero** — cuando lo probamos era
  `https://yarn-logic-slideshow-graphics.trycloudflare.com` (`assistant_id=61ac3d13-9376-5266-a91e-23c8d9c1b340`);
  cambia en cada corrida y al empaquetar ya no respondía.
- **Nos reveló un fix:** su servidor langgraph exige que el `contextId` (= thread_id) sea un **UUID**
  (`-32602 "Invalid thread ID"` si no lo es). Nuestro cliente ahora lo coacciona a UUID para todos
  los dialectos — commit `52eba04` + test (ver `respuestas/55`, §4).
- **Ficha (Agent Card):** **no capturamos su card completa** (solo resolvimos su `assistant_id` y lo
  consumimos; su túnel efímero ya no responde — la ficha exacta la tiene Fabio en su repo). Lo que sí
  consta de lo observado, en formato LangGraph nativo:

```json
{
  "graph_id": "agente_fabio",
  "assistant_id": "61ac3d13-9376-5266-a91e-23c8d9c1b340",
  "description": "Bioinformatica: analiza secuencias de ADN y proteinas, consulta bases publicas (UniProt —Swiss-Prot/TrEMBL— y NCBI) y arma flujos de analisis (pipelines) reproducibles.",
  "card_url": "/.well-known/agent-card.json?assistant_id=61ac3d13-9376-5266-a91e-23c8d9c1b340",
  "endpoint_mensajes": "/a2a/61ac3d13-9376-5266-a91e-23c8d9c1b340"
}
```

- **Evidencia:** la interacción (resolución de `assistant_id`, respuestas de bioinformática y el bug
  `Invalid thread ID` → fix) está en `respuestas/55-despliegue-vps-interop-backoffice.md` (§4).

> Para que Gustavo consuma NUESTRO agente (sentido inverso) se usa el puente del prompt 49
> (ver `src/puente_a2a/` y `guia_para_gustavo.md`). En producción ese puente está publicado de
> forma permanente en **`https://agente.etmk.cl`** (ver `documento-entrega.md` §11.1), así que ya
> no hace falta pasar una URL de túnel nueva cada vez.
