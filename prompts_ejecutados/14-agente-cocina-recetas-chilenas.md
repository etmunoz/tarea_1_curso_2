<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/14-agente-cocina-recetas-chilenas.md`  
> **Objetivo:** 14 · Agente de cocina chilena con costeo de recetas  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2013 · **Última modificación:** 20261110 2312
<!--/encabezado-grupo-->

# 14 · Agente de cocina chilena con costeo de recetas

**Fecha:** 2026-11-10

## Prompt

> Construir un agente de recetas de cocina con recetas clásicas chilenas (unas 20).
> Lo importante: a partir de la receta, calcular el monto que significaría producirla
> para 4 personas. En un SQLite guardar los precios de los ingredientes en función de
> las unidades que tiene la receta, para no hacer conversión, sino solo la multiplicación
> para obtener el costo por ingrediente, además del costo total y por persona.

## Verificación pedida

- ~20 recetas chilenas en SQLite; precios por la unidad usada (sin conversión).
- `costear_receta(nombre, personas=4)`: costo por ingrediente, total y por persona en CLP.
- Agente registrado e integrado (ficha + catálogo del coordinador); tests sin key.
