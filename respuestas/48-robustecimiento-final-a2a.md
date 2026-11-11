<!--encabezado-grupo-->
> **Archivo:** `respuestas/48-robustecimiento-final-a2a.md`  
> **Objetivo:** Respuesta 48 · Robustecimiento final del Taller A2A (5 correcciones)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1410 · **Última modificación:** 20261111 2016
<!--/encabezado-grupo-->

# Respuesta 48 · Robustecimiento final del Taller A2A (5 correcciones)

Prompt: [`../prompts_ejecutados/48-robustecimiento-final-a2a.md`](../prompts_ejecutados/48-robustecimiento-final-a2a.md)

> **Rama aislada `prompt-48-robustez`** (git worktree), para no perjudicar la demo con
> Gustavo que corre en `main`. **No se hizo push** (el prompt lo pide explícitamente):
> espera autorización.

## A. Resumen ejecutivo

Se corrigieron las **5 áreas** pedidas, manteniendo la arquitectura (LangGraph, supervisor,
A2A nativo, descubrimiento por Agent Card, config por entorno). Todo con pruebas deterministas.

- **Corregido y verificado:** distinción inexistente/desconectado; guardrails por capas con
  política ALLOW/SANITIZE/BLOCK y observabilidad; robustez del cliente A2A (validación JSON,
  jerarquía de excepciones, recuperación de assistant_id obsoleto); autorización por mínimo
  privilegio; token Bearer en el cliente.
- **Abierto / límite honesto:** la **autenticación fuerte** necesita validar el token en el
  RECEPTOR (custom auth de LangGraph); se deja como referencia + modo demo (no se simula
  resuelto). La detección de inyección sigue siendo heurística (no infalible). La memoria del
  hilo (`InMemorySaver`) no persiste entre reinicios.

## B. Matriz de cambios

| Problema | Archivos | Solución | Pruebas | Estado |
|---|---|---|---|---|
| 1 · Inexistente vs desconectado | `catalogo.py`, `graph.py`, `prompts.py` | última ficha conocida (capacidades) + estado de disponibilidad; el supervisor elige al especialista caído → `agente_no_disponible` | `test_robustez_a2a_48.py` (C1) | ✅ |
| 2 · Guardrails por capas | `guardrails.py`, `graph.py` | tipos+normalización; política ALLOW/SANITIZE/BLOCK; observabilidad `registrar_evento` | `test_guardrails_auth_48.py` (C2) | ✅ (límite heurístico declarado) |
| 3 · Auth/authz A2A | `auth.py` (nuevo), `a2a.py`, `graph.py` | autorización mínimo privilegio + Bearer cliente; validación server-side de referencia | `test_guardrails_auth_48.py` (C3) | ◑ verificable; authn fuerte = referencia |
| 4 · Robustez cliente A2A | `a2a.py` | jerarquía `ErrorA2A`; validación estructural JSON; timeouts conn/read; recuperación assistant_id (404→recargar→1 reintento) | `test_robustez_a2a_48.py` (C4) | ✅ |
| 5 · Docs/evidencias | `documento-entrega.md`, `.env.example`, `evidencias/11-…` | sincronizadas con el código; PDF regenerado | — | ✅ |

## C. Resultados de pruebas

```
$ uv run pytest -q
110 passed, 1 skipped
```

- Aprobadas: **110** · Falladas: **0** · Omitidas: **1** (`test_consultar_devuelve_estado_controlado`
  solo si no hay `GOOGLE_API_KEY` exportada; con clave, corre).
- Nuevas: `test_robustez_a2a_48.py` (11), `test_guardrails_auth_48.py` (19). Deterministas, sin red.
- Entorno: worktree con `.env` copiado (clave local); Redis/langgraph de `main` no se tocan.

## D. Seguridad

- **Implementados y verificados:** allow-list de agentes; autorización por operación (mínimo
  privilegio); guardrails de entrada (tipos, tamaño, inyección), salida (redacción, longitud,
  tipos) y A2A (política + separación instrucción/dato por FLUJO, no solo texto); recuperación
  controlada de `assistant_id` sin bucles; token Bearer adjuntado por el cliente; tokens nunca
  en logs (enmascarados) ni en el repo (entorno).
- **Implementados pero no validados integralmente:** validación server-side del token
  (`auth.validar_token`) — es referencia; exigirla requiere habilitar auth en el receptor.
- **Riesgos residuales:** detección de inyección por regex (falsos positivos/negativos posibles);
  sin autenticación fuerte extremo-a-extremo en modo demo; memoria no persistente.
- **Mejoras futuras:** custom auth de LangGraph + mTLS/named tunnel; clasificador ML para
  inyección/PII; checkpointer persistente.

## E. Documentación actualizada

- `entrega/documento-entrega.md` §10 (sub-sección "Robustecimiento final").
- `.env.example` (nuevas variables: `A2A_TOKEN`, `A2A_TOKENS_VALIDOS`, `A2A_AGENTES_PERMITIDOS`,
  `A2A_OPERACIONES_PERMITIDAS`, `A2A_IDENTIDADES`, `GUARDRAIL_POLITICA_A2A`, timeouts…).
- `evidencias/11-robustez-48-mac.md` (comportamientos con salidas reales).

## F. Git

- Rama: `prompt-48-robustez` (worktree `../tarea_1_curso_2-p48`), **sin push**.
- Cambios vs `main`: `src/coordinador/{a2a,catalogo,graph,guardrails,prompts}.py`, nuevo
  `src/coordinador/auth.py`, 2 archivos de test nuevos, `documento-entrega.md`, `.env.example`,
  `evidencias/11-…`. ~807 inserciones.
- El grafo compila; imports OK; sin secretos en el diff.

**Siguiente paso (requiere tu autorización):** `git push` de la rama y/o merge a `main`.

## G. Decisión de entrega (documentado)

- **Push:** se empuja **solo la rama `prompt-48-robustez`** a GitHub; **NO se mergea ni se
  pushea a `main`** por decisión del grupo: hay que esperar a que Gustavo pruebe su endpoint y
  a que **nosotros accedamos a su agente** para sacar esa evidencia antes de integrar.
- **`main` queda intacto** sirviendo la demo con Gustavo (el puente A2A clásico y el
  `langgraph dev` siguen corriendo desde el directorio principal).
- **Pendiente para integrar a `main`:** (1) evidencia del sentido nosotros→Gustavo cuando su
  `message/send` funcione; (2) merge de esta rama; (3) regenerar carpeta de entrega/zip desde
  `main` (toman el nombre correcto `tarea_1_curso_2/`).
- **Nota de índice:** en `main` la fila 48 de `prompts_ejecutados/README.md` se coló en el
  commit 49 y su respuesta vive en esta rama; se resuelve al mergear.
