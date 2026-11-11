#!/usr/bin/env bash
# --8<-- encabezado-grupo
# Archivo: scripts/mac_puente.sh
# Objetivo: mac_puente.sh del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 1342
# Última modificación: 20261111 1957
# --8<-- fin-encabezado-grupo

# Mac · levanta el PUENTE A2A clásico para que un cliente A2A estándar (p. ej. el de
# Gustavo) pueda consumir nuestro agente_ezequiel. Luego, en otra terminal, exponer el
# puente por Cloudflare y pasar esa URL al compañero:
#     cloudflared tunnel --url http://127.0.0.1:8790
# Uso:  ./scripts/mac_puente.sh ["https://<tunel-del-puente>"]   (la URL pública a anunciar)
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
for _ in 1 2 3 4; do [ -n "${CONDA_DEFAULT_ENV:-}" ] && conda deactivate 2>/dev/null || break; done
export PUENTE_BASE="${PUENTE_BASE:-http://127.0.0.1:2024}"
export PUENTE_GRAFO="${PUENTE_GRAFO:-agente_ezequiel}"
export PUENTE_PORT="${PUENTE_PORT:-8790}"
if [ "${1:-}" ]; then export PUENTE_URL_PUBLICA="${1%/}"; fi
exec uv run python -m src.puente_a2a.servidor
