<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/58-ruteo-sin-acumular-y-salida.md`  
> **Objetivo:** 58 · Ruteo muestra solo los pasos de la pregunta actual + botones Nueva conversación y Salir  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1558 · **Última modificación:** 20261112 1558
<!--/encabezado-grupo-->

# 58 · Ruteo sin acumular + salida/reset

**Fecha:** 2026-11-12 · **Equipo:** VPS `coordinador.etmk.cl`

Respuesta: [`../respuestas/58-ruteo-sin-acumular-y-salida.md`](../respuestas/58-ruteo-sin-acumular-y-salida.md)

## Instrucciones del usuario (textual)

1. > "no entiendo el por qué se da tantas vueltas el ruteo de la derecha."
2. > "la app de coordinador no tiene una salida o exit o quit"

## Qué se hizo

- **Causa de las "vueltas":** en el grafo coordinador, el campo `ruta` usa el reductor
  `operator.add` (concatena) y el coordinador corre con un `InMemorySaver` (checkpointer) y el
  `thread_id` fijo por sesión → cada pregunta **sumaba** sus pasos a los anteriores. El panel
  mostraba la ruta acumulada de toda la sesión, no la de la consulta.
- **Fix:** el backend (`_preguntar`) mide cuántos pasos había antes en el estado del thread
  (`get_state`) y devuelve **solo los pasos nuevos** de la pregunta actual.
- **Salida/reset:** se agregaron dos botones a la barra:
  - 🔄 **Nueva conversación**: reinicia el `thread` y limpia chat + ruteo.
  - 🚪 **Salir**: limpia la sesión e intenta cerrar el Basic Auth (con el caveat de que el logout
    de Basic Auth no es 100% confiable entre navegadores).
