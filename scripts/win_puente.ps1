# --8<-- encabezado-grupo
# Archivo: scripts/win_puente.ps1
# Objetivo: win_puente.ps1 del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 2049
# Última modificación: 20261111 2049
# --8<-- fin-encabezado-grupo

# Windows (Tomás) · levanta el PUENTE A2A clásico delante de agente_tomas para que
# tools/monitor_puente.py muestre quién consume el agente. langgraph dev nativo NO
# escribe el log del monitor; por eso se consume a través de este puente.
#
# Uso tipico (3 terminales):
#   1) .\scripts\win_puente.ps1                       # arranca el puente (:8791)
#   2) cloudflared tunnel --url http://127.0.0.1:8791 # copia la URL https que imprime
#   3) .\scripts\win_puente.ps1 "https://<tu-tunel>.trycloudflare.com"   # reinicia anunciando esa URL
#   4) uv run python tools\monitor_puente.py --log logs\puente-tomas.log # monitor Tkinter
#
# Parametros (o variables de entorno PUENTE_*):
param(
  [string]$UrlPublica = $env:PUENTE_URL_PUBLICA,  # URL del tunel vigente que la card anuncia
  [string]$Grafo      = $(if ($env:PUENTE_GRAFO) { $env:PUENTE_GRAFO } else { "agente_tomas" }),
  [int]   $Puerto     = $(if ($env:PUENTE_PORT)  { [int]$env:PUENTE_PORT } else { 8791 }),
  [string]$Base       = $(if ($env:PUENTE_BASE)  { $env:PUENTE_BASE } else { "http://127.0.0.1:2024" })
)
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."
for ($i=0; $i -lt 4 -and $env:CONDA_DEFAULT_ENV; $i++) { try { conda deactivate } catch { break } }

$env:PUENTE_BASE  = $Base
$env:PUENTE_GRAFO = $Grafo
$env:PUENTE_PORT  = "$Puerto"
# Log de accesos por defecto, para que el monitor Tkinter vea el trafico.
if (-not $env:PUENTE_LOG) { $env:PUENTE_LOG = Join-Path (Get-Location).Path "logs\puente-tomas.log" }
New-Item -ItemType Directory -Force -Path (Split-Path $env:PUENTE_LOG) | Out-Null
if ($UrlPublica) { $env:PUENTE_URL_PUBLICA = $UrlPublica.TrimEnd('/') }

Write-Host "Puente A2A -> grafo=$Grafo  puerto=$Puerto  log=$env:PUENTE_LOG"
if ($env:PUENTE_URL_PUBLICA) { Write-Host "Anuncia como endpoint: $env:PUENTE_URL_PUBLICA" }
else { Write-Host "Sin URL publica aun: levanta el tunel y reinicia pasando la URL como argumento." }
uv run python -m src.puente_a2a.servidor
