<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/48a-ajustes-finales-robustez.md`  
> **Objetivo:** Prompt para Claude Code — Ajustes finales de robustez en `prompt-48-robustez`  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1429 · **Última modificación:** 20261111 1438
<!--/encabezado-grupo-->

# Prompt para Claude Code — Ajustes finales de robustez en `prompt-48-robustez`

## Contexto

Trabaja en el repositorio `etmunoz/tarea_1_curso_2`, **rama `prompt-48-robustez`**. Se revisó la implementación del prompt 48 y se identificaron cinco puntos adicionales. Tu misión es **comprobar cada hallazgo contra el código actual**, corregir lo que efectivamente corresponda, incorporar pruebas de regresión y sincronizar documentación y evidencias. No reemplaces la arquitectura existente (LangGraph, Supervisor, A2A nativo, Agent Cards, Cloudflare, `uv`).

**Reglas:** Lee primero `AGENTS.md` y las convenciones del repositorio. Trabaja exclusivamente en la rama indicada y verifica el estado de Git antes de editar. No hagas merge a `main`, `push`, rebase destructivo ni cambios a servicios remotos sin autorización. No inventes evidencias ni resultados de pruebas. Evita dependencias nuevas salvo necesidad justificada. No alteres los agentes de Fabio o Gustavo. Protege credenciales y datos sensibles.

## 1. Validación exhaustiva de respuestas A2A (prioridad alta)

Archivo principal: `src/coordinador/a2a.py`.

**Hallazgo:** existen rutas de extracción de texto que presuponen estructuras concretas. Por ejemplo, `_texto_de_resultado()` utiliza `.get()` sobre `result`, y sus accesos a `status` e `history` pueden fallar si el servidor devuelve listas, cadenas, `null` u objetos inesperados. `_endpoint_clasico()` también debe validar `supportedInterfaces` y sus elementos.

**Implementa:**

1. Validación explícita del tipo raíz de JSON-RPC y de `result`, `status`, `history`, `artifacts`, `parts`, `supportedInterfaces` y los elementos anidados que realmente consume el cliente.
2. Manejo diferenciado de respuesta JSON inválida, respuesta estructuralmente inválida y error JSON-RPC remoto.
3. Conversión de errores de estructura en `RespuestaA2AInvalida` (o una excepción controlada equivalente), sin exponer trazas ni datos internos al usuario.
4. Extracción de texto estricta: no conviertas silenciosamente una respuesta malformada en `str(result)` como si fuese una respuesta válida del agente. Si el protocolo admite resultados sin texto, representa ese estado de forma explícita y controlada.
5. Compatibilidad con los dialectos A2A clásico y LangGraph actualmente soportados. No impongas campos obligatorios que sean opcionales según el dialecto sin justificarlo.

**Pruebas deterministas:** JSON raíz `[]`, `null`, cadena o número; `result` lista o escalar; `status` cadena; `history` con elementos no-dict; `supportedInterfaces` con elementos no-dict; `artifacts` malformados; error JSON-RPC; respuesta válida de ambos dialectos. Comprueba que no escapen `AttributeError`, `TypeError`, `IndexError` ni `KeyError`.

## 2. Autenticación uniforme durante descubrimiento y llamadas A2A (prioridad alta)

**Hallazgo:** `dialecto()` llama directamente a `httpx.get`, mientras `_pedir()` incorpora `Authorization` si está configurado. Un endpoint que exige autenticación puede responder `401/403` al descubrimiento y ser clasificado incorrectamente como otro dialecto.

**Implementa:**

1. Centraliza las peticiones de descubrimiento y mensajería en una capa HTTP coherente, reutilizando la política de encabezados, timeouts y excepciones controladas.
2. Diferencia claramente `401/403` (acceso denegado), errores de transporte, `404`, errores de protocolo y respuestas válidas de detección de dialecto.
3. **No** clasifiques automáticamente como LangGraph cualquier respuesta que no sea una Agent Card clásica válida.
4. Revisa la precedencia de encabezados: ningún encabezado suministrado accidentalmente debe sustituir silenciosamente la credencial configurada. Documenta cómo se selecciona el token por destino si el proyecto contempla agentes de diferentes propietarios; evita enviar un token común a endpoints arbitrarios.
5. No afirmes que hay autenticación de extremo a extremo: la validación del token en el receptor sigue pendiente salvo que exista integración real y pruebas verificables.

**Pruebas:** descubrimiento clásico y LangGraph exitosos; `401`, `403`, `404`, timeout y JSON malformado; verificación de encabezados con mocks sin imprimir secretos; comportamiento con y sin token; destino no autorizado.

## 3. Recuperación precisa del `assistant_id` obsoleto (prioridad media-alta)

**Hallazgo:** `enviar_mensaje()` invalida el identificador ante cualquier HTTP `404` del endpoint LangGraph y reintenta una vez. Un `404` podría deberse a un error distinto del identificador obsoleto.

**Implementa:**

1. Distingue, cuando el protocolo lo permita, un `assistant_id` inexistente de otros `404` mediante el cuerpo/código de error y el contexto de la solicitud.
2. Invalida únicamente la entrada `(base_url, graph)` afectada.
3. Consulta `/assistants/search` nuevamente y reintenta **como máximo una vez**, solo cuando sea seguro que la operación original no se ejecutó.
4. Si el nuevo identificador es igual al anterior o la búsqueda no devuelve uno válido, termina con error controlado y sin bucles.
5. No reintentes errores ambiguos de operaciones potencialmente no idempotentes. Documenta el criterio.

**Pruebas:** identificador renovado y éxito; identificador idéntico; búsqueda vacía; búsqueda malformada; segundo `404`; `404` no relacionado; error de transporte durante la renovación; máximo un reintento.

## 4. Semántica de disponibilidad y caché (prioridad media-alta)

Archivo principal: `src/coordinador/catalogo.py`.

**Hallazgo:** `estado()` puede inferir disponibilidad a partir de una Agent Card cacheada; eso no equivale necesariamente a una comprobación reciente de conectividad.

**Implementa:**

1. Separa claramente **capacidad conocida**, **última verificación de conectividad** y **estado actual estimado**.
2. Considera estados `disponible`, `no_disponible` y `desconocido` (o representación equivalente), con timestamp y TTL explícitos.
3. Evita que una ficha en caché se trate automáticamente como prueba de que el endpoint sigue vivo.
4. Mantén la capacidad de seleccionar a un especialista conocido aunque esté desconectado, para responder `agente_no_disponible` en lugar de `sin_agente`.
5. Define qué ocurre cuando el agente se desconecta después de ser seleccionado y cuando vuelve a estar operativo. Evita sondeos excesivos y degradación del rendimiento.
6. Revisa que el supervisor no confunda un agente **nunca descubierto** con uno conocido temporalmente caído.

**Pruebas:** caché de ficha vigente con endpoint caído; expiración del TTL de disponibilidad; agente conocido desconectado; agente nunca descubierto; reconexión; caída entre selección y envío; agentes alternativos disponibles.

## 5. Semántica correcta de ALLOW / SANITIZE / BLOCK (prioridad media)

Archivo principal: `src/coordinador/guardrails.py`.

**Hallazgo:** con la política predeterminada `SANITIZE`, una respuesta limpia puede etiquetarse como `SANITIZE` aunque su contenido no cambie. Esto dificulta la observabilidad.

**Implementa:**

1. Define el resultado en función de la **acción efectiva**, distinguiéndolo de la **política configurada**.
2. Devuelve `ALLOW` cuando la respuesta es válida, no presenta hallazgos y se entrega sin modificación.
3. Devuelve `SANITIZE` cuando se redactan secretos o se transforma/neutraliza contenido de forma efectiva.
4. Devuelve `BLOCK` cuando se descarta el contenido según la política y el tipo de riesgo.
5. Mantén la distinción entre `decision`, `motivo` y `politica_configurada` en los eventos, sin registrar texto sensible.
6. No describas los guardrails heurísticos como garantía absoluta contra prompt injection. Conserva pruebas de falsos positivos y falsos negativos conocidos.

**Pruebas:** respuesta limpia con política predeterminada → `ALLOW`; secreto redactado → `SANITIZE`; inyección sospechosa con política de bloqueo → `BLOCK`; entrada malformada → `BLOCK`; texto educativo legítimo sobre prompt injection no bloqueado indebidamente.

## 6. Revisión transversal de seguridad y consistencia

Después de implementar los cinco ajustes:

- Verifica que los errores A2A controlados no terminen ocultando indiscriminadamente errores de programación. Diferencia indisponibilidad de transporte, fallo de protocolo y autorización denegada en logs/estado interno; ofrece mensajes seguros al usuario.
- Verifica que la autenticación del receptor siga declarada como **pendiente** si no está realmente aplicada en el servidor.
- Revisa los tests existentes, en especial `tests/test_robustez_a2a_48.py`, `tests/test_guardrails_auth_48.py` y `tests/test_resiliencia_a2a.py`.
- Actualiza `evidencias/11-robustez-48-mac.md`, `entrega/documento-entrega.md`, `.env.example` y cualquier documento que describa comportamientos modificados. Conserva la trazabilidad de lo ejecutado.
- No fabriques capturas ni salidas de pruebas remotas. Si no hay acceso a los equipos de los compañeros, deja expresamente esa validación como pendiente.
- Si se regeneran PDF/ZIP, comprueba que reflejen el contenido actualizado y que no contengan secretos, `.env` ni archivos temporales.

## 7. Validación y criterios de aceptación

Ejecuta, al menos:

```bash
uv run pytest -q
uv run pytest tests/test_robustez_a2a_48.py tests/test_guardrails_auth_48.py tests/test_resiliencia_a2a.py -v
```

Ejecuta además las verificaciones de estilo/importación y compilación del grafo disponibles en el proyecto. Inspecciona el diff completo antes de finalizar.

**Criterios de aceptación:**

- Ninguna estructura JSON inesperada de los casos cubiertos produce excepciones no controladas.
- El descubrimiento A2A respeta autenticación y distingue explícitamente acceso denegado de dialecto desconocido.
- La recuperación del `assistant_id` es acotada, segura y verificable.
- La ficha cacheada no se presenta como verificación actual de conectividad.
- Una respuesta limpia se registra como `ALLOW`, no como `SANITIZE`.
- La distinción `sin_agente` / `agente_no_disponible` se conserva.
- No se rompe la interoperabilidad existente entre los dos dialectos A2A ni la arquitectura del taller.
- Las limitaciones de seguridad quedan documentadas sin exageraciones.

## 8. Informe final obligatorio

Antes de editar, entrega un **diagnóstico breve** de cuáles de los cinco hallazgos se reproducen en la versión actual y cuáles no. Luego implementa las correcciones comprobadas.

Al terminar, presenta:

1. **Matriz de hallazgos:** confirmado/no reproducido, causa raíz, archivos afectados y corrección aplicada.
2. **Resumen técnico de cambios:** funciones y contratos modificados, con explicación de compatibilidad.
3. **Resultados reales de pruebas:** comandos, aprobadas, fallidas, omitidas y limitaciones del entorno.
4. **Riesgos residuales:** especialmente autenticación server-side, guardrails heurísticos y conectividad entre equipos.
5. **Documentación/evidencias actualizadas:** archivos y artefactos regenerados.
6. **Estado Git:** rama, archivos modificados, resumen del diff y confirmación de que `main` no fue modificado.

**No hagas `push` ni `merge` sin mi autorización expresa.**
