<!--encabezado-grupo-->
> **Archivo:** `respuestas/01-extraer-taller-a-markdown.md`  
> **Objetivo:** 01 · Respuesta — Extraer el taller A2A a Markdown  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1620 · **Última modificación:** 20261110 2325
<!--/encabezado-grupo-->

# 01 · Respuesta — Extraer el taller A2A a Markdown

Prompt: [`../prompts_ejecutados/01-extraer-taller-a-markdown.md`](../prompts_ejecutados/01-extraer-taller-a-markdown.md)

## Qué se hizo

Se escribió el extractor `tools/extraer_clase.py` (en el proyecto
[`descargaweb`](https://github.com/etmunoz/descargaweb)) que separa las slides
(`<section class="slide">`) de una clase html y las convierte a Markdown (tablas,
listas, bloques de código, eyebrow separado). Se corrió sobre la clase del taller
y la salida quedó en `taller-a2a/`.

```bash
python3 tools/extraer_clase.py descargas/sitio sf8f5c9 61408ca1 --out tarea_1_curso_2/taller-a2a
```

## Salida

```text
taller-a2a/
  01-lo-que-vamos-a-armar-y-entregar.md
  02-el-blueprint-de-tu-agente.md
  03-mi-agente-con-mi-skill.md
  04-probarlo-solo-antes-de-conectarlo.md
  05-la-ficha-es-tu-curriculum.md
  06-salir-a-internet-con-cloudflare.md
  07-sumar-a-los-companeros.md
  08-la-ronda-de-preguntas.md
  09-entrega-y-evaluacion.md
  10-tres-ideas-para-seguir.md
  index.md
  clase.html
```

Páginas 8 y 9 con tablas Markdown correctas (ronda y rúbrica de evaluación); los
dos prompts largos (prompt 1 y prompt 2) quedaron intactos dentro de sus fences.

## Estado

Hecho y verificado (lectura de las 10 páginas completa).
