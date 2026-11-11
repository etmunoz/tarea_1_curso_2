<!--encabezado-grupo-->
> **Archivo:** `guia_ezequiel_tomas.md`  
> **Objetivo:** Guía end-to-end · Ezequiel (Mac) ↔ Tomás (Windows) — bidireccional, por Cloudflare  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1953 · **Última modificación:** 20261111 1227
<!--/encabezado-grupo-->

# Guía end-to-end · Ezequiel (Mac) ↔ Tomás (Windows) — bidireccional, por Cloudflare

Prueba de A2A **entre dos computadores en redes distintas** (sin LAN): **la misma repo**
corre en ambos equipos y el **rol lo definen variables de entorno** (no cambia el código).
Es **bidireccional**: desde el Mac usas el coordinador con acceso a lo local y lo remoto, y
desde el Windows igual. La prueba termina con **consultas en ambos lados** y **evidencias
registradas en los dos PC**. Todo el tráfico entre equipos va por **túneles HTTP de
Cloudflare**; **nada por TCP ni LAN**.

## Reparto (quién hace qué)

- **MacOS = Ezequiel**: corre los agentes **Ezequiel** (IA/Data Science) y **cocina** (y viajes),
  expone su `langgraph dev` por un **túnel HTTP de Cloudflare**, y corre un **coordinador**.
- **Windows = Tomás**: corre el agente **Tomás** (Maestro Reiki) con su **RAG sobre un Redis
  LOCAL** (dockerizado, no se expone por red), expone su `langgraph dev` por un **túnel HTTP de
  Cloudflare**, y corre un **coordinador**.
- Cada agente **expone sus capacidades** (y el RAG, en el caso de Tomás) **a través de su propio
  agente** por el túnel HTTP. El coordinador de cada lado alcanza lo remoto por ese túnel.

```
   MacOS (Ezequiel)                               Windows (Tomás)
 ┌───────────────────────────────┐             ┌───────────────────────────────┐
 │ langgraph dev :2024            │             │ langgraph dev :2024            │
 │  ezequiel · cocina · viajes    │             │  tomas (RAG → Redis LOCAL)    │
 │ túnel HTTP Cloudflare ◀────────┼──HTTP CF───▶┼───────▶ túnel HTTP Cloudflare  │
 │ coordinador (mac):             │             │ coordinador (windows):        │
 │  local  ezequiel, cocina       │             │  local  tomas                 │
 │  remoto tomas (túnel win)      │             │  remoto ezequiel, cocina (túnel mac) │
 └───────────────────────────────┘             └───────────────────────────────┘
```

## Requisitos

| | Mac (Ezequiel) | Windows (Tomás) |
|---|---|---|
| uv + Python 3.13 | sí | sí (lo instala el setup) |
| cloudflared | `brew install cloudflared` | lo instala el setup |
| Docker Desktop | no | **sí** (Redis local del RAG) |
| GOOGLE_API_KEY (Gemini, con saldo) | sí | sí (la misma) |

> No se necesita dominio: los túneles de agentes son `trycloudflare.com` (HTTP, gratis).

---

## A · MacOS (Ezequiel) — desde cero

```bash
mkdir -p ~/proyectos && cd ~/proyectos
gh repo clone etmunoz/tarea_1_curso_2 2>/dev/null || true
cd tarea_1_curso_2
uv sync
cp .env.example .env            # pega tu GOOGLE_API_KEY en .env
uv run python tools/probar_gemini.py   # debe decir: ✓ Gemini respondió 'OK'
```

```bash
# Terminal 1 — agentes (langgraph dev) + ficha de Ezequiel
./scripts/mac_servir.sh
```

```bash
# Terminal 2 — túnel HTTP; COPIA la URL https (es el "túnel del Mac")
./scripts/mac_tunel.sh
# imprime algo como: https://azul-rio-123.trycloudflare.com
```

```bash
# Terminal 3 (opcional) — app web del Mac para probar agentes uno a uno y el coordinador
./scripts/mac_app.sh            # abre http://127.0.0.1:8800
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

# 2) Setup: instala uv, Python 3.13, cloudflared, Docker; uv sync; .env + clave;
#    levanta Redis LOCAL y carga el RAG de Reiki.
.\scripts\setup_windows.ps1
#    (si Docker se acaba de instalar: ábrelo una vez y re-corre el script)
```

