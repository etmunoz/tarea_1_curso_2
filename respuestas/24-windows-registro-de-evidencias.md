<!--encabezado-grupo-->
> **Archivo:** `respuestas/24-windows-registro-de-evidencias.md`  
> **Objetivo:** 24 · Respuesta — Windows: dejar registro de prompts y resultados  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2208 · **Última modificación:** 20261111 0743
<!--/encabezado-grupo-->

# 24 · Respuesta — Windows: dejar registro de prompts y resultados

Prompt: [`../prompts_ejecutados/24-windows-registro-de-evidencias.md`](../prompts_ejecutados/24-windows-registro-de-evidencias.md)

## Qué se hizo

- Se siguió la convención existente (`prompts_ejecutados/NN-slug.md` + `respuestas/NN-slug.md`,
  encabezado de grupo de `CONVENCIONES.md`) y se registraron los prompts de la sesión en Windows:

| # | Tema | Resultado |
|---|---|---|
| 21 | Clonar y leer instrucciones | ✓ clonado; riesgos detectados (BOM, ExecutionPolicy) |
| 22 | Ejecutar `setup_windows.ps1` | ✓ con arreglos: clave casi sobrescrita, SSL por AVG → excepción |
| 23 | Puerto de Redis | ✓ 6380/8002 configurable; RAG con 9 fragmentos |
| 24 | Este registro | ✓ |

- Se actualizó el índice [`../prompts_ejecutados/README.md`](../prompts_ejecutados/README.md).
- De aquí en adelante, cada prompt de la sesión en Windows se registra igual (25, 26, …).

## Estado

Registro al día. Cambios aún **sin commit** (decisión del usuario).

---

## Respuesta completa del asistente (chat)

### Mensaje de avance (traducido)

> Los archivos de registro están escritos y el índice actualizado. Reviso los encabezados con
> la herramienta del proyecto y guardo tu preferencia en mi memoria.

### Respuesta final

> Dejé registrada la sesión en Windows con el mismo formato que ya usa el repo: por cada
> prompt hay un archivo en `prompts_ejecutados/` y su respuesta en `respuestas/`, con el mismo número.
>
> | # | Prompt | Qué registra |
> |---|---|---|
> | 21 | Clonar y leer instrucciones | Clon del repo, herramientas ya instaladas, riesgos que vi antes de ejecutar: los `.ps1` sin BOM y la política de ejecución. |
> | 22 | Ejecutar setup | Lo que pasó en orden: el Enter vacío que habría borrado la clave, la prueba de Gemini que quedó reintentando, el error SSL causado por AVG y la excepción que agregaste. |
> | 23 | Puerto de Redis | El choque con `redis-rag`, por qué no lo reutilicé (la carga del RAG habría borrado su índice `reiki`), el cambio a 6380/8002 y la carga del RAG con 9 fragmentos. |
> | 24 | Registro de evidencias | Este pedido y el resumen de los cuatro prompts. |
>
> Cada respuesta separa **lo bueno**, **lo malo o lo que no resultó** y **lo que se arregló**.
> También anota lo que sigue pendiente:
> - `setup_windows.ps1` no debería sobrescribir la clave cuando la respuesta viene vacía.
> - La guía debería mencionar los antivirus que revisan el tráfico HTTPS.
> - En `.env.example` hay tres líneas `REDIS_URL` repetidas.
> - Los `.ps1` siguen sin BOM.
>
> Por seguridad, la clave no aparece en ningún archivo.
>
> Además:
> - Actualicé el índice `prompts_ejecutados/README.md`.
> - Pasé la revisión de encabezados del proyecto: los 150 archivos tienen su encabezado.
> - Guardé en mi memoria que en este proyecto debo registrar cada prompt a medida que
>   avanzamos. Desde el próximo lo haré sin que me lo recuerdes, empezando por el 25.
