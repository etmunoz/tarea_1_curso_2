<!--encabezado-grupo-->
> **Archivo:** `guia_ezequiel_tomas.md`  
> **Objetivo:** Guía end-to-end · Ezequiel (Mac) ↔ Tomás (Windows) — todo por Cloudflare  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1953 · **Última modificación:** 20261110 2124
<!--/encabezado-grupo-->

# Guía end-to-end · Ezequiel (Mac) ↔ Tomás (Windows) — todo por Cloudflare

Prueba de A2A **entre dos computadores en redes distintas** (sin LAN): todo el tráfico
entre equipos pasa por **Cloudflare**. Pensada para ser **plug-and-play**: sigue los
pasos en orden y funciona.

## Reparto (quién hace qué)

- **MacOS = Ezequiel**: corre el agente **Ezequiel** (IA/Data Science), **hospeda el Redis**
  (dockerizado) y corre el **coordinador** que enruta las preguntas.
- **Windows = Tomás**: corre el agente **Tomás** (Maestro Reiki) y su **RAG**, que usa el
  **Redis del Mac** de forma remota.

Todo entre equipos va por Cloudflare:

```
   MacOS (Ezequiel)                               Windows (Tomás)
 ┌───────────────────────────────┐             ┌───────────────────────────────┐
 │ langgraph dev :2024            │             │ langgraph dev :2024            │
 │   · agente_ezequiel (local)    │             │   · agente_tomas              │
 │ Redis :6379 (Docker)           │             │ RAG de Tomás → usa el Redis   │
 │   └─ túnel TCP Cloudflare ─────┼──TCP CF────▶│      del Mac (forwarder local) │
 │ coordinador:                   │             │ túnel HTTP Cloudflare de Tomás │
 │   local: ezequiel              │◀──HTTP CF───┼──── (trycloudflare.com)        │
 │   remoto: tomas (túnel HTTP)   │             │                               │
 └───────────────────────────────┘             └───────────────────────────────┘
      IA/Data Science → Ezequiel (local)
      Reiki           → Tomás (remoto, Windows) · responde con el RAG sobre el Redis del Mac
```

## Requisitos

| | Mac (Ezequiel) | Windows (Tomás) |
|---|---|---|
| uv + Python 3.13 | sí | sí (lo instala el setup) |
| cloudflared | `brew install cloudflared` | lo instala el setup |
| Docker Desktop | **sí** (para Redis) | no |
| GOOGLE_API_KEY (Gemini, con saldo) | sí | sí (la misma) |
| **Cuenta Cloudflare + un DOMINIO en Cloudflare** | **sí** (para el túnel TCP de Redis) | no |

> **Importante (único prerrequisito especial):** exponer Redis por Cloudflare entre redes
> distintas necesita un **túnel con nombre (TCP)**, y eso exige un **dominio gestionado en
> tu cuenta de Cloudflare** (sus nameservers apuntando a Cloudflare). Elige un host, p. ej.
> `redis-tomas.TU-DOMINIO.com`. Los agentes (HTTP) usan túneles gratis `trycloudflare.com`
> y no necesitan dominio.

---

## A · MacOS (Ezequiel) — desde cero

```bash
# 1) Clonar (si no está)
mkdir -p ~/proyectos && cd ~/proyectos
gh repo clone etmunoz/tarea_1_curso_2 2>/dev/null || true
cd tarea_1_curso_2
uv sync
cp .env.example .env            # pega tu GOOGLE_API_KEY en .env
uv run python tools/probar_gemini.py   # debe decir: ✓ Gemini respondió 'OK'
```

```bash
# 2) Terminal 1 — agente Ezequiel (langgraph dev) + su ficha
./scripts/mac_servir.sh
```

```bash
# 3) Terminal 2 — Redis + túnel TCP de Cloudflare (reemplaza por tu host real)
./scripts/mac_redis_cloudflare.sh redis-tomas.TU-DOMINIO.com
# La primera vez abre el navegador (cloudflared tunnel login): elige tu dominio.
# Deja esta terminal ABIERTA. Pásale al Windows el host: redis-tomas.TU-DOMINIO.com
```

---

## B · Windows (Tomás) — desde cero (PowerShell)

