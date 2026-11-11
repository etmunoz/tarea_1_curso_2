<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/45-forzar-estado-controlado-end-to-end.md`  
> **Objetivo:** Prompt 45 · Forzar el estado controlado end-to-end (remoto caído)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 0735 · **Última modificación:** 20261111 2016
<!--/encabezado-grupo-->

# Prompt 45 · Forzar el estado controlado end-to-end (remoto caído)

**Pedido del usuario (textual):**

> Fuerza ese camino end-to-end y deja la evidencia. Esto debe quedar en otro
> prompt y su resultado correspondiente.

**Contexto:** en el prompt 44, con Windows caído, el supervisor evitaba al agente
marcado "(no disponible ahora)" y enrutaba a `sin_agente`; el estado controlado solo
se veía en la llamada A2A directa. Aquí se fuerza el camino completo por el coordinador.

**Tarea:** hacer que el supervisor ELIJA al agente remoto y choque al consultar, para
capturar end-to-end la ruta `supervisor → agente_no_disponible` y el mensaje
controlado. Se logra sembrando la ficha del remoto en la caché `CARD_TTL` (simula el
caso real: el agente estaba arriba, su ficha quedó cacheada, y se cayó justo antes de
consultar). Nueva sección `_seccion_forzado` en `tools/evidencia_robustez.py`.
