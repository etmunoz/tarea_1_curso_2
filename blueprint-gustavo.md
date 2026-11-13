<!--encabezado-grupo-->
> **Archivo:** `blueprint-gustavo.md`  
> **Objetivo:** Blueprint · Agente de Gustavo  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2334 · **Última modificación:** 20261112 2158
<!--/encabezado-grupo-->

# Blueprint · Agente de Gustavo Reyes

> Completado por **Gustavo Reyes** (agente meteorólogo). Transcrito de su blueprint.

| Qué definir | Mi agente |
|-------------|-----------|
| Quién soy | Agente meteorólogo |
| Hace | Entrega el estado del clima por ciudad y puede hacer pronóstico del tiempo para hoy o para la semana, solo para las ciudades de **Santiago, Concepción y Valdivia**. |
| No hace | No entrega pronóstico para otras ciudades que no sean las mencionadas, ni pronósticos del clima que excedan 7 días en el futuro. |
| Herramientas | `pronostico_hoy(ciudad:str)`: devuelve el pronóstico del tiempo para hoy dada una ciudad · `pronostico_semana(ciudad:str)`: devuelve el pronóstico del tiempo para la semana dada una ciudad |
| Decide solo | A partir de la ciudad y el plazo (hoy / semana), decide qué herramienta usar. |
| Nunca sin persona | — |
| Deriva a otro | Cuando la pregunta no es de meteorología (o es de otra ciudad / plazo mayor a 7 días) → lo dice en una frase y no responde. |
| Dónde se ejecuta | `http://127.0.0.1:8003` · `src/agente_meteorologo/` · `python main.py meteorologo "¿Cuál es el pronóstico del tiempo para Santiago el día de hoy?"` |
| Dirección pública | `https://forest-optical-distributors-trinity.trycloudflare.com` (túnel de Cloudflare, efímero) |

## Herramientas · de dónde salen los datos

- `pronostico_hoy(ciudad)` — pronóstico (ficticio) del clima de hoy para Santiago, Concepción o Valdivia.
- `pronostico_semana(ciudad)` — pronóstico (ficticio) de los próximos 7 días para esas mismas ciudades.

## Ficha / Agent Card (Paso 5)

- **name:** `agente_meteorologo`
- **description:** Entrega pronósticos (ficticios) del clima de hoy y de los próximos siete días para
  Santiago, Concepción y Valdivia, con temperaturas y condiciones. No responde fuera de la
  meteorología ni para otras ciudades o plazos mayores a siete días.
- **skills:** "Clima de hoy", "Clima semanal".

> Interoperación con nuestro coordinador: su dialecto A2A es el clásico del SDK a2a-protocol.org
> (método `SendMessage`); el detalle está en [`entrega/companeros.md`](entrega/companeros.md).
