<!--encabezado-grupo-->
> **Archivo:** `respuestas/60-fix-endpoint-clasico-host-interno.md`  
> **Objetivo:** 60 · Respuesta — Ezequiel (Mac), Gustavo y fix de endpoint clásico con host interno  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1642 · **Última modificación:** 20261112 1642
<!--/encabezado-grupo-->

# 60 · Respuesta — Ezequiel (Mac) + Gustavo + fix de endpoint clásico

Prompt: [`../prompts_ejecutados/60-fix-endpoint-clasico-host-interno.md`](../prompts_ejecutados/60-fix-endpoint-clasico-host-interno.md)

## 1 · Ezequiel del Mac (túnel nuevo)

El túnel previo (`reservations-…`) quedó zombie (proceso vivo, URL sin responder → 000). Se levantó
uno nuevo:

```
URL: https://workplace-incurred-eden-charleston.trycloudflare.com
card langgraph (sin assistant_id) -> 400  (alcanzable)
name con assistant_id -> "Agente de Ezequiel"
```

Se actualizó la config del coordinador del VPS (campo `ezequiel`). Ruteo real por el coordinador:
```
elegido: Agente de Ezequiel · destino host: workplace-incurred-eden-charleston.trycloudflare.com
resp: [Agente de Ezequiel] Para clasificación desbalanceada… ROC-AUC, F1 (macro y por clase), matriz de confusión…
```

## 2 · Gustavo (`agente_meteorologo`)

Sondeo de `https://devon-harris-retain-shoe.trycloudflare.com`:
- Agent Card clásica (`/.well-known/agent-card.json`): **name `agente_meteorologo`**, skills "Clima de
  hoy"/"Clima semanal" (Santiago/Concepción/Valdivia). `supportedInterfaces[0].url =
  http://127.0.0.1:8003` (su bind interno). No es langgraph (`/assistants/search` → 404).

## 3 · Bug: endpoint clásico usaba el host interno de la card

`_endpoint_clasico` tomaba la `url` / `supportedInterfaces[].url` de la card tal cual. La de Gustavo
es `http://127.0.0.1:8003`, así que el cliente intentaba conectarse a **ese host local** (no al
túnel) → `httpx.ConnectError: [Errno 61] Connection refused`, y el coordinador lo marcaba
"no disponible".

**Fix (`src/coordinador/a2a.py`):** si el host anunciado por la card es **local/privado**
(`127.0.0.1`, `localhost`, `10.*`, `192.168.*`, `172.16–31.*`, vacío), se ignora ese host y se usa la
`base` (el túnel por el que SÍ llegamos), conservando solo el `path` anunciado. Si el host anunciado
es público, se respeta. Se agregó el helper `_host_privado`.

### Verificación

- Local (cliente directo): endpoint resuelto → `https://devon-…trycloudflare.com`; respuesta real:
  *"Para hoy en Valdivia se espera lluvia intermitente… máx 16 °C, mín 7 °C."*
- Tests: `pytest` de interop/resiliencia/robustez A2A → **35 passed**.
- End-to-end por el coordinador del VPS:
  ```
  elegido: agente_meteorologo · destino host: devon-harris-retain-shoe.trycloudflare.com
  resp: [agente_meteorologo] El pronóstico para hoy en Valdivia es de lluvia intermitente…
  ```

## 4 · Estado del catálogo (tras configurar)

| Agente | Estado |
|---|---|
| agente_cocina | disponible (local VPS) |
| Agente de Ezequiel | disponible (Mac, remoto) |
| Agente de Tomás | disponible (Windows, remoto) |
| agente_meteorologo (Gustavo) | disponible (remoto) |
| Agente Fabio | no_disponible (su túnel caído) |
| ProteinMAN | no_disponible (su túnel caído) |

## Archivos tocados

- `src/coordinador/a2a.py` — `import urlparse`, helper `_host_privado`, fix en `_endpoint_clasico`.
- `prompts_ejecutados/60-…md` y `respuestas/60-…md` (este registro).

## Pendientes

- Fabio y ProteinMAN quedan `no_disponible` hasta que sus dueños refresquen su túnel (se actualiza en
  ⚙️). Los túneles de Cloudflare son efímeros.
- Regenerar el zip de entrega para incluir 60 cuando se pida.
- Housekeeping: revocar el sudo temporal (`sudo rm /etc/sudoers.d/90-administrator-nopasswd`).
