# --8<-- encabezado-grupo
# Archivo: scripts/win_app.ps1
# Objetivo: win_app.ps1 del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2140
# Última modificación: 20261110 2147
# --8<-- fin-encabezado-grupo

# Windows (Tomás) · app web para probar agentes uno a uno y vía coordinador.
# Config propia del Windows: local tomas; remoto opcional = túnel del Mac.
# Uso:  .\scripts\win_app.ps1 ["https://<tunel-mac>"]
param([string]$TunelMac = "")
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."
for ($i=0; $i -lt 4 -and $env:CONDA_DEFAULT_ENV; $i++) { try { conda deactivate } catch { break } }
$env:APP_ROL = "Windows · Tomás"
$env:A2A_GRAFOS_LOCALES = "agente_tomas"
if ($TunelMac) { $t = $TunelMac.TrimEnd('/'); $env:URLS_AGENTES = "$t#agente_ezequiel,$t#agente_cocina" }
uv run python -m src.webapp.app
