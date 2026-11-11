<!--encabezado-grupo-->
> **Archivo:** `respuestas/52-confirmar-repo-gustavo-y-cache-metodo.md`  
> **Objetivo:** Respuesta 52 · Confirmar interop contra el repo de Gustavo + cache de método  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1957 · **Última modificación:** 20261111 2016
<!--/encabezado-grupo-->

# Respuesta 52 · Confirmar interop contra el repo de Gustavo + cache de método

Prompt: [`../prompts_ejecutados/52-confirmar-repo-gustavo-y-cache-metodo.md`](../prompts_ejecutados/52-confirmar-repo-gustavo-y-cache-metodo.md)

## 1. Revisión del repo de Gustavo (confirmación)

Repo: https://github.com/guswolf-007/taller_A2A_uai. Estructura relevante: `main.py`, `src/`
(agentes `agente_meteorologo`, `agente_restaurantes`, `agente_viajes`, `coordinador`, y `comun/`).
El servidor A2A está en **`src/comun/servidor.py`**:

- **Framework:** FastAPI + SDK **a2a-protocol.org** (`a2a.server`), con
  `create_jsonrpc_routes(manejador, rpc_url="/")` y rutas de Agent Card.
- **Método JSON-RPC:** `SendMessage` (no `message/send`). Endpoints de salud: `/salud`, `/health`.
- **Respuesta:** su handler (`responder: Callable[[str,str],str]`) devuelve el texto del agente,
  que llega envuelto como *content blocks* (`[{'type':'text','text':…,'extras':{…}}]`).

→ **Confirma** que nuestro fallback a `SendMessage` + el desanidado (prompt 51) coinciden con su
implementación real. No hubo que corregir nada; sí se robusteció (abajo).

## 2. Mejora: cache de método por host

`src/coordinador/a2a.py`: nuevo `_cache_metodo`. Cuando un servidor clásico responde `-32601` a
`message/send` y el fallback `SendMessage` funciona, se **recuerda por host**. Las siguientes
llamadas van **directo a `SendMessage`**, sin gastar el `message/send` fallido (menos latencia,
una llamada en vez de dos).

```
tests/test_interop_sendmessage_51.py::test_cache_metodo_evita_reintento  → 2ª llamada: solo SendMessage
```

## 3. Documentación

- `entrega/companeros.md`: entrada completa de **agente_meteorologo** (autor Gustavo Reyes),
  con su repo, stack, dialecto, entrada en `.env` y la Agent Card.
- `evidencias/13-interop-gustavo-mac.md`: sección de confirmación contra su repo + la mejora.

## 4. Resultados (detallado)

```
$ uv run pytest tests/test_interop_sendmessage_51.py -q
6 passed        (desanidado, extractor, fallback, no-reintento, cache)

$ uv run pytest -q
147 passed, 1 skipped
```

- Live (del prompt 51, cuando su túnel estaba arriba): nuestro cliente → su agente devolvió
  pronósticos reales de Valdivia/Concepción, desanidados. En esta sesión su túnel está **caído**
  (`ConnectError`), y nuestro cliente lo reporta como `AgenteNoDisponible` (estado controlado, sin
  filtrar trazas) — la re-prueba live queda pendiente de que Gustavo levante su túnel.
- Interoperabilidad A2A **en ambos sentidos** confirmada contra su implementación real.

Rama/estado: en `main` (ya mergeado). `main` sigue sirviendo el puente para Gustavo.
