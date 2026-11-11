<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/19-app-web-por-equipo.md`  
> **Objetivo:** 19 · App web por equipo para probar agentes (uno a uno y vía coordinador)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2140 · **Última modificación:** 20261111 1227
<!--/encabezado-grupo-->

# 19 · App web por equipo para probar agentes (uno a uno y vía coordinador)

**Fecha:** 2026-11-10

## Prompt

> Crear la app web simple para acceder a los agentes, así probarlos de a uno y, por otro
> lado, a través del coordinador. Debe ser una app web para Mac y otra para Windows, para
> que las configuraciones sean propias de cada uno (según los agentes que manejan).

## Verificación pedida

- App web (sin dependencias extra) con selector de agente (local/remoto) + "Coordinador".
- Config por equipo vía entorno (misma app, roles distintos): `scripts/mac_app.sh`, `scripts/win_app.ps1`.
- Probar un agente directo (A2A) y el coordinador (ruteo).
