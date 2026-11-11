<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/11-esqueleto-entrega.md`  
> **Objetivo:** 11 · Esqueleto de entrega y empaquetador del zip  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1941 · **Última modificación:** 20261111 1429
<!--/encabezado-grupo-->

# 11 · Esqueleto de entrega y empaquetador del zip

**Fecha:** 2026-11-10

## Prompt

> Preparar el empaquetado y documento de entrega (Paso 9 del taller).

## Qué se pidió

- Borrador del **documento de entrega** con la estructura de la rúbrica.
- Plantilla `companeros.md` y guía de `evidencias/`.
- Un **empaquetador** que arme el zip del grupo con la estructura del Paso 9,
  sin incluir `.env`/`.venv`.

## Verificación pedida

- `tools/empaquetar_entrega.py --grupo N` crea `dist/grupo-N-taller-a2a.zip`.
- El zip trae `proyecto/` (todo lo versionado) + documento + blueprint + companeros + evidencias.
- No se cuela ningún `.env` (solo `.env.example`); avisa de pendientes.
