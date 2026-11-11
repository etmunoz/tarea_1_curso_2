# --8<-- encabezado-grupo
# Archivo: scripts/setup_windows.ps1
# Objetivo: setup_windows.ps1 del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2114
# Última modificación: 20261110 2124
# --8<-- fin-encabezado-grupo

# Setup del Windows (agente Tomás) para la prueba A2A entre 2 computadores.
# Reparto: el Redis lo ANFITRIONA el Mac (Ezequiel). Tomás (aquí) corre el RAG
# apuntando su REDIS_URL al Redis del Mac. Por eso Windows NO instala Docker.
#
# Ejecútalo DESDE LA RAÍZ del repo ya clonado:
#   .\scripts\setup_windows.ps1 -RedisUrl redis://localhost:6379
# Reparto por Cloudflare: el Redis vive en el Mac; en el Windows se alcanza por un
# forwarder local (scripts/win_redis_cloudflare.ps1), por eso REDIS_URL=redis://localhost:6379.
# La ingesta del RAG (cargar_rag_reiki.py) se corre DESPUÉS, con ese forwarder abierto.
# Parámetros:
#   -RedisUrl <url>  se escribe en .env (para el reparto por Cloudflare: redis://localhost:6379).
#   -CargarRag       ingesta el RAG ya (solo si el forwarder de Redis ya está abierto).
param([string]$RedisUrl = "", [switch]$CargarRag)
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."

function Refresh-Path {
  $m = [System.Environment]::GetEnvironmentVariable("Path","Machine")
  $u = [System.Environment]::GetEnvironmentVariable("Path","User")
  $env:Path = "$m;$u;$env:USERPROFILE\.local\bin"
}
function Tengo($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function Instala($id) {
  Write-Host "Instalando $id ..." -ForegroundColor Cyan
  winget install -e --id $id --accept-source-agreements --accept-package-agreements --silent
  Refresh-Path
}

Write-Host "== 1/6 · Prerrequisitos (uv, cloudflared) ==" -ForegroundColor Green
if (-not (Tengo winget)) { throw "No hay winget (App Installer). Instálalo desde Microsoft Store y reintenta." }
if (-not (Tengo uv))          { Instala "astral-sh.uv" }
if (-not (Tengo cloudflared)) { Instala "Cloudflare.cloudflared" }
Refresh-Path
if (-not (Tengo uv)) { throw "uv no quedó en el PATH. Cierra y reabre PowerShell y vuelve a correr este script." }

Write-Host "== 2/6 · Python 3.13 + dependencias ==" -ForegroundColor Green
uv python install 3.13
uv sync

Write-Host "== 3/6 · Archivo .env ==" -ForegroundColor Green
if (-not (Test-Path .env)) { Copy-Item .env.example .env; Write-Host "Creado .env desde .env.example." }
if (-not (Select-String -Path .env -Pattern '^GOOGLE_API_KEY=.+' -Quiet)) {
  $k = Read-Host "Pega tu GOOGLE_API_KEY (Gemini, la misma del Mac)"
  (Get-Content .env) -replace '^GOOGLE_API_KEY=.*', "GOOGLE_API_KEY=$k" | Set-Content .env -Encoding utf8
  Write-Host "Clave guardada en .env (no se versiona)." -ForegroundColor DarkGray
}
if ($RedisUrl) {
  (Get-Content .env) -replace '^REDIS_URL=.*', "REDIS_URL=$RedisUrl" | Set-Content .env -Encoding utf8
  Write-Host "REDIS_URL = $RedisUrl (Redis del Mac)." -ForegroundColor DarkGray
}

Write-Host "== 4/6 · Probar la API key ==" -ForegroundColor Green
uv run python tools/probar_gemini.py

Write-Host "== 5/6 · RAG (Reiki) ==" -ForegroundColor Green
if ($CargarRag) {
  if (-not $RedisUrl) { Write-Host "⚠ -CargarRag necesita -RedisUrl (el Redis del Mac). Omitido." -ForegroundColor Yellow }
  else {
    Write-Host "Ingestando documentos de Reiki al Redis del Mac ($RedisUrl) ..."
    uv run python tools/cargar_rag_reiki.py
  }
} else {
  Write-Host "RAG no ingestado (pasa -RedisUrl ... -CargarRag para hacerlo). Tomás igual responde sin él." -ForegroundColor DarkGray
}

Write-Host "== 6/6 · Listo ==" -ForegroundColor Green
Write-Host @"
Siguientes pasos (una terminal PowerShell por cada línea):
  1) .\scripts\win_servir.ps1     # levanta Tomás (langgraph dev) + su ficha
  2) .\scripts\win_tunel.ps1      # abre el túnel; COPIA la URL https y pásala al Mac
  3) En el Mac:  ./scripts/mac_coordinador.sh "https://<tunel-win>#agente_tomas"
Si un .ps1 no corre por permisos:  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
"@ -ForegroundColor Cyan
