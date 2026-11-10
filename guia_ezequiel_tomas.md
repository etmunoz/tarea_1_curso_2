<!-- --8<-- encabezado-grupo
Archivo: guia_ezequiel_tomas.md
Objetivo: Guía end-to-end · Ezequiel (Mac) ↔ Tomás (Windows)
Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
Creación: 20261110 1952
Última modificación: 20261110 1952
--8<-- fin-encabezado-grupo -->

# Guía end-to-end · Ezequiel (Mac) ↔ Tomás (Windows)

Prueba de A2A **entre tus dos computadores**, antes de hacerlo con los compañeros:

- **MacOS** corre el agente **Ezequiel** (IA Engineer & Data Scientist).
- **Windows** corre el agente **Tomás** (Maestro Reiki).
- El **coordinador** (en el Mac) suma a los dos y enruta cada pregunta al que corresponde.

```
   MacOS                                   Windows
 ┌─────────────────────────┐            ┌─────────────────────────┐
 │ langgraph dev :2024      │            │ langgraph dev :2024      │
 │  · agente_ezequiel (local)│           │  · agente_tomas          │
 │ coordinador ─────────────┼──A2A──────▶│  (expuesto por cloudflared│
 │  local: ezequiel          │  túnel     │   https://…trycloudflare) │
 │  remoto: tomas (túnel win)│            │                          │
 └─────────────────────────┘            └─────────────────────────┘
        IA/Data Science → Ezequiel (local)
        Reiki           → Tomás (remoto, en el Windows)
```

## Modo automatizado (scripts)

Para no pegar comandos a mano, cada lado tiene sus scripts (`.sh` en Mac, `.ps1` en
Windows). El único paso manual inevitable es **intercambiar la URL del túnel**.

**MacOS (Ezequiel):**
```bash
./scripts/mac_servir.sh                                   # terminal 1: langgraph dev + ficha de Ezequiel
./scripts/mac_tunel.sh                                     # terminal 2: (opcional) túnel del Mac
./scripts/mac_coordinador.sh "https://<tunel-win>#agente_tomas"   # terminal 3: enruta y guarda evidencias
```

**Windows (Tomás) · PowerShell:**
```powershell
.\scripts\win_servir.ps1          # terminal 1: langgraph dev + ficha de Tomás
.\scripts\win_tunel.ps1           # terminal 2: túnel -> copia la URL y pásala al Mac
# (si el coordinador lo corres en el Windows):
.\scripts\win_coordinador.ps1 "https://<tunel-mac>#agente_ezequiel"
```

Los scripts hacen `uv sync`, crean `.env` si falta (te avisan de la `GOOGLE_API_KEY`),
sacan cualquier conda activo, levantan el servidor y configuran la ficha sola cuando
el servidor responde. El detalle de cada paso está abajo.

## 0. Requisitos en CADA computador

- El repo clonado: `git clone https://github.com/etmunoz/tarea_1_curso_2`
- **uv** y **Python 3.13** (uv lo instala: `uv python install 3.13`)
- Una **`GOOGLE_API_KEY`** (Gemini) en `.env` — la clave va solo en `.env` (ignorado), nunca al repo.
- **cloudflared** instalado (para el túnel):
  - Mac: `brew install cloudflared`
  - Windows: `winget install --id Cloudflare.cloudflared` (o descarga el `.exe`)

---

## Parte A · MacOS — agente Ezequiel

```bash
cd ~/proyectos/tarea_1_curso_2
uv sync
cp .env.example .env            # pega tu GOOGLE_API_KEY en .env
uv run langgraph dev            # publica agente_viajes, agente_ezequiel, agente_tomas en :2024
```

En **otra terminal** del Mac, configura la ficha de Ezequiel y guárdala como evidencia:

```bash
uv run python tools/configurar_fichas.py --grafos agente_ezequiel --guardar-evidencia
# → evidencias/02-ficha-agente_ezequiel.json
```

> El Mac corre también el coordinador (Parte C), así que **no necesita túnel**: el
> coordinador llega a Ezequiel por `http://127.0.0.1:2024`.

---

## Parte B · Windows — agente Tomás (PowerShell)

```powershell
cd $env:USERPROFILE\proyectos\tarea_1_curso_2
uv sync
Copy-Item .env.example .env     # pon tu GOOGLE_API_KEY en .env
uv run langgraph dev            # :2024  (la 1ª vez, el firewall pregunta → permitir redes privadas)
```