```powershell
# 3) Terminal 1 — agente Tomás (langgraph dev) + su ficha
.\scripts\win_servir.ps1
```

```powershell
# 4) Terminal 2 — túnel HTTP; COPIA la URL https (es el "túnel del Windows")
.\scripts\win_tunel.ps1
# imprime algo como: https://reiki-azul-456.trycloudflare.com
```

```powershell
# 5) Terminal 3 (opcional) — app web del Windows
.\scripts\win_app.ps1            # abre http://127.0.0.1:8800
```

---

## C · Intercambien las URLs y corran el coordinador EN AMBOS

Cada equipo le pasa al otro su URL de túnel.

```bash
# En el MAC (Terminal 4) — remoto = túnel del Windows
./scripts/mac_coordinador.sh "https://<tunel-windows>"
# Enruta: ML→Ezequiel(local) · Reiki→Tomás(remoto) · receta→cocina(local) · fuera→ninguno
# Guarda: evidencias/04-catalogo-mac.txt y 05-ronda-mac.md
```

```powershell
# En el WINDOWS (Terminal 4) — remoto = túnel del Mac
.\scripts\win_coordinador.ps1 "https://<tunel-mac>"
# Enruta: Reiki→Tomás(local) · métricas→Ezequiel(remoto) · receta→cocina(remoto) · fuera→ninguno
# Guarda: evidencias/04-catalogo-windows.txt y 05-ronda-windows.md
```

> La **app web** (paso opcional) hace lo mismo con clics: en el selector eliges un agente
> (local o remoto) para probarlo solo, o **"Coordinador"** para ver el ruteo. En el Mac la app
> ve a Ezequiel/cocina locales + Tomás remoto; en el Windows, a Tomás local + Ezequiel/cocina
> remotos. Pásale a la app la URL del túnel del otro equipo con la variable del script.

Al terminar, **cada PC tiene sus propias evidencias** (`*-mac` en el Mac, `*-windows` en el
Windows), demostrando que el ruteo funciona **en ambos sentidos**.

---

## Evidencias (Paso 7–8 del taller)

| Archivo | Dónde se genera | Qué demuestra |
|---|---|---|
| `02-ficha-agente_ezequiel.json` · `02-ficha-agente_cocina.json` | Mac (`mac_servir.sh`) | fichas de Ezequiel/cocina |
| `02-ficha-agente_tomas.json` | Windows (`win_servir.ps1`) | ficha de Tomás |
| `04-catalogo-mac.txt` · `05-ronda-mac.md` | Mac (`mac_coordinador.sh`) | el Mac enruta local+remoto |
| `04-catalogo-windows.txt` · `05-ronda-windows.md` | Windows (`win_coordinador.ps1`) | el Windows enruta local+remoto |
| `01-saltos.png` · `03-tunel.png` | ambos (capturas) | manual |

Empaquetar la entrega al final (en cualquiera de los dos; el zip incluye `evidencias/`):

```bash
uv run python tools/empaquetar_entrega.py --grupo N
```

---

## Problemas típicos

- **El coordinador no ve al remoto:** revisa que en el OTRO equipo sigan abiertos `*_servir` y
  `*_tunel`, y que la URL que te pasaron sea la actual (el túnel HTTP **cambia la URL** al reiniciarse).
- **Windows: Tomás no usa el RAG (`buscar_reiki` degrada):** Docker Desktop debe estar abierto y
  `docker compose up -d` + `tools/cargar_rag_reiki.py` ejecutados (lo hace `setup_windows.ps1`).
- **Firewall de Windows:** la 1ª vez permite `langgraph`/Python en redes privadas.
- **Permisos de `.ps1`:** `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- **402 / sin saldo en Gemini:** la clave necesita saldo/cuota (`tools/probar_gemini.py` lo diagnostica).

## Al terminar (teardown)

- `Ctrl+C` en los `*_servir`, `*_tunel` y `*_app` de ambos equipos.
- En el Windows, para bajar Redis: `docker compose down`.
- Las URLs `trycloudflare.com` son temporales: no las dejes en `.env` versionado.
