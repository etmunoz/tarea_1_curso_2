<!--encabezado-grupo-->
> **Archivo:** `respuestas/11-esqueleto-entrega.md`  
> **Objetivo:** 11 · Respuesta — Esqueleto de entrega y empaquetador  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1941 · **Última modificación:** 20261110 2124
<!--/encabezado-grupo-->

# 11 · Respuesta — Esqueleto de entrega y empaquetador

Prompt: [`../prompts_ejecutados/11-esqueleto-entrega.md`](../prompts_ejecutados/11-esqueleto-entrega.md)

## Archivos creados

- `entrega/documento-entrega.md` — borrador del documento con las 10 secciones de la
  rúbrica (identificación, blueprints, agente, probarlo solo, ficha, túnel, coordinador,
  ronda, cómo correr, evidencias). Campos en vivo marcados ⟨pendiente⟩.
- `entrega/companeros.md` — plantilla por agente ajeno (nombre, skill, URL, grafo, ficha JSON).
- `evidencias/README.md` — qué debe mostrar cada captura y cómo producirla.
- `tools/empaquetar_entrega.py` — arma el zip con `git ls-files` (así `proyecto/` nunca
  incluye `.env`/`.venv`); documento/blueprint/companeros/evidencias en la raíz del zip.
- `.gitignore` — ignora `dist/`. `plan.json` — grupo `entrega` (z01). ROADMAP: 3.3 🟡.

## Salida de la verificación

```text
$ uv run python tools/empaquetar_entrega.py --grupo 1
✓ Zip creado: dist/grupo-1-taller-a2a.zip  (317235 bytes)
  proyecto/: 93 archivos versionados
Avisos (completar antes de entregar):
  - no hay documento-entrega.pdf; se incluyó el .md (exportar a PDF antes de entregar)
  - el documento tiene campos ⟨pendiente⟩ sin completar
  - evidencias faltantes: 01-saltos.png, 02-ficha.json, 03-tunel.png, 04-catalogo.png, 05-ronda.png

# estructura (raíz del zip):
documento-entrega.md · blueprint-ezequiel.md · companeros.md · evidencias/ · proyecto/…

# seguridad:
$ unzip -l dist/grupo-1-taller-a2a.zip | grep -i '\.env' | grep -v '.env.example'
(ningún .env — solo .env.example)
```

## Qué falta para la entrega final

- Completar los ⟨pendiente⟩ del documento (identificación completa, ficha, túnel, ronda).
- Generar las 5 evidencias (PNG/JSON) en la corrida en vivo.
- Exportar `documento-entrega.md` → `documento-entrega.pdf` (el empaquetador lo prefiere si existe).
- Completar `companeros.md` con los túneles de Fabio y Gustavo.

## Estado

Esqueleto de entrega ✅ y empaquetador funcionando 🟡 (zip se arma; falta el contenido en vivo).