En **otra terminal** (PowerShell), la ficha de Tomás + evidencia:

```powershell
uv run python tools/configurar_fichas.py --grafos agente_tomas --guardar-evidencia
# → evidencias/02-ficha-agente_tomas.json
```

En **otra terminal**, abre el túnel y copia la URL pública de Tomás:

```powershell
cloudflared tunnel --url http://127.0.0.1:2024
# ... imprime algo como:  https://reiki-azul-123.trycloudflare.com
```

Comparte esa URL con el Mac (chat, mensaje, etc.). Verifica desde el Mac que se ve:

```bash
curl -s "https://reiki-azul-123.trycloudflare.com/.well-known/agent-card.json?assistant_id=$(curl -s -X POST https://reiki-azul-123.trycloudflare.com/assistants/search -H 'Content-Type: application/json' -d '{"graph_id":"agente_tomas"}' | python3 -c 'import json,sys;print(json.load(sys.stdin)[0]["assistant_id"])')" | python3 -m json.tool
```

> Deja el `langgraph dev` y el `cloudflared` abiertos en el Windows mientras dure la prueba.

---

## Parte C · MacOS — el coordinador enruta a los dos

En el **`.env` del Mac**, define el catálogo (Ezequiel local + Tomás remoto por su túnel):

```bash
A2A_BASE=http://127.0.0.1:2024
A2A_GRAFOS_LOCALES=agente_ezequiel
URLS_AGENTES=https://reiki-azul-123.trycloudflare.com#agente_tomas
```

Corre el coordinador y guarda las evidencias:

```bash
uv run python -m src.coordinador.graph        # ves la ruta y la respuesta [Nombre] …
uv run python tools/guardar_evidencias.py     # → evidencias/04-catalogo.txt y 05-ronda.md
```

Esperado:

- *"¿Qué técnica uso si tengo desbalance de clases?"* → `supervisor → agente_remoto` · **[Agente de Ezequiel]** (local, Mac)
- *"¿Para qué sirve el símbolo Cho Ku Rei en Reiki?"* → `supervisor → agente_remoto` · **[Agente de Tomás]** (remoto, Windows)
- *"¿Quién ganó el mundial de 1962?"* → `supervisor → sin_agente` · **ninguno**

---

## Evidencias a guardar (Paso 7–8 del taller)

| Archivo | Cómo se genera | Dónde |
|---|---|---|
| `02-ficha-agente_ezequiel.json` | `configurar_fichas.py` en el Mac | automático |
| `02-ficha-agente_tomas.json` | `configurar_fichas.py` en el Windows | automático |
| `04-catalogo.txt` | `guardar_evidencias.py` en el Mac | automático |
| `05-ronda.md` | `guardar_evidencias.py` en el Mac | automático |
| `01-saltos.png` | captura del notebook/A2A de un agente usando su herramienta y rechazando lo ajeno | manual |
| `03-tunel.png` | captura de la terminal de `cloudflared` (Windows) + la ficha de Tomás vista desde el Mac | manual |

Todas se juntan corriendo, al final, el empaquetador:

```bash
uv run python tools/empaquetar_entrega.py --grupo N   # arma dist/grupo-N-taller-a2a.zip con las evidencias
```

---

## Problemas típicos

- **"Connection refused" / el coordinador no ve a Tomás:** revisa que en el Windows sigan abiertos `langgraph dev` y `cloudflared`, y que la URL del `.env` del Mac sea la actual (cloudflared **cambia la URL** cada vez que se reinicia).
- **El firewall de Windows:** la primera vez, permitir `langgraph`/Python en redes privadas.
- **`curl` en PowerShell** es otro comando: usa `curl.exe` o `Invoke-RestMethod`.
- **`assistant_id`:** cada servidor asigna un UUID por grafo; el cliente lo resuelve solo con `POST /assistants/search {"graph_id": ...}`.
- **La ficha no cambia en el catálogo:** reinicia el `langgraph dev` tras `configurar_fichas.py` si hace falta; el supervisor lee las fichas al construir el catálogo.

## Al terminar

- `Ctrl+C` en los túneles de `cloudflared` (mientras estén abiertos, cualquiera con la URL usa tu agente y gasta tu clave).
- Las URLs de `trycloudflare.com` son temporales: no las dejes en el `.env` versionado.
