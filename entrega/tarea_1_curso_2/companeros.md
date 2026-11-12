<!--encabezado-grupo-->
> **Archivo:** `entrega/companeros.md`  
> **Objetivo:** Compañeros · agentes ajenos sumados al coordinador  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1941 · **Última modificación:** 20261111 2049
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

- **Skill:** **bioinformática** — análisis de secuencias de **ADN y proteínas**, consulta a bases de
  datos públicas (**UniProt** —Swiss-Prot/TrEMBL— y **NCBI**) y armado de **pipelines reproducibles**.
  No responde temas fuera de bioinformática.
- **Autor:** Fabio Durán.
- **Dialecto A2A:** **LangGraph nativo** (igual que nuestros agentes): la card se pide con
  `?assistant_id=<uuid>` y los mensajes van a `/a2a/<assistant_id>`; el `contextId` debe ser un
  **UUID** (= thread_id). *(Consumirlo nos reveló un fix: nuestro cliente ahora coacciona el
  `contextId` a UUID para evitar `-32602 "Invalid thread ID"` — ver `respuestas/55`.)*
- **URL:** túnel de Cloudflare **efímero** (p. ej. `https://yarn-logic-slideshow-graphics.trycloudflare.com`,
  `assistant_id=61ac3d13-9376-5266-a91e-23c8d9c1b340`); cambia en cada corrida.
- **Ficha (Agent Card) — formato LangGraph nativo** *(reconstruida: su túnel estaba caído al empaquetar)*:

```json
{
  "name": "agente_fabio",
  "description": "Agente de bioinformatica: analiza secuencias de ADN y proteinas, consulta bases de datos publicas (UniProt —Swiss-Prot y TrEMBL— y NCBI) y ayuda a armar flujos de analisis (pipelines) reproducibles. No responde temas fuera de bioinformatica.",
  "version": "0.17.1",
  "url": "https://<tunel-de-fabio>.trycloudflare.com",
  "preferredTransport": "JSONRPC",
  "capabilities": {"streaming": true, "pushNotifications": false},
  "defaultInputModes": ["application/json", "text/plain"],
  "defaultOutputModes": ["application/json", "text/plain"],
  "skills": [{"name": "Agente de Fabio Capabilities"}]
}
```

- **Evidencia de la interoperación:** consumido en vivo (preguntas de bioinformática: ADN/proteínas,
  UniProt) durante el prompt 55; detalle en `respuestas/55-despliegue-vps-interop-backoffice.md` (§4).

> Para que Gustavo consuma NUESTRO agente (sentido inverso) se usa el puente del prompt 49
> (ver `src/puente_a2a/` y `guia_para_gustavo.md`). En producción ese puente está publicado de
> forma permanente en **`https://agente.etmk.cl`** (ver `documento-entrega.md` §11.1), así que ya
> no hace falta pasar una URL de túnel nueva cada vez.