```powershell
# 1) Clonar el repo privado
winget install -e --id GitHub.cli --accept-source-agreements --accept-package-agreements
#    (cierra y reabre PowerShell para refrescar el PATH)
gh auth login                        # GitHub.com → HTTPS → Login with a web browser
mkdir "$env:USERPROFILE\proyectos" -ErrorAction SilentlyContinue
cd "$env:USERPROFILE\proyectos"
gh repo clone etmunoz/tarea_1_curso_2
cd tarea_1_curso_2

# 2) Setup (instala uv, Python 3.13, cloudflared; uv sync; .env + clave; apunta REDIS_URL al forwarder local)
.\scripts\setup_windows.ps1 -RedisUrl redis://localhost:6379
```

```powershell
# 3) Terminal A — acceso al Redis del Mac por Cloudflare (deja ABIERTA)
.\scripts\win_redis_cloudflare.ps1 redis-tomas.TU-DOMINIO.com
```

```powershell
# 4) Terminal B — ingesta del RAG (ahora que el Redis del Mac es accesible en localhost:6379)
uv run python tools/cargar_rag_reiki.py        # debe decir: ✓ N fragmentos indexados
```

```powershell
# 5) Terminal C — agente Tomás + su ficha
.\scripts\win_servir.ps1
```

```powershell
# 6) Terminal D — túnel HTTP de Tomás; COPIA la URL https y pásala al Mac
.\scripts\win_tunel.ps1
# imprime algo como: https://reiki-azul-123.trycloudflare.com
```

---

## C · MacOS (Ezequiel) — el coordinador enruta a los dos

```bash
# Terminal 3 — con la URL del túnel de Tomás (Windows)
./scripts/mac_coordinador.sh "https://<tunel-win>#agente_tomas"
```

Esperado (enrutamiento correcto):

- *"¿Qué técnica uso si tengo desbalance de clases?"* → **[Agente de Ezequiel]** (local, Mac)
- *"¿Qué símbolos se aprenden en el nivel 2 de Reiki?"* → **[Agente de Tomás]** (remoto, Windows; responde con el RAG sobre el Redis del Mac)
- *"¿Cuánto cuesta un pastel de choclo para 4?"* → **[Agente de cocina chilena]** (local, Mac)
- *"¿Quién ganó el mundial de 1962?"* → **sin_agente** (rechazado)

El coordinador guarda `evidencias/04-catalogo.txt` y `evidencias/05-ronda.md`.

---

## Evidencias (Paso 7–8 del taller)

| Archivo | Cómo se genera | Dónde |
|---|---|---|
| `02-ficha-agente_ezequiel.json` | `mac_servir.sh` (configura la ficha) | Mac, automático |
| `02-ficha-agente_tomas.json` | `win_servir.ps1` (configura la ficha) | Windows, automático |
| `04-catalogo.txt` · `05-ronda.md` | `mac_coordinador.sh` | Mac, automático |
| `01-saltos.png` | captura de un agente usando su herramienta y rechazando lo ajeno | manual |
| `03-tunel.png` | captura de `cloudflared` (túnel de Tomás) + su ficha vista desde el Mac | manual |

Empaquetar la entrega al final (en el Mac):

```bash
uv run python tools/empaquetar_entrega.py --grupo N
```

---

## Problemas típicos

- **cloudflared tunnel login no abre / dominio no aparece:** tu dominio debe estar **agregado y
  activo en Cloudflare** (nameservers apuntando a Cloudflare). Revisa el panel de Cloudflare.
- **Windows: el RAG no conecta (`Redis no responde`):** verifica que la Terminal A
  (`win_redis_cloudflare.ps1`) siga abierta y que `.env` tenga `REDIS_URL=redis://localhost:6379`.
- **El coordinador no ve a Tomás:** revisa que en el Windows sigan abiertos `win_servir.ps1` y
  `win_tunel.ps1`, y que la URL que le pasaste al Mac sea la actual (el túnel HTTP **cambia la URL**
  al reiniciarse).
- **Firewall de Windows:** la 1ª vez permite `langgraph`/Python en redes privadas.
- **Permisos de `.ps1`:** `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- **402 / sin saldo al usar Gemini:** la clave necesita saldo/cuota (ver `tools/probar_gemini.py`).

## Al terminar (teardown)

- `Ctrl+C` en: `win_tunel.ps1`, `win_redis_cloudflare.ps1`, `mac_redis_cloudflare.sh`, `win_servir.ps1`, `mac_servir.sh`.
- En el Mac, si quieres bajar Redis: `docker compose down`.
- Las URLs `trycloudflare.com` son temporales: no las dejes en `.env` versionado.
