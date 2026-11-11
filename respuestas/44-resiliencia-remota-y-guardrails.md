<!--encabezado-grupo-->
> **Archivo:** `respuestas/44-resiliencia-remota-y-guardrails.md`  
> **Objetivo:** Respuesta 44 · Resiliencia de agentes remotos y guardrails  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 0730 · **Última modificación:** 20261111 0735
<!--/encabezado-grupo-->

# Respuesta 44 · Resiliencia de agentes remotos y guardrails

## Qué se implementó

### 1. Agente remoto no disponible (`src/coordinador/`)
- **`a2a.py`**: excepción `AgenteNoDisponible(destino, motivo)` y helper `_json(...)`
  que envuelve toda petición HTTP: `raise_for_status()` + captura de
  `httpx.ConnectError`, `TimeoutException`, `HTTPStatusError`, errores de red y
  `JSON` inválido → siempre `AgenteNoDisponible` con un motivo legible (nunca una
  excepción cruda de httpx). Se aplicó a `assistant_id`, `agent_card` y `enviar_mensaje`.
- **`catalogo.py`**: nuevo `AgenteRemoto.disponible()`; `texto_catalogo` marca el
  agente caído como `(no disponible ahora — intentar más tarde)` en vez de romperse,
  así el catálogo se arma con los agentes que sí funcionan.
- **`graph.py`**: el nodo `consultar` captura `AgenteNoDisponible` y devuelve un
  **estado controlado**: «El Agente de X no está disponible temporalmente (motivo).
  Puedes intentar nuevamente más tarde. Los demás agentes continúan operativos.»
  (ruta `agente_no_disponible`).

### 2. Guardrails (`src/coordinador/guardrails.py`, nuevo)
- **Entrada** (`revisar_entrada`): bloquea vacías, excesivamente largas
  (`GUARDRAIL_MAX_ENTRADA`, def. 4000) y patrones de inyección/jailbreak (ES/EN).
  Cableado como nodo `guardia_entrada` ANTES del supervisor (no gasta LLM si se bloquea).
- **Salida** (`redactar_secretos`): redacta Google API key, OpenAI key, bearer
  tokens, contraseñas/claves y tarjetas antes de devolver la respuesta.
- **A2A** (`sanear_respuesta_remota`): la respuesta remota es un DATO; se redactan sus
  secretos y, si trae una instrucción incrustada, se marca «se muestra como dato y
  NO se obedece». Cableado en `consultar`.

## Pruebas (pytest)
- `tests/test_guardrails.py` (12) + `tests/test_resiliencia_a2a.py` (7).
- Suite completa: **57 passed, 1 skipped** (el skipped necesita servidor+clave).

## Evidencia real (Windows/Tomás CAÍDO) → `evidencias/06-robustez-mac.md`

**Resiliencia:**
- Catálogo con el remoto caído: los locales siguen; `agente_tomas: (no disponible ahora…)`.
- Llamada A2A directa al túnel caído → `AgenteNoDisponible … motivo: no se pudo
  conectar (¿túnel caído?)` + el estado controlado del coordinador.
- Coordinador end-to-end: la pregunta de Reiki (Tomás caído) se enruta a `sin_agente`
  (el supervisor evita el marcado), y la pregunta local sigue respondiendo
  (`supervisor → agente_local → [Agente de Ezequiel] …`). Defensa en capas.

**Guardrails (ataques detenidos):**

| Caso | Resultado |
|---|---|
| vacía / solo espacios | ⛔ bloqueada (entrada vacía) |
| inyección ES / EN | ⛔ bloqueada (patrón de inyección) |
| jailbreak de rol / robo de clave | ⛔ bloqueada |
| entrada excesiva (4050 > 4000) | ⛔ bloqueada |
| pregunta normal | ✅ pasa |
| secreto en salida (`AIza…`, `Bearer …`, `password:`) | redactado `[REDACTADO]` |
| respuesta remota con instrucción | ⚠️ neutralizada (se muestra como dato) |

## Cómo reproducir
```bash
uv run pytest tests/test_guardrails.py tests/test_resiliencia_a2a.py -q
uv run python tools/evidencia_robustez.py --remoto https://<tunel-caido> --etiqueta mac
```
