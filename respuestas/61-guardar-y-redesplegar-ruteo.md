<!--encabezado-grupo-->
> **Archivo:** `respuestas/61-guardar-y-redesplegar-ruteo.md`  
> **Objetivo:** 61 · Respuesta — Guardar el ruteo por respuesta y botón para re-desplegarlo  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1655 · **Última modificación:** 20261112 1655
<!--/encabezado-grupo-->

# 61 · Respuesta — Guardar y re-desplegar el ruteo

Prompt: [`../prompts_ejecutados/61-guardar-y-redesplegar-ruteo.md`](../prompts_ejecutados/61-guardar-y-redesplegar-ruteo.md)

## Cambios en `tools/coordinador_web.py` (frontend)

- **`botonChat(txt, fn)`**: helper para los botones de acción de cada burbuja (mismo estilo).
- **`burbuja(cls, texto, nombre, d)`**: ahora recibe el ruteo `d`. Para respuestas del bot agrega una
  fila de acciones con **🧭 Ver ruteo** (si hay `ruta`/`elegido`) → `pintarRuteo(d)`, y **✉️ Enviar
  por correo** (si el correo está configurado). Antes el panel derecho se perdía al preguntar de
  nuevo; ahora cada respuesta lo puede volver a mostrar.
- **Historial persistente**: `historial[]` + `guardarHist()`/`restaurarHist()` en **`sessionStorage`**
  por `thread` (clave `coord_hist_<thread>`, últimas 60 entradas). En cada turno se guarda
  `{rol, texto, nombre, d}`. Al cargar la página se re-renderiza la conversación y se re-despliega el
  **último** ruteo.
- **`nuevaConversacion()`** limpia `historial` además del chat/ruteo; **🚪 Salir** limpia la sesión.
- Texto de ayuda en el estado vacío del panel: «Cada respuesta guarda su ruteo: toca 🧭 Ver ruteo…».

## Verificación

- `py_compile` OK.
- Desplegado en el VPS (`git reset --hard` + `systemctl restart agente-coordinador`, `active`).
- La página servida contiene el nuevo JS (`Ver ruteo` / `restaurarHist` / `botonChat` presentes).
- Prueba manual (navegador): varias preguntas → cada respuesta muestra 🧭 Ver ruteo; al tocarla se
  re-despliega su ruteo a la derecha; al recargar el tab se restauran conversación y último ruteo.

## Refinamiento (feedback del usuario)

Cuando el supervisor **no deriva** (respuesta "ninguno / sin agente"), el cuadro "Antecedentes del acceso" desaparecía y el panel quedaba inconsistente. Ahora `pintarRuteo` muestra igual el cuadro con el texto «No se consultó ningún agente — el supervisor respondió directamente (sin acceso externo)», para que no se "pierda".

## Archivos tocados

- `tools/coordinador_web.py` — `botonChat`, `burbuja(…, d)`, historial en `sessionStorage`,
  `restaurarHist()` al cargar, reset en `nuevaConversacion`.
- `prompts_ejecutados/61-…md` y `respuestas/61-…md` (este registro).

## Estado

- Commit `5352b8d`, desplegado en `https://coordinador.etmk.cl`.

## Pendientes

- La persistencia es por sesión del tab (`sessionStorage`); si se quisiera entre sesiones/dispositivos
  habría que persistir del lado del servidor (no pedido).
- Regenerar el zip de entrega (registros 60/61) cuando se pida.
- Housekeeping: revocar el sudo temporal (`sudo rm /etc/sudoers.d/90-administrator-nopasswd`).
