# --8<-- encabezado-grupo
# Archivo: scripts/win_tunel.ps1
# Objetivo: win_tunel.ps1 del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1952
# Última modificación: 20261111 1224
# --8<-- fin-encabezado-grupo

# Windows · abre un túnel https a tu langgraph dev (:2024). Copia la URL que imprime y pásala al Mac.
$ErrorActionPreference = "Stop"
if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
  Write-Host "Instala cloudflared: winget install --id Cloudflare.cloudflared"; exit 1
}
cloudflared tunnel --url http://127.0.0.1:2024
