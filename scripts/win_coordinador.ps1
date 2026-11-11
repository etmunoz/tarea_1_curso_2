# --8<-- encabezado-grupo
# Archivo: scripts/win_coordinador.ps1
# Objetivo: win_coordinador.ps1 del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1953
# Última modificación: 20261111 1205
# --8<-- fin-encabezado-grupo

# Windows (Tomás) · coordinador BIDIRECCIONAL: enruta a lo LOCAL (Tomás) y a lo REMOTO
# (Ezequiel y cocina, en el Mac, por su túnel HTTP de Cloudflare). Guarda la evidencia
# etiquetada "windows". Todo cruza por túneles HTTP; nada por TCP/LAN.
# Uso:  .\scripts\win_coordinador.ps1 "https://<tunel-mac>"
param([Parameter(Mandatory=$true)][string]$TunelMac)
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot\.."
for ($i=0; $i -lt 4 -and $env:CONDA_DEFAULT_ENV; $i++) { try { conda deactivate } catch { break } }
$TunelMac = $TunelMac.TrimEnd('/')

if (-not $env:A2A_BASE) { $env:A2A_BASE = "http://127.0.0.1:2024" }
$env:A2A_GRAFOS_LOCALES = "agente_tomas"
$env:URLS_AGENTES = "$TunelMac#agente_ezequiel,$TunelMac#agente_cocina"
Write-Host "Catalogo: local[$env:A2A_GRAFOS_LOCALES] + remoto[$env:URLS_AGENTES]"

uv run python tools/guardar_evidencias.py --etiqueta windows --preguntas `
  "¿Cuáles son los cinco principios del Reiki?" `
  "¿Qué métricas uso en un problema de regresión?" `
  "¿Cuánto cuesta una cazuela de vacuno para 6 personas?" `
  "¿Quién descubrió América?"
Write-Host "OK Evidencias del Windows: evidencias/04-catalogo-windows.txt y 05-ronda-windows.md"
