<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/28-windows-verificar-tunel.md`  
> **Objetivo:** 28 · Windows: verificar el túnel de Cloudflare del agente Tomás  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2220 · **Última modificación:** 20261110 2220
<!--/encabezado-grupo-->

# 28 · Windows: verificar el túnel de Cloudflare del agente Tomás

**Fecha:** 2026-11-10 · **Equipo:** Windows (nodo Tomás)

## Prompt

> dice esto: *(pegó la salida de `.\scripts\win_tunel.ps1`)*

Extracto de la salida pegada:

```text
INF Requesting new quick Tunnel on trycloudflare.com...
INF |  https://delays-therapeutic-wait-yeast.trycloudflare.com  |
INF Settings: map[ha-connections:1 protocol:quic url:http://127.0.0.1:2024]
INF cloudflared does not support loading the system root certificate pool on Windows. ...
ERR Failed to dial a quic connection error="failed to dial to edge with quic: timeout: no recent network activity"
INF Retrying connection in up to 2s
INF CONNECTIVITY PRE-CHECKS ... SUMMARY: Environment is healthy. cloudflared will use 'quic' as primary protocol.
INF Registered tunnel connection ... location=scl02 protocol=quic
```

Pregunta de seguimiento:

> pero dime la URL que no la vi en la salida o no se como identificarla

## Verificación pedida

- Que la URL pública del túnel llegue al `langgraph dev` local y que el agente Tomás responda por A2A desde internet.
