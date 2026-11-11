<!--encabezado-grupo-->
> **Archivo:** `respuestas/48a-ajustes-finales-robustez.md`  
> **Objetivo:** Respuesta 48a · Ajustes finales de robustez (continuación del 48)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1429 · **Última modificación:** 20261111 1741
<!--/encabezado-grupo-->

# Respuesta 48a · Ajustes finales de robustez (continuación del 48)

Prompt: [`../prompts_ejecutados/48a-ajustes-finales-robustez.md`](../prompts_ejecutados/48a-ajustes-finales-robustez.md)

> Rama `prompt-48-robustez` (misma del 48). **No se mergeó a `main`.**

## Diagnóstico (¿se reproducen los 5 hallazgos?)

| # | Hallazgo | ¿Reproducido? | Causa raíz |
|---|---|---|---|
| 1 | Extracción A2A presupone estructuras | **Sí** | `_texto_de_resultado`/`_endpoint_clasico` usaban `.get`/índices sin validar tipos; fallback silencioso a `str(result)` |
| 2 | Auth no uniforme en descubrimiento | **Sí** | `dialecto()` llamaba `httpx.get` directo (sin auth/timeout) y clasificaba como langgraph todo lo no-clásico |
| 3 | Recuperación de assistant_id imprecisa | **Parcial** | Reintentaba ante cualquier 404; no comparaba id viejo/nuevo |
| 4 | Disponibilidad inferida de la caché | **Sí** | `estado()` usaba `self.card()` (caché de 120s) como prueba de conectividad |
| 5 | ALLOW/SANITIZE/BLOCK por política, no acción | **Sí** | respuesta limpia → `SANITIZE` por defecto |

## Correcciones aplicadas (resumen técnico)

1. **`a2a._texto_de_resultado(result, destino)`**: validación defensiva (dict/list/escalar/null);
   sin texto → `RespuestaA2AInvalida` (ya no `str(result)`). `_endpoint_clasico` valida
   `supportedInterfaces` y sus elementos. Firma con `destino` opcional (compatibilidad).
2. **`a2a.dialecto()`** pasa por `_pedir` (auth + timeouts + transporte controlado); nueva
   `AccesoDenegadoA2A` para `401/403`; solo clasifica `langgraph` si el cuerpo pide
   `assistant_id`; lo demás → `RespuestaA2AInvalida` (dialecto desconocido).
3. **`a2a.enviar_mensaje`**: recuperación acotada — captura el id viejo, re-busca, si el id **no
   cambió** → `IdentificadorAsistenteObsoleto` (sin reintento); búsqueda vacía/malformada →
   error controlado; segundo 404 → error; máximo **un** reintento; `401/403` → `AccesoDenegadoA2A`.
4. **`catalogo.estado()`** hace **sondeo fresco** (bypassa el TTL de capacidad) cacheando solo el
   resultado de conectividad (`_disp`, TTL corto); nueva `disponibilidad()` con tres estados
   (`disponible`/`no_disponible`/`desconocido`).
5. **`guardrails.evaluar_respuesta_remota`**: la **decisión = acción efectiva** — limpia → `ALLOW`,
   redacción/neutralización → `SANITIZE`, descarte → `BLOCK`; se conserva la política en el motivo.

Compatibilidad: ambos dialectos A2A (clásico/langgraph) siguen funcionando; la distinción
`sin_agente`/`agente_no_disponible` se conserva; sin dependencias nuevas; el grafo compila (7 nodos).

## Resultados reales de pruebas

```
$ uv run pytest tests/test_ajustes_48a.py -q
23 passed

$ uv run pytest -q
133 passed, 1 skipped
```

- Nuevas (48a): `tests/test_ajustes_48a.py` (23). Actualizada: `test_evaluar_remota_limpia` → `ALLOW`.
- Omitida: 1 (`test_consultar_devuelve_estado_controlado` sin `GOOGLE_API_KEY`). Deterministas, sin red.

## Riesgos residuales

- **Autenticación server-side:** sigue **pendiente/declarada** — la validación del token en el
  receptor requiere habilitar auth en LangGraph; `auth.validar_token` es referencia. Un allow-list
  no es autenticación.
- **Guardrails heurísticos:** detección por regex con falsos positivos/negativos conocidos (no es
  garantía absoluta contra prompt injection).
- **Conectividad entre equipos:** la validación nosotros→agente de Gustavo sigue **pendiente**
  (su `message/send` responde `-32601`); no se fabricó evidencia de esa ruta.

## Documentación/evidencias actualizadas

- `evidencias/11-robustez-48-mac.md` (sección "Ajustes finales (prompt 48a)" con salidas reales).
- `entrega/documento-entrega.md` (nota 48a en §10). `prompts_ejecutados/48a-…` + índice.

## Estado Git

- Rama: `prompt-48-robustez` (worktree `../tarea_1_curso_2-p48`). **`main` NO modificado.**
- Cambios: `src/coordinador/{a2a,catalogo,guardrails}.py`, `tests/test_ajustes_48a.py` (nuevo),
  `tests/test_guardrails_auth_48.py` (1 línea), evidencia y documento.
- Sin secretos en el diff. **Pendiente de autorización:** push de la rama.
