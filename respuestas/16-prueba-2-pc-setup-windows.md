<!--encabezado-grupo-->
> **Archivo:** `respuestas/16-prueba-2-pc-setup-windows.md`  
> **Objetivo:** 16 · Respuesta — Prueba entre 2 computadores: setup del Windows  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2113 · **Última modificación:** 20261110 2312
<!--/encabezado-grupo-->

# 16 · Respuesta — Prueba entre 2 computadores: setup del Windows

Prompt: [`../prompts_ejecutados/16-prueba-2-pc-setup-windows.md`](../prompts_ejecutados/16-prueba-2-pc-setup-windows.md)

## Qué se hizo

- **Repo verificado**: `git status` limpio, sincronizado con `origin/main`; un clon limpio
  tiene todo (pyproject/uv.lock con `langchain-text-splitters`, `.env.example` con el modelo
  de embeddings correcto, docker-compose, docs de Reiki, scripts). `.env` correctamente NO versionado.
- **`scripts/setup_windows.ps1`** (nuevo): instala uv, Python 3.13, cloudflared (y Docker con
  `-ConRedis`); `uv sync`; crea `.env` y pide la `GOOGLE_API_KEY`; la valida con `probar_gemini.py`;
  con `-ConRedis` además `docker compose up -d` + `cargar_rag_reiki.py`. Al final imprime los pasos servir/túnel/coordinador.
- **`guia_ezequiel_tomas.md`**: sección "Preparar el Windows DESDE CERO" (instalar GitHub CLI,
  `gh auth login`, `gh repo clone etmunoz/tarea_1_curso_2`, correr el setup).

## Verificación

```text
$ git status --short            -> (vacío, limpio)
$ git log --oneline -1          -> 15 · Corrida en vivo … (pusheado)
archivos clave versionados      -> ✓ pyproject, uv.lock, langgraph.json, .env.example,
                                    docker-compose.yml, data/reiki/*, scripts/win_*.ps1, guía
.env versionado                 -> ✗ (bien: no se versiona)
scripts/setup_windows.ps1       -> creado (59 líneas)
```

## Pasos para el otro computador (Windows, PowerShell)

```powershell
winget install -e --id GitHub.cli --accept-source-agreements --accept-package-agreements
gh auth login
cd "$env:USERPROFILE\proyectos"; gh repo clone etmunoz/tarea_1_curso_2; cd tarea_1_curso_2
.\scripts\setup_windows.ps1            # (o -ConRedis para el RAG)
# luego:
.\scripts\win_servir.ps1               # terminal 1
.\scripts\win_tunel.ps1                # terminal 2 → copiar URL
# en el Mac:  ./scripts/mac_coordinador.sh "https://<tunel-win>#agente_tomas"
```

## Estado

Setup del Windows listo y documentado. Falta la corrida real cuando el otro equipo
esté configurado (intercambiar la URL del túnel y correr el coordinador en el Mac).
