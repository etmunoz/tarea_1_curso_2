<!--encabezado-grupo-->
> **Archivo:** `respuestas/59-agente-proteinman-configurable.md`  
> **Objetivo:** 59 · Respuesta — ProteinMAN configurable + fix de chips vacíos  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1624 · **Última modificación:** 20261112 1624
<!--/encabezado-grupo-->

# 59 · Respuesta — ProteinMAN configurable + fix de chips

Prompt: [`../prompts_ejecutados/59-agente-proteinman-configurable.md`](../prompts_ejecutados/59-agente-proteinman-configurable.md)

## 1 · ProteinMAN como 5º agente configurable

Cambios en `tools/coordinador_web.py`:

- `AGENTES_CFG` += `("proteinman", "proteinman", False)` (remoto).
- Campo `🦸 Proteinman` en el modal de ⚙️; `CLAVES` del JS incluye `proteinman`; `meta()` le asigna
  icono 🦸 / color.

## 2 · Descubrimiento del grafo (sondeo de la URL)

URL entregada: `https://founded-mandatory-examined-nominated.trycloudflare.com`.

```
GET /ok                          -> 200            (langgraph nativo)
POST /assistants/search          -> graph_id: proteinman
                                    assistant_id: 988d2098-af3e-5d3f-9bec-7ace332b7936
GET /.well-known/agent-card.json -> exige assistant_id (dialecto langgraph)
```

Ficha (Agent Card):
- **name:** ProteinMAN
- **description:** "Especialista en IA y Data Science aplicada a bioinformática. Puede: recomendar
  técnicas de ML para problemas con datos biológicos, sugerir métricas para evaluar modelos
  bioinformáticos, elegir un modelo según el tipo de dato biológico (secuencias, expresión génica,
  estructuras)."

→ El `graph_id` real es **`proteinman`** (mi default `agente_proteinman` era incorrecto); se corrigió
en `AGENTES_CFG`. Commit `dc89b5b`.

## 3 · Fix de chips vacíos (`_agentes`)

`src/coordinador/catalogo.py`: `nombre` es `@property` pero `descripcion` es un **método**. En
`_agentes()` se usaba `a.descripcion` (sin llamar) → `(desc or "")[:160]` lanzaba
`TypeError: 'method' object is not subscriptable`, el handler devolvía `[]` y los chips salían
vacíos. Fix: `a.descripcion()`. Commit `236a289`.

## 4 · Verificación

`GET /api/agentes` (tras el fix):
```
AGENTES: 5
 - agente_cocina      | disponible | local
 - agente_tomas       | disponible | local
 - Agente de Ezequiel | disponible | remoto
 - Agente Fabio       | disponible | remoto
 - ProteinMAN         | disponible | remoto
```

Ruteo real a ProteinMAN:
```
elegido : ProteinMAN
ruta    : guardia_entrada → supervisor → agente_remoto → guardia_salida
destino : {"tipo":"remoto","grafo":"proteinman",
           "endpoint":"https://founded-mandatory-examined-nominated.trycloudflare.com",
           "host":"founded-...trycloudflare.com","ip":"104.16.230.132"}
respuesta: [ProteinMAN] Error executing assistant: ChatGoogleGenerativeAIError
```

→ El coordinador enrutó y consumió a ProteinMAN correctamente. El `ChatGoogleGenerativeAIError`
es **del backend de ProteinMAN** (su llamada a Gemini: clave/cuota), no del coordinador; la respuesta
se relayó como **dato** (guardrails) sin tumbar el servicio.

## Archivos tocados

- `tools/coordinador_web.py` — `AGENTES_CFG` (+proteinman), modal/JS/`meta()`, fix `descripcion()`.
- `prompts_ejecutados/59-…md` y `respuestas/59-…md` (este registro).

## Estado

- ProteinMAN agregado, configurable en ⚙️ y verificado en el ruteo del VPS. Los 5 agentes listan
  `disponible` y los chips ya se pintan.

## Pendientes

- La URL de ProteinMAN es un túnel efímero (se cambia en ⚙️ cuando rote). Su error de Gemini lo
  resuelve quien corre ese agente.
- Regenerar el zip de entrega para incluir 57/58/59 cuando se pida.
- Housekeeping: revocar el sudo temporal (`sudo rm /etc/sudoers.d/90-administrator-nopasswd`).
