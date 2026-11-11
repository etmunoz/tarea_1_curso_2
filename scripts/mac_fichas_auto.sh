#!/usr/bin/env bash
# --8<-- encabezado-grupo
# Archivo: scripts/mac_fichas_auto.sh
# Objetivo: mac_fichas_auto.sh del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 2016
# Última modificación: 20261111 2016
# --8<-- fin-encabezado-grupo

# Mac · mantiene las fichas (Agent Cards) aplicadas AUTOMÁTICAMENTE: re-aplica tras cada recarga
# en caliente de `langgraph dev` (que las resetea). Déjalo en una terminal aparte.
# Uso:  ./scripts/mac_fichas_auto.sh ["agente_ezequiel,agente_cocina"]
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
for _ in 1 2 3 4; do [ -n "${CONDA_DEFAULT_ENV:-}" ] && conda deactivate 2>/dev/null || break; done
export A2A_BASE="${A2A_BASE:-http://127.0.0.1:2024}"
exec uv run python tools/configurar_fichas.py --grafos "${1:-agente_ezequiel,agente_cocina}" --vigilar
