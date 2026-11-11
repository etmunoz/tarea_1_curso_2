<!--encabezado-grupo-->
> **Archivo:** `respuestas/43-mac-pull-windows-y-reempaquetar-final.md`  
> **Objetivo:** Respuesta 43 · Mac: integrar evidencias de Windows y reempaquetar la entrega final  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2349 · **Última modificación:** 20261111 1227
<!--/encabezado-grupo-->

# Respuesta 43 · Mac: integrar evidencias de Windows y reempaquetar la entrega final

Prompt: [`../prompts_ejecutados/43-mac-pull-windows-y-reempaquetar-final.md`](../prompts_ejecutados/43-mac-pull-windows-y-reempaquetar-final.md)

## 1. Pull de las evidencias de Windows (salida real)

```text
$ git fetch origin
From https://github.com/etmunoz/tarea_1_curso_2
   5a80f5d..4c89013  main -> origin/main

$ git pull --rebase origin main
Updating 5a80f5d..4c89013
Fast-forward
 .../evidencias/04-catalogo-windows.txt             |  2 +-
 .../tarea_1_curso_2/evidencias/05-ronda-windows.md | 10 +-
 evidencias/04-catalogo-windows.txt                 |  2 +-
 evidencias/05-ronda-windows.md                     | 10 +-
 .../42-windows-capturar-evidencias-finales.md      | 21 ++++
 prompts_ejecutados/README.md                       |  1 +
 .../42-windows-capturar-evidencias-finales.md      | 106 +++++++++++++++
 7 files changed, 140 insertions(+), 12 deletions(-)
```

> Nota: el commit `4c89013` (prompt 42, hecho en el Windows) entró con el email personal
> `etmunoz@gmail.com` porque el git del Windows no tenía el email de marcador. Esto quedó
> en el historial público (ver el aviso en la respuesta 40).

## 2. Evidencia bidireccional completa (espejo entre equipos)

- **Mac** (`05-ronda-mac.md`): Ezequiel y cocina **locales**; Tomás **remoto** por Cloudflare.
- **Windows** (`05-ronda-windows.md`): Tomás **local**; Ezequiel y cocina **remotos** por Cloudflare.

Ronda real del Windows (extracto `05-ronda-windows.md`, desde `ASUS-ETMK`):

```
> ¿Cuáles son los cinco principios del Reiki?
  ruta: supervisor → agente_local    [Agente de Tomás] … Gokai …
> ¿Qué métricas uso en un problema de regresión?
  ruta: supervisor → agente_remoto   [Agente de Ezequiel] … MAE, RMSE, R², MAPE …
> ¿Cuánto cuesta una cazuela de vacuno para 6 personas?
  ruta: supervisor → agente_remoto   [Agente de cocina chilena] … Costo total: $11.302 CLP …
> ¿Quién descubrió América?           ruta: supervisor → sin_agente
```

## 3. Reempaquetado (salida real)

```text
$ uv run python tools/empaquetar_entrega.py --grupo NN
✓ Carpeta de entrega: entrega/tarea_1_curso_2/ (versionada en la repo)
✓ Zip creado: dist/grupo-NN-tarea_1_curso_2.zip
  raíz del zip: tarea_1_curso_2/ · proyecto/: 215 archivos versionados

$ uv run python tools/aplicar_encabezados.py --check
OK · 204 archivos con encabezado.
```

Fichas recargadas en el Mac. Commit `3305e58` — «43 · Mac: integrar evidencias finales de
Windows y reempaquetar la entrega».
