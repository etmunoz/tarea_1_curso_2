# --8<-- encabezado-grupo
# Archivo: scripts/win_redis_cloudflare.ps1
# Objetivo: win_redis_cloudflare.ps1 del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2123
# Última modificación: 20261110 2124
# --8<-- fin-encabezado-grupo

# Windows (Tomás) · abre el acceso TCP al Redis del Mac vía Cloudflare.
# Deja un forwarder local en localhost:6379 → Redis del Mac (por el túnel de Cloudflare).
# Uso:  .\scripts\win_redis_cloudflare.ps1 redis-tomas.TU-DOMINIO.com
# Requiere cloudflared (lo instala setup_windows.ps1). Deja esta terminal ABIERTA.
param([Parameter(Mandatory=$true)][string]$HostName, [int]$Port = 6379)
$ErrorActionPreference = "Stop"
if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
  Write-Host "Falta cloudflared. Corre antes .\scripts\setup_windows.ps1"; exit 1
}
Write-Host "Abriendo acceso a Redis del Mac ($HostName) en localhost:$Port ..." -ForegroundColor Cyan
Write-Host "En tu .env debe quedar: REDIS_URL=redis://localhost:$Port" -ForegroundColor DarkGray
cloudflared access tcp --hostname $HostName --url "localhost:$Port"
