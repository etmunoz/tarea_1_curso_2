<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/47-guardrail-salida-y-allowlist.md`  
> **Objetivo:** Prompt 47 · Guardrail de salida completo + allow-list de agentes (tools permitidas)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1204 · **Última modificación:** 20261111 1410
<!--/encabezado-grupo-->

# Prompt 47 · Guardrail de salida completo + allow-list de agentes (tools permitidas)

**Pedido (redactado a partir de la consulta del usuario):**

> Ya tenemos un guardrail de **entrada** (nodo `guardia_entrada`), pero el de **salida**
> quedó parcial: solo redacta secretos y solo en el nodo `consultar`. Quiero cerrar dos
> cosas en el coordinador:
>
> 1. **Guardrail de salida de verdad.** Un nodo dedicado `guardia_salida`, al final del
>    grafo, por el que pasen **todas** las respuestas (las de `consultar`, las de
>    `sin_agente` y el aviso de `guardia_entrada`). Que aplique las restricciones de
>    salida: redactar credenciales/datos sensibles, poner un tope de longitud y evitar
>    respuestas vacías. La idea es que ninguna respuesta salga del coordinador sin pasar
>    por este control, no solo la de un agente.
>
> 2. **Lista de tools permitidas (allow-list de agentes).** Los "tools" del coordinador son
>    los agentes que puede invocar. Hoy el catálogo se arma desde `A2A_GRAFOS_LOCALES` +
>    `URLS_AGENTES`, lo que ya es un allow-list implícito, pero quiero uno **explícito**:
>    una variable (p. ej. `A2A_AGENTES_PERMITIDOS`) que, si está definida, acote qué
>    grafos entran al catálogo, de modo que aunque alguien configure mal `URLS_AGENTES`
>    o intente colar un túnel, solo corran los agentes aprobados. Si no se define, se
>    permiten todos (compatibilidad hacia atrás).
>
> Impleméntalo, registra la salida bien completa, haz **pruebas extensas** con pytest para
> la robustez, genera las **evidencias**, actualiza lo que haya que actualizar (diagramas,
> docs), commitea y pushea, genera el empaquetado y vuelve a commitear y pushear, y reporta.

**Tareas:**
1. `guardrails.py`: `revisar_salida` (redacción + tope `GUARDRAIL_MAX_SALIDA` + no vacío).
2. `graph.py`: nodo `guardia_salida` común; todos los caminos terminan en él.
3. `catalogo.py`: `A2A_AGENTES_PERMITIDOS` (allow-list) aplicado en `construir_catalogo`.
4. Tests extensos (`tests/test_salida_y_allowlist.py`).
5. Evidencia (`06-robustez-mac.md` §4 salida, §5 allow-list) + diagrama del grafo actualizado.
