<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/61-guardar-y-redesplegar-ruteo.md`  
> **Objetivo:** 61 · Guardar el ruteo de cada respuesta y botón para re-desplegarlo en el panel  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1655 · **Última modificación:** 20261112 1655
<!--/encabezado-grupo-->

# 61 · Guardar y re-desplegar el ruteo por respuesta

**Fecha:** 2026-11-12 · **Equipo:** VPS `coordinador.etmk.cl`

Respuesta: [`../respuestas/61-guardar-y-redesplegar-ruteo.md`](../respuestas/61-guardar-y-redesplegar-ruteo.md)

## Instrucción del usuario (textual)

> "sabes que el chat del coordinador en la VPS pierde lo de la derecha, sería una buena idea el que
> se guardara y que si toco un botoncito en el[la] la respuesta del chat, se volviese a desplegar
> nuevamente, al menos en la misma sesión en que estamos."

## Qué se hizo

- El panel derecho ("Ruteo del coordinador") se pisaba con cada nueva pregunta → se perdía el ruteo
  anterior. Ahora cada respuesta **guarda su ruteo** (ruta/elegido/motivo/destino) y trae un botón
  **🧭 Ver ruteo** que lo vuelve a desplegar a la derecha.
- La conversación (burbujas + ruteo de cada una) se persiste en **`sessionStorage`** por `thread`, así
  que sobrevive recargas del tab (misma sesión). Al cargar se restaura y se muestra el último ruteo.
- **🔄 Nueva conversación** limpia el historial; **🚪 Salir** limpia la sesión.
