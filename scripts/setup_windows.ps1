# --8<-- encabezado-grupo
# Archivo: scripts/setup_windows.ps1
# Objetivo: setup_windows.ps1 del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2113
# Última modificación: 20261110 2113
# --8<-- fin-encabezado-grupo

# Setup del Windows (agente Tomás) para la prueba A2A entre 2 computadores.
# Ejecútalo DESDE LA RAÍZ del repo ya clonado:  .\scripts\setup_windows.ps1
# Opcional:  .\scripts\setup_windows.ps1 -ConRedis   (además levanta Redis y carga el RAG)
param([switch]$ConRedis)
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

Write-Host "== 1/6 · Prerrequisitos ==" -ForegroundColor Green
if (-not (Tengo winget)) { throw "No hay winget (App Installer). Instálalo desde Microsoft Store y reintenta." }
if (-not (Tengo uv))          { Instala "astral-sh.uv" }
if (-not (Tengo cloudflared)) { Instala "Cloudflare.cloudflared" }
if ($ConRedis -and -not (Tengo docker)) { Instala "Docker.DockerDesktop"; Write-Host "⚠ Abre Docker Desktop una vez antes de usar -ConRedis." -ForegroundColor Yellow }
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

Write-Host "== 4/6 · Probar la API key ==" -ForegroundColor Green
uv run python tools/probar_gemini.py

if ($ConRedis) {
  Write-Host "== 5/6 · Redis + RAG (opcional) ==" -ForegroundColor Green
  docker compose up -d
  Start-Sleep -Seconds 3
  uv run python tools/cargar_rag_reiki.py
} else {
  Write-Host "== 5/6 · Redis/RAG omitido (corre con -ConRedis si lo quieres) ==" -ForegroundColor DarkGray
}

Write-Host "== 6/6 · Listo ==" -ForegroundColor Green
Write-Host @"
Siguientes pasos (una terminal PowerShell por línea):
  1) .\scripts\win_servir.ps1     # levanta Tomás (langgraph dev) + su ficha
  2) .\scripts\win_tunel.ps1      # abre el túnel; COPIA la URL https y pásala al Mac
  3) En el Mac:  ./scripts/mac_coordinador.sh "https://<tunel-win>#agente_tomas"
Si un .ps1 no corre por permisos:  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
"@ -ForegroundColor Cyan
