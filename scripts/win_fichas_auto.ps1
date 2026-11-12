# --8<-- encabezado-grupo
# Archivo: scripts/win_fichas_auto.ps1
# Objetivo: win_fichas_auto.ps1 del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 2049
# Última modificación: 20261111 2049
# --8<-- fin-encabezado-grupo

# Windows (Tomás) · mantiene las fichas (Agent Cards) aplicadas AUTOMÁTICAMENTE: langgraph dev
# recarga en caliente y resetea el name/description; este vigilante las re-aplica solo. Déjalo
# corriendo en una terminal aparte (Ctrl+C para parar).
# Uso:  .\scripts\win_fichas_auto.ps1 ["agente_tomas"]
param([string]$Grafos = "agente_tomas")
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."
for ($i=0; $i -lt 4 -and $env:CONDA_DEFAULT_ENV; $i++) { try { conda deactivate } catch { break } }
if (-not $env:A2A_BASE) { $env:A2A_BASE = "http://127.0.0.1:2024" }
uv run python tools\configurar_fichas.py --grafos $Grafos --vigilar
