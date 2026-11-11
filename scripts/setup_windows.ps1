# --8<-- encabezado-grupo
# Archivo: scripts/setup_windows.ps1
# Objetivo: setup_windows.ps1 del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2114
# Última modificación: 20261111 1204
# --8<-- fin-encabezado-grupo

# Setup del Windows (nodo Tomás) para la prueba A2A bidireccional entre 2 computadores.
# La MISMA repo sirve en ambos equipos; el rol lo definen las variables de entorno.
# Tomás usa su Redis LOCAL (dockerizado) para el RAG; nada se expone por TCP/LAN:
# el RAG se alcanza consultando al AGENTE Tomás por su túnel HTTP de Cloudflare.
#
# Ejecútalo DESDE LA RAÍZ del repo ya clonado:
#   .\scripts\setup_windows.ps1
#   .\scripts\setup_windows.ps1 -SinRag     # omite Docker/Redis/ingesta (Tomás degrada el RAG)
param([switch]$SinRag)
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
if (-not $SinRag -and -not (Tengo docker)) {
  Instala "Docker.DockerDesktop"
  Write-Host "⚠ Abre Docker Desktop UNA vez (acepta términos) y reabre PowerShell; luego re-corre este script." -ForegroundColor Yellow
}
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

Write-Host "== 5/6 · Redis LOCAL + RAG de Reiki ==" -ForegroundColor Green
if ($SinRag) {
  Write-Host "Omitido (-SinRag). Tomás responde, pero sin buscar_reiki." -ForegroundColor DarkGray
} elseif (-not (Tengo docker)) {
  Write-Host "⚠ Docker no está en el PATH aún. Abre Docker Desktop y re-corre el script (sin -SinRag)." -ForegroundColor Yellow
} else {
  docker compose up -d
  Start-Sleep -Seconds 4
  uv run python tools/cargar_rag_reiki.py   # ingesta en el Redis LOCAL
}

Write-Host "== 6/6 · Listo ==" -ForegroundColor Green
Write-Host @"
Siguientes pasos (una terminal PowerShell por línea):
  1) .\scripts\win_servir.ps1     # agente Tomás (langgraph dev) + su ficha
  2) .\scripts\win_tunel.ps1      # túnel HTTP de Tomás; COPIA la URL y pásala al Mac
  3) Pídele al Mac su URL de túnel y corre el coordinador desde Windows:
     .\scripts\win_coordinador.ps1 "https://<tunel-mac>"
Si un .ps1 no corre por permisos:  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
"@ -ForegroundColor Cyan
