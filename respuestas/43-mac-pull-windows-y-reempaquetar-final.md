<!--encabezado-grupo-->
> **Archivo:** `respuestas/43-mac-pull-windows-y-reempaquetar-final.md`  
> **Objetivo:** Respuesta 43 · Mac: integrar evidencias de Windows y reempaquetar la entrega final  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2349 · **Última modificación:** 20261110 2349
<!--/encabezado-grupo-->

# Respuesta 43 · Mac: integrar evidencias de Windows y reempaquetar la entrega final

## Qué se hizo

1. **`git pull --rebase`** (fast-forward `5a80f5d..4c89013`): llegó el **prompt 42**
   de Windows con las evidencias finales:
   - `evidencias/04-catalogo-windows.txt` y `05-ronda-windows.md` (y sus copias en
     `entrega/tarea_1_curso_2/`).
2. **Evidencia bidireccional completa** (espejo entre equipos):
   - **Mac** (`05-ronda-mac.md`): Ezequiel y cocina **locales**; Tomás **remoto**
     por el túnel Cloudflare del Windows.
   - **Windows** (`05-ronda-windows.md`): Tomás **local**; Ezequiel y cocina
     **remotos** por el túnel Cloudflare del Mac.
   - Ambos enrutan bien por ficha y rechazan lo fuera de dominio (`sin_agente`).
3. **Reempaquetado final**: `tools/empaquetar_entrega.py --grupo NN` regeneró la
   carpeta versionada `entrega/tarea_1_curso_2/` y `dist/grupo-NN-tarea_1_curso_2.zip`
   con todo lo requerido y sin avisos pendientes.
4. **Fichas recargadas** en el Mac tras aplicar encabezados.

## Estado de la entrega (cerrada)

- Raíz del zip: `tarea_1_curso_2/` con `LEEME.txt`, `documento-entrega.pdf`,
  `blueprint-{ezequiel,fabio,gustavo}.md`, `companeros.md`, `evidencias/`
  (fichas, catálogos y rondas de **Mac y Windows**) y `proyecto/` (código completo,
  sin `.env` ni `.venv`).
- Sin campos ⟨pendiente⟩; empaquetador sin avisos.

## Para compartir

- Repo público: https://github.com/etmunoz/tarea_1_curso_2
- Carpeta de entrega: https://github.com/etmunoz/tarea_1_curso_2/tree/main/entrega/tarea_1_curso_2
