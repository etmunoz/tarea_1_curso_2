<!--encabezado-grupo-->
> **Archivo:** `respuestas/62-ficha-agente-vps-y-vigilante.md`  
> **Objetivo:** 62 · Respuesta — Ficha correcta en agente.etmk.cl + servicio vigilante persistente  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1910 · **Última modificación:** 20261112 1910
<!--/encabezado-grupo-->

# 62 · Respuesta — Ficha correcta en agente.etmk.cl + vigilante

Prompt: [`../prompts_ejecutados/62-ficha-agente-vps-y-vigilante.md`](../prompts_ejecutados/62-ficha-agente-vps-y-vigilante.md)

## Diagnóstico

Gustavo apuntó primero a un túnel langgraph equivocado (de ProteinMAN) → HTTP 400 (langgraph exige
`assistant_id` en la card). Al pasarle la URL buena `https://agente.etmk.cl`, su coordinador la
descubrió, pero la card venía con la **descripción genérica de langgraph**:

```
description: "agente_ezequiel assistant"
skill:       "agente_ezequiel Capabilities"
tags:        ["assistant","langgraph"]
```

Causa: el puente (`src/puente_a2a/servidor.py`, `card_clasica`) construye su card **desde la card de
langgraph** (`card_langgraph.get("description")`). El langgraph del VPS había perdido la ficha
aplicada: cada deploy (`git reset --hard`) toca `src/`, y `langgraph dev` hace **hot-reload** que
borra las fichas (`PATCH /assistants/<id>`). La descripción buena sí está en `src/fichas.py`, pero no
estaba aplicada en el VPS.

## Solución

1. Re-aplicar la ficha en el VPS:
   ```
   A2A_BASE=http://127.0.0.1:2024 uv run python tools/configurar_fichas.py --grafos agente_ezequiel,agente_cocina
   ```
2. Dejarla **persistente** con un servicio systemd nuevo **`agente-fichas`** que corre
   `configurar_fichas.py --vigilar` (re-aplica apenas langgraph borra las fichas, cada 5 s). Archivo
   en [`../deploy/systemd/agente-fichas.service`](../deploy/systemd/agente-fichas.service);
   `enabled` + `active`.

## Verificación (card final de `agente.etmk.cl`)

```
name       : Agente de Ezequiel
description: Ingeniero de IA y Data Scientist: recomienda qué técnica de machine learning usar para un
             problema, qué métricas mirar y qué modelo elegir según el tipo de dato. No programa por ti,
             no entrena modelos reales y no responde temas fuera de IA/Data Science.
skill      : Agente de Ezequiel Capabilities -> (misma descripción de IA/ML)
```

→ Ahora el supervisor de Gustavo tiene evidencia para enrutar preguntas de ML a `agente_ezequiel`.

## Archivos tocados

- `deploy/systemd/agente-fichas.service` (nuevo) + `deploy/README.md` (lo suma a la arquitectura y al
  `enable`).
- (En el VPS) `/etc/systemd/system/agente-fichas.service`, `enabled`/`active`.
- `prompts_ejecutados/62-…md` y `respuestas/62-…md` (este registro).

## Estado

- `agente.etmk.cl` publica la ficha correcta y se mantiene sola (vigilante). Son ahora **5 servicios**
  systemd (langgraph, fichas, puente, monitor, coordinador).

## Pendientes

- Regenerar el zip de entrega (registros 60/61/62) cuando se pida.
- Housekeeping: revocar el sudo temporal (`sudo rm /etc/sudoers.d/90-administrator-nopasswd`).
