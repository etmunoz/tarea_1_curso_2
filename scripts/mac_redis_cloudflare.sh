#!/usr/bin/env bash
# --8<-- encabezado-grupo
# Archivo: scripts/mac_redis_cloudflare.sh
# Objetivo: mac_redis_cloudflare.sh del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2123
# Última modificación: 20261110 2124
# --8<-- fin-encabezado-grupo

# Mac (Ezequiel) · expone el Redis local por un TÚNEL TCP de Cloudflare (redes distintas).
# Requisitos: cuenta Cloudflare + un DOMINIO gestionado en Cloudflare + cloudflared.
# Uso:  ./scripts/mac_redis_cloudflare.sh redis-tomas.TU-DOMINIO.com
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
HOST="${1:?Uso: ./scripts/mac_redis_cloudflare.sh redis-tomas.TU-DOMINIO.com}"
NAME="reiki-redis"
command -v cloudflared >/dev/null || { echo "Instala cloudflared: brew install cloudflared"; exit 1; }
command -v docker >/dev/null && docker compose up -d >/dev/null 2>&1 || true

# 1) Login (una vez): abre el navegador y eliges tu dominio de Cloudflare.
[ -f "$HOME/.cloudflared/cert.pem" ] || cloudflared tunnel login

# 2) Crear el túnel con nombre (si no existe).
cloudflared tunnel list 2>/dev/null | awk '{print $2}' | grep -qx "$NAME" || cloudflared tunnel create "$NAME"
TID=$(cloudflared tunnel list 2>/dev/null | awk -v n="$NAME" '$2==n{print $1; exit}')

# 3) Config con ingress TCP -> Redis local.
CFG="$HOME/.cloudflared/${NAME}.yml"
cat > "$CFG" <<YML
tunnel: ${NAME}
credentials-file: ${HOME}/.cloudflared/${TID}.json
ingress:
  - hostname: ${HOST}
    service: tcp://localhost:6379
  - service: http_status:404
YML

# 4) Ruta DNS del host hacia este túnel.
cloudflared tunnel route dns "$NAME" "$HOST" 2>/dev/null || echo "(ruta DNS ya existía o requiere revisión en el panel de Cloudflare)"

echo "✓ Túnel TCP de Redis listo. Pásale al Windows este host:  $HOST"
echo "  En el Windows:  .\\scripts\\win_redis_cloudflare.ps1 $HOST"
echo "  (deja esta terminal abierta mientras dure la prueba)"
exec cloudflared tunnel run --config "$CFG" "$NAME"
