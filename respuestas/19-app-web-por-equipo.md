<!--encabezado-grupo-->
> **Archivo:** `respuestas/19-app-web-por-equipo.md`  
> **Objetivo:** 19 · Respuesta — App web por equipo  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2140 · **Última modificación:** 20261111 1210
<!--/encabezado-grupo-->

# 19 · Respuesta — App web por equipo

Prompt: [`../prompts_ejecutados/19-app-web-por-equipo.md`](../prompts_ejecutados/19-app-web-por-equipo.md)

## Archivos creados

- `src/webapp/app.py` — app web (librería estándar, sin deps extra). Página única con selector
  (agentes locales 🟢 / remotos 🔵 + 🧭 Coordinador), caja de texto y chat. Endpoints:
  `GET /` (HTML), `GET /api/agentes`, `POST /api/preguntar`. Reutiliza `src.coordinador`
  (A2A directo y el grafo supervisor). Config por entorno: `APP_ROL`, `A2A_GRAFOS_LOCALES`,
  `URLS_AGENTES`, `WEBAPP_PORT`.
- `scripts/mac_app.sh` — rol "Mac · Ezequiel"; locales ezequiel/cocina/viajes; remoto opcional = túnel del Windows.
- `scripts/win_app.ps1` — rol "Windows · Tomás"; local tomas; remoto opcional = túnel del Mac.
- `src/webapp/app.py` coerciona el `context_id` a UUID para las llamadas A2A directas.

## Verificación (en vivo, con langgraph dev arriba)

```text
GET /api/agentes -> [agente_ezequiel (local), agente_cocina (local), agente_tomas (local)]

POST directo a cocina ("¿Cuánto cuesta un charquicán para 4?")
-> ruta: directo
-> "El costo total ... es de $5.500 CLP ... $1.375 CLP por persona ..."

POST al coordinador ("¿Qué es el símbolo Cho Ku Rei?")
-> ruta: supervisor → agente_remoto
-> "[agente_tomas] El Cho Ku Rei es un símbolo de Nivel II ..."
```

## Uso

```bash
./scripts/mac_app.sh "https://<tunel-windows>"      # Mac  → http://127.0.0.1:8800
.\scripts\win_app.ps1 "https://<tunel-mac>"         # Windows → http://127.0.0.1:8800
```

## Estado

App web lista y verificada: prueba agentes uno a uno y vía coordinador; la misma app con
config propia por equipo (Mac ve ezequiel/cocina locales + tomas remoto; Windows al revés).
