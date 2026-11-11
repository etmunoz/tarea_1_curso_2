<!--encabezado-grupo-->
> **Archivo:** `entrega/documento-entrega.md`  
> **Objetivo:** Documento de entrega · Taller A2A (Curso 2 · Sesión 1)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1941 · **Última modificación:** 20261110 2306
<!--/encabezado-grupo-->

# Documento de entrega · Taller A2A (Curso 2 · Sesión 1)

> Borrador. Los campos marcados ⟨pendiente⟩ se completan tras la corrida en vivo
> (`GOOGLE_API_KEY` + `langgraph dev`) y la actividad de grupo. Se exporta a
> `documento-entrega.pdf` para el zip (ver `tools/empaquetar_entrega.py`).

## 1. Identificación

- **Curso 2 · Sesión 1** — Taller "tu skill es un agente y habla por A2A".
- **Grupo:** ⟨N⟩
- **Integrantes (nombres y apellidos completos):**
  - Fabio Durán ⟨apellido completo⟩
  - Gustavo Reyes ⟨apellido completo⟩
  - Ezequiel Muñoz Krsulovic
- **Repositorio:** https://github.com/etmunoz/tarea_1_curso_2

## 2. Blueprints (uno por integrante)

- **Ezequiel · IA Engineer & Data Scientist** → [`blueprint-ezequiel.md`](../blueprint-ezequiel.md)
- Fabio → ⟨blueprint-fabio.md⟩
- Gustavo → ⟨blueprint-gustavo.md⟩

## 3. Mi agente (Paso 3)

- Paquete `src/agente_ezequiel/`: herramientas `recomendar_tecnica`,
  `metricas_recomendadas`, `elegir_modelo` (datos simulados), prompt separado y
  grafo `create_agent` registrado en `langgraph.json` como `agente_ezequiel`.
- **Prompt usado** para crearlo: `prompts_ejecutados/04-crear-agente-ezequiel.md`.
- Qué cambié después de verlo funcionar: ⟨2 líneas⟩

## 4. Probarlo solo (Paso 4)

- Comandos y salida: `respuestas/04-crear-agente-ezequiel.md`.
- Evidencia: `evidencias/01-saltos.png` ⟨pendiente: captura en vivo⟩.

## 5. La ficha / Agent Card (Paso 5)

- Descripción (qué sé / qué no hago) y skills con ejemplo.
- Antes → después: ⟨pendiente⟩
- Evidencia: `evidencias/02-ficha.json` ⟨pendiente⟩.

## 6. Salir a internet · Cloudflare (Paso 6)

- Túnel: `cloudflared tunnel --url http://127.0.0.1:2024`
- Mi dirección pública: ⟨https://…trycloudflare.com⟩ (también en el blueprint).
- Evidencia: `evidencias/03-tunel.png` ⟨pendiente⟩.

## 7. Sumar a los compañeros · coordinador (Paso 7)

- Coordinador/supervisor: `src/coordinador/` (enruta por ficha; `URLS_AGENTES`).
- Agentes ajenos sumados: ver [`compañeros.md`](companeros.md) ⟨pendiente completar⟩.
- Evidencia: `evidencias/04-catalogo.png` ⟨pendiente⟩.

## 8. La ronda de preguntas (Paso 8)

| Integrante | Pregunta | A quién fue | ¿Estuvo bien? |
|---|---|---|---|
| ⟨…⟩ | ⟨…⟩ | ⟨[Agente de …]⟩ | ⟨sí/no⟩ |

- Comentario (qué ficha eligió mejor el supervisor, choques, qué cambiarían): ⟨pendiente⟩
- Evidencia: `evidencias/05-ronda.png` ⟨pendiente⟩.

## 9. Cómo correr el proyecto

```bash
uv sync
cp .env.example .env          # pega GOOGLE_API_KEY
uv run langgraph dev          # publica agente_viajes y agente_ezequiel (:2024)
uv run pytest                 # 14 passed (+ los que requieren langgraph dev)
```

- Demos: `uv run python -m src.swarm.graph`, `uv run python -m src.consumidor.graph`,
  `uv run python -m src.coordinador.graph`; notebooks en `notebooks/`.

## 10. Evidencias incluidas

Ver carpeta `evidencias/` (lista y requisitos en `evidencias/README.md`).
