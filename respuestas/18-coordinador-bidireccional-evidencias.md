<!--encabezado-grupo-->
> **Archivo:** `respuestas/18-coordinador-bidireccional-evidencias.md`  
> **Objetivo:** 18 · Respuesta — Coordinador bidireccional y evidencias en ambos PC  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2136 · **Última modificación:** 20261111 0835
<!--/encabezado-grupo-->

# 18 · Respuesta — Coordinador bidireccional y evidencias en ambos PC

Prompt: [`../prompts_ejecutados/18-coordinador-bidireccional-evidencias.md`](../prompts_ejecutados/18-coordinador-bidireccional-evidencias.md)

## Cambios

- **Eliminados** los scripts del enfoque TCP de Redis (descartado): no hay nada por TCP/LAN.
  El RAG de Tomás usa un **Redis LOCAL**; su RAG se alcanza **consultando al agente Tomás** por
  su túnel HTTP de Cloudflare.
- `tools/guardar_evidencias.py` — `--etiqueta` sufija las evidencias por equipo
  (`04-catalogo-<etiqueta>.txt`, `05-ronda-<etiqueta>.md`) y anota el host que la generó.
- `scripts/mac_coordinador.sh` — local `agente_ezequiel,agente_cocina` + remoto `tomas` (túnel
  del Windows); guarda evidencias `*-mac`.
- `scripts/win_coordinador.ps1` — local `agente_tomas` + remoto `ezequiel,cocina` (túnel del
  Mac); guarda evidencias `*-windows`.
- `setup_windows.ps1` — instala Docker + levanta Redis LOCAL + ingesta el RAG (Tomás autónomo).
- `.env.example` — `REDIS_URL` siempre local al equipo de Tomás.
- `guia_ezequiel_tomas.md` — reescrita: bidireccional, misma repo, todo por túnel HTTP, pasos
  A/B/C, evidencias en ambos PC, troubleshooting.

## Verificación (smoke test en un equipo, tratando localhost como "remoto")

```text
# Coordinador MAC (local: ezequiel,cocina · remoto: tomas)
> ¿Qué técnica uso si tengo desbalance de clases?   -> [Agente de Ezequiel]  (local)
> ¿Qué símbolos se aprenden en el nivel 2 de Reiki? -> [Agente de Tomás]     (remoto)
> ¿Cuánto cuesta un pastel de choclo para 4?        -> [Agente de cocina chilena] (local)
> ¿Quién ganó el mundial de 1962?                   -> sin_agente
  → evidencias/04-catalogo-mac.txt, 05-ronda-mac.md

# Coordinador WINDOWS (local: tomas · remoto: ezequiel,cocina)
> ¿Cuáles son los cinco principios del Reiki?       -> [Agente de Tomás]     (local)
> ¿Qué métricas uso en un problema de regresión?    -> [Agente de Ezequiel]  (remoto)
> ¿Cuánto cuesta una cazuela para 6 personas?       -> [Agente de cocina chilena] (remoto)
> ¿Quién descubrió América?                         -> sin_agente
  → evidencias/04-catalogo-windows.txt, 05-ronda-windows.md
```

Ambos sentidos enrutan correctamente a local y remoto, con evidencias separadas por equipo.

## Estado

Modelo bidireccional listo y verificado (smoke test). La corrida real entre los 2 PC genera
`*-mac` en el Mac y `*-windows` en el Windows, demostrando operatividad en ambos sentidos.
