#!/usr/bin/env bash
# --8<-- encabezado-grupo
# Archivo: scripts/mac_app.sh
# Objetivo: mac_app.sh del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2140
# Última modificación: 20261111 0743
# --8<-- fin-encabezado-grupo

# Mac (Ezequiel) · app web para probar agentes uno a uno y vía coordinador.
# Config propia del Mac: locales ezequiel/cocina/viajes; remoto opcional = túnel del Windows.
# Uso:  ./scripts/mac_app.sh ["https://<tunel-windows>"]
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
for _ in 1 2 3 4; do [ -n "${CONDA_DEFAULT_ENV:-}" ] && conda deactivate 2>/dev/null || break; done
export APP_ROL="Mac · Ezequiel"
export A2A_GRAFOS_LOCALES="agente_ezequiel,agente_cocina,agente_viajes"
if [ "${1:-}" ]; then export URLS_AGENTES="${1%/}#agente_tomas"; fi
exec uv run python -m src.webapp.app
