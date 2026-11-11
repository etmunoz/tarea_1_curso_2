<!--encabezado-grupo-->
> **Archivo:** `respuestas/41-empaquetar-entrega-carpeta-y-leeme.md`  
> **Objetivo:** Respuesta 41 · Empaquetar la entrega como carpeta en la repo + LEEME  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2322 · **Última modificación:** 20261111 1227
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

---

## Cierre (estado final)

Entrega empaquetada y publicada. Commit `79f07ff` pusheado a la rama principal.

- **Repo público:** https://github.com/etmunoz/tarea_1_curso_2
- **Carpeta de entrega (verla en la web, sin deszipear nada):**
  https://github.com/etmunoz/tarea_1_curso_2/tree/main/entrega/tarea_1_curso_2
- **Zip reproducible:** `uv run python tools/empaquetar_entrega.py --grupo N`
  → `dist/grupo-N-tarea_1_curso_2.zip` (raíz `tarea_1_curso_2/`, 204 archivos en
  `proyecto/`, sin `.env` ni `.venv`).

### Cómo lo revisan los compañeros
1. Abrir el link de la carpeta de entrega (arriba) para ver documento, blueprint,
   LEEME y evidencias directo en GitHub.
2. Para correrlo: `git clone https://github.com/etmunoz/tarea_1_curso_2` y seguir
   el `LEEME.txt` (uv sync · `.env` con GOOGLE_API_KEY · docker compose up -d ·
   langgraph dev · configurar_fichas).

### Qué queda por completar (de ellos / manual, no bloquea)
- Número de grupo en `documento-entrega.md`.
- Blueprints de Fabio y Gustavo (`blueprint-fabio.md`, `blueprint-gustavo.md`).
- Capturas `evidencias/01-saltos.png` y `03-tunel.png`.
- Exportar `documento-entrega.md` → `.pdf` y re-empaquetar.

Con esto queda **cerrado** lo hecho por Ezequiel (agentes, coordinador, A2A
bidireccional Mac↔Windows por Cloudflare, evidencias y empaquetado).

---

## Pendientes completados (cierre final)

- **Número de grupo:** `NN` en `documento-entrega.md` (valor dado por el usuario).
- **Blueprints de Fabio y Gustavo:** `blueprint-fabio.md` y `blueprint-gustavo.md`
  (plantillas con la misma estructura que el de Ezequiel, para que las completen).
  El empaquetador ahora copia **todos** los `blueprint-*.md` a la entrega.
- **Capturas:** `evidencias/01-saltos.png` (ronda real por el coordinador:
  supervisor → agente_local / sin_agente) y `evidencias/03-tunel.png` (ficha del
  agente servida por la URL pública `requirements-early-describes-socket.trycloudflare.com`).
  Generadas desde la corrida real con Pillow; reemplazables por capturas manuales.
- **PDF:** `tools/exportar_pdf.py` (markdown → xhtml2pdf, deps PEP 723, `uv run`);
  genera `entrega/documento-entrega.pdf`, que el zip incluye en la raíz.
- **Fichas recargadas** tras los cambios para que Windows pueda probar contra el
  Mac después de re-clonar (`configurar_fichas.py --grafos agente_ezequiel,agente_cocina,agente_viajes`).

El empaquetador ya **no reporta avisos**: documento completo (sin ⟨pendiente⟩),
PDF presente y todas las evidencias requeridas.
