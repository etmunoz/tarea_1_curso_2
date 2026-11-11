<!--encabezado-grupo-->
> **Archivo:** `respuestas/48b-seguridad-interop-puente.md`  
> **Objetivo:** Respuesta 48b · Refuerzos de seguridad sobre la interoperabilidad (49 + Gustavo)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1438 · **Última modificación:** 20261111 1738
<!--/encabezado-grupo-->

# Respuesta 48b · Refuerzos de seguridad sobre la interoperabilidad (49 + Gustavo)

Prompt: [`../prompts_ejecutados/48b-seguridad-interop-puente.md`](../prompts_ejecutados/48b-seguridad-interop-puente.md)

> Rama `prompt-48-robustez`. **`main` no modificado.**

## Diagnóstico (¿se reproducen los hallazgos?)

| # | Hallazgo | ¿Reproducido? | Causa raíz |
|---|---|---|---|
| 1 | Puente sin guardrails ni auth | **Sí** | `servidor.py` aceptaba `message/send` público sin revisar entrada ni redactar salida, sin token |
| 2 | Token enviado a endpoints arbitrarios | **Sí** | `_pedir` adjuntaba `A2A_TOKEN` a TODA petición (incl. el túnel de Gustavo) |
| 3 | El puente podía filtrar trazas | **Sí (potencial)** | excepción no controlada en `http.server` → 500 con traceback |
| 4 | Respuestas clásicas como dato no confiable | **No (ya cubierto)** | el coordinador ya saneaba toda respuesta remota en `consultar` (dialecto-agnóstico) |

## Correcciones aplicadas

1. **Guardrails en el puente (`src/puente_a2a/servidor.py`):** ahora el puente aplica el
   guardrail de **ENTRADA** (bloquea vacías/largas/inyección con `-32602` + mensaje controlado) y
   el de **SALIDA** (redacta credenciales / limita longitud) a lo que entra y sale por el túnel
   público. Token opcional `PUENTE_TOKEN` (exige `Authorization: Bearer`; `401` si falta). La card
   queda **pública** para descubrimiento.
2. **Token por destino (`auth.token_para`, `encabezados_auth(url)`):** nuestro `A2A_TOKEN` se
   envía **solo** a hosts confiables (`A2A_BASE` + `A2A_HOSTS_CONFIABLES` + localhost); a un
   endpoint de tercero (Gustavo) **no** se adjunta. `a2a._pedir` ya selecciona por destino.
3. **Catch-all en el puente:** `do_GET`/`do_POST` envuelven todo; ante cualquier error interno
   devuelven un mensaje seguro (`error interno del puente`), **nunca un traceback**.
4. **Verificado:** las respuestas de agentes clásicos (como el de Gustavo) ya pasan por
   `evaluar_respuesta_remota` en el coordinador (política ALLOW/SANITIZE/BLOCK); se añadió prueba.

## Resumen técnico

- `auth.py`: `_hosts_confiables()`, `token_para(url)`, `encabezados_auth(url)` (compatible: sin
  `url` usa el token global).
- `a2a._pedir`: adjunta el token **por destino**.
- `puente_a2a/servidor.py`: guardrails de entrada/salida, `PUENTE_TOKEN`, `_token_ok`, catch-all.
- Compatibilidad: el puente sigue sirviendo a un cliente A2A clásico (Gustavo); sin dependencias
  nuevas; el grafo compila.

## Resultados reales de pruebas

```
$ uv run pytest tests/test_seguridad_48b.py -q
8 passed

$ uv run pytest -q
141 passed, 1 skipped
```

Nuevas: `tests/test_seguridad_48b.py` (8: token por destino, no-fuga a tercero, puente bloquea
inyección, redacta secreto, exige token, no filtra trazas, card pública). Actualizada:
`test_cliente_adjunta_bearer` (host confiable). Deterministas (puente real + langgraph simulado).

## Riesgos residuales

- **Autenticación server-side del langgraph propio:** sigue **pendiente** (el `PUENTE_TOKEN`
  protege el puente, pero el `langgraph dev` detrás no exige token por sí mismo).
- **Rate limiting / DoS en el puente:** no implementado (límite declarado).
- **Guardrails heurísticos:** falsos +/− conocidos.
- **Nosotros→Gustavo:** **pendiente** por su `-32601`; no se fabricó evidencia de esa ruta.

## Documentación/evidencias

- `evidencias/11-robustez-48-mac.md` (sección "Refuerzos de seguridad… prompt 48b", salidas reales).
- `.env.example` (`A2A_HOSTS_CONFIABLES`, `PUENTE_TOKEN`). `prompts_ejecutados/48b-…` + índice.

## Estado Git

- Rama `prompt-48-robustez` (worktree). **`main` NO modificado.**
- Cambios: `src/coordinador/{auth,a2a}.py`, `src/puente_a2a/servidor.py`,
  `tests/test_seguridad_48b.py` (nuevo), `tests/test_guardrails_auth_48.py` (1 línea),
  `.env.example`, evidencia. Sin secretos en el diff.
