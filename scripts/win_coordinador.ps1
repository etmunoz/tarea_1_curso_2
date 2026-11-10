# --8<-- encabezado-grupo
# Archivo: scripts/win_coordinador.ps1
# Objetivo: win_coordinador.ps1 del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1952
# Última modificación: 20261110 2041
# --8<-- fin-encabezado-grupo

# Windows · corre el coordinador enrutando a Tomás (local) + el remoto que le pases, y guarda evidencias.
# Uso: .\scripts\win_coordinador.ps1 "https://<tunel-mac>#agente_ezequiel"
param([Parameter(Mandatory=$true)][string]$Remoto)
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."
for ($i=0; $i -lt 4 -and $env:CONDA_DEFAULT_ENV; $i++) { try { conda deactivate } catch { break } }
if (-not $env:A2A_BASE) { $env:A2A_BASE = "http://127.0.0.1:2024" }
if (-not $env:A2A_GRAFOS_LOCALES) { $env:A2A_GRAFOS_LOCALES = "agente_tomas" }
$env:URLS_AGENTES = $Remoto
Write-Host "Catalogo: local[$env:A2A_GRAFOS_LOCALES] + remoto[$Remoto]"
uv run python -m src.coordinador.graph
uv run python tools/guardar_evidencias.py
