# --8<-- encabezado-grupo
# Archivo: scripts/win_servir.ps1
# Objetivo: win_servir.ps1 del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1952
# Última modificación: 20261111 1406
# --8<-- fin-encabezado-grupo

# Windows · levanta el agente Tomás (langgraph dev) y configura su ficha cuando esté arriba.
param([string]$Grafo = "agente_tomas")
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."
for ($i=0; $i -lt 4 -and $env:CONDA_DEFAULT_ENV; $i++) { try { conda deactivate } catch { break } }

uv sync
if (-not (Test-Path .env)) { Copy-Item .env.example .env; Write-Host "WARN: creé .env - pon tu GOOGLE_API_KEY." }
if (-not (Select-String -Path .env -Pattern '^GOOGLE_API_KEY=.+' -Quiet)) { Write-Host "WARN: falta GOOGLE_API_KEY en .env." }

# Cuando el servidor responda, configura la ficha y guarda la evidencia.
$raiz = (Get-Location).Path
Start-Job -ScriptBlock {
  Set-Location $using:raiz
  while ($true) { try { if ((Invoke-WebRequest http://127.0.0.1:2024/ok -UseBasicParsing -TimeoutSec 3).StatusCode -eq 200) { break } } catch { Start-Sleep 1 } }
  uv run python tools/configurar_fichas.py --grafos $using:Grafo --guardar-evidencia
} | Out-Null

Write-Host "langgraph dev (:2024) - Ctrl+C para parar"
uv run langgraph dev
