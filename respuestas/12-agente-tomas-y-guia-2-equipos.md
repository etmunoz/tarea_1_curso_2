<!--encabezado-grupo-->
> **Archivo:** `respuestas/12-agente-tomas-y-guia-2-equipos.md`  
> **Objetivo:** 12 · Respuesta — Agente Tomás + guía y scripts 2 computadores  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1952 · **Última modificación:** 20261111 1413
<!--/encabezado-grupo-->

# 12 · Respuesta — Agente Tomás + guía y scripts 2 computadores

Prompt: [`../prompts_ejecutados/12-agente-tomas-y-guia-2-equipos.md`](../prompts_ejecutados/12-agente-tomas-y-guia-2-equipos.md)

## Archivos creados

- `src/agente_tomas/` — `herramientas.py` (`principios_reiki`, `posiciones_manos`,
  `info_simbolo`; sin consejo médico), `prompts.py` (`SYSTEM_TOMAS`), `graph.py`
  (`create_agent`, `name="agente_tomas"`). Registrado en `langgraph.json`.
- `src/fichas.py` — fichas (name + description) de ezequiel, tomas y viajes.
- `tools/configurar_fichas.py` — aplica la ficha (`PATCH /assistants/<id>`) y guarda
  `evidencias/02-ficha-<grafo>.json` (requiere el servidor; no requiere key).
- `tools/guardar_evidencias.py` — guarda `evidencias/04-catalogo.txt` (servidor) y
  `evidencias/05-ronda.md` (servidor + key).
- `guia_ezequiel_tomas.md` — prueba end-to-end Mac (Ezequiel) ↔ Windows (Tomás),
  con topología, pasos, evidencias y troubleshooting, + sección "Modo automatizado".
- `scripts/` — `.sh` (Mac): `mac_servir.sh`, `mac_tunel.sh`, `mac_coordinador.sh`;
  `.ps1` (Windows): `win_servir.ps1`, `win_tunel.ps1`, `win_coordinador.ps1`.
- `tests/test_agente_tomas.py`, `notebooks/tomas_paso_a_paso.ipynb`.
- `plan.json` grupo `agente-tomas` (t01); ROADMAP con Fase 3.bis (prueba 2 equipos).

## Salida de la verificación

```text
$ uv run python -c "from src.agente_tomas.herramientas import info_simbolo; print(info_simbolo.invoke({'nombre':'Hon Sha Ze Sho Nen'}))"
{'simbolo': 'Hon Sha Ze Sho Nen', 'nivel': 'II', 'para_que': 'enviar Reiki a distancia (tiempo/espacio)'}

$ langgraph.json graphs: agente_viajes, agente_ezequiel, agente_tomas

$ uv run pytest -q
19 passed, 5 skipped

$ for f in scripts/*.sh; do bash -n "$f"; done   # sintaxis OK

# scripts degradan sin servidor/clave sin romper:
$ uv run python tools/guardar_evidencias.py   → guarda 04-catalogo.txt; ronda omitida (sin key)
$ uv run python tools/configurar_fichas.py --grafos agente_tomas  → reporta "Connection refused" si no hay langgraph dev
```

## Cómo correr la prueba (resumen; detalle en guia_ezequiel_tomas.md)

- **Mac:** `./scripts/mac_servir.sh` (Ezequiel + ficha).
- **Windows:** `.\scripts\win_servir.ps1` (Tomás + ficha) y `.\scripts\win_tunel.ps1` (copia la URL).
- **Mac:** `./scripts/mac_coordinador.sh "https://<tunel-win>#agente_tomas"` → enruta y guarda evidencias.

## Estado

Agente Tomás, fichas, guardado de evidencias, guía y scripts ✅ (verificados sin key).
Falta la **corrida real entre los 2 equipos** (requiere `GOOGLE_API_KEY` + túneles).
