#!/usr/bin/env bash
# --8<-- encabezado-grupo
# Archivo: scripts/mac_redis.sh
# Objetivo: mac_redis.sh del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2123
# Última modificación: 20261110 2124
# --8<-- fin-encabezado-grupo

# Mac (Ezequiel) · ANFITRIÓN del Redis: lo levanta en local (dockerizado).
# Para compartirlo con el Windows por Cloudflare, usa scripts/mac_redis_cloudflare.sh
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
command -v docker >/dev/null || { echo "Instala/abre Docker Desktop primero."; exit 1; }
docker compose up -d
echo "✓ Redis arriba (Redis Stack · UI http://localhost:8001 · REDIS_URL=redis://localhost:6379)"
echo "  Para exponerlo al Windows por Cloudflare: ./scripts/mac_redis_cloudflare.sh <host.tudominio.com>"
