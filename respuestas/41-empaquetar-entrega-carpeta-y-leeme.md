<!--encabezado-grupo-->
> **Archivo:** `respuestas/41-empaquetar-entrega-carpeta-y-leeme.md`  
> **Objetivo:** Respuesta 41 · Empaquetar la entrega como carpeta en la repo + LEEME  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2322 · **Última modificación:** 20261110 2322
<!--/encabezado-grupo-->

# Respuesta 41 · Empaquetar la entrega como carpeta en la repo + LEEME

## Qué se hizo

1. **`entrega/documento-entrega.md`** completado: integrantes (Fabio Durán,
   Gustavo Reyes, Ezequiel Muñoz), repo público, tabla de la ronda real (sacada
   de `evidencias/05-ronda-mac.md`) y referencias a los nombres reales de las
   evidencias. Quedan ⟨pendiente⟩ solo el número de grupo, los blueprints de los
   compañeros y las 2 capturas manuales.
2. **`entrega/LEEME.txt`** nuevo: explica la estructura y el paso a paso tras
   deszipear (uv sync, .env, docker compose, langgraph dev, fichas, scripts).
3. **`tools/empaquetar_entrega.py`** reescrito:
   - La raíz del zip ahora es una sola carpeta con el nombre de la repo
     (`tarea_1_curso_2/`).
   - Incluye `LEEME.txt` arriba.
   - Checklist de evidencias corregido a los nombres reales
     (`02-ficha-agente_ezequiel.json`, `04-catalogo-mac.txt`, `05-ronda-mac.md`…).
   - Materializa `entrega/tarea_1_curso_2/` (versionada en la repo) con
     documento, blueprint, companeros, LEEME y evidencias/ (sin `proyecto/`, que
     es la repo entera y entra solo al zip para no duplicarla en git).

## Salida de la corrida

```
✓ Carpeta de entrega: entrega/tarea_1_curso_2/ (versionada en la repo)
✓ Zip creado: dist/grupo-N-tarea_1_curso_2.zip  (525576 bytes)
  raíz del zip: tarea_1_curso_2/ · proyecto/: 204 archivos versionados
Avisos (completar antes de entregar):
  - no hay documento-entrega.pdf; se incluyó el .md (exportar a PDF antes de entregar)
  - el documento tiene campos ⟨pendiente⟩ sin completar
  - evidencias faltantes: 01-saltos.png, 03-tunel.png
```

## Estructura del zip (raíz)

```
tarea_1_curso_2/
├── LEEME.txt
├── documento-entrega.md      (exportar a .pdf antes de entregar)
├── blueprint-ezequiel.md
├── companeros.md
├── evidencias/               (fichas JSON, catálogos y rondas Mac+Windows)
└── proyecto/                 (204 archivos versionados; sin .env ni .venv)
```

## Pendientes manuales (no bloquean el empaquetado)

- Número de grupo en el documento.
- Blueprints de Fabio y Gustavo.
- Capturas `evidencias/01-saltos.png` y `evidencias/03-tunel.png`.
- Exportar `documento-entrega.md` → `.pdf` y volver a correr el empaquetador.

## Encabezados

`aplicar_encabezados.py` → OK · 194 archivos con encabezado (incluido el LEEME).
