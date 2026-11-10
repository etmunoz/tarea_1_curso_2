#!/usr/bin/env bash
# --8<-- encabezado-grupo
# Archivo: scripts/mac_coordinador.sh
# Objetivo: mac_coordinador.sh del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1952
# Última modificación: 20261110 1952
# --8<-- fin-encabezado-grupo

# Mac · corre el coordinador enrutando a Ezequiel (local) + el remoto que le pases, y guarda evidencias.
# Uso: scripts/mac_coordinador.sh "https://<tunel-windows>#agente_tomas"
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
for _ in 1 2 3 4; do [ -n "${CONDA_DEFAULT_ENV:-}" ] && conda deactivate 2>/dev/null || break; done
REMOTO="${1:?Uso: scripts/mac_coordinador.sh \"https://<tunel>#agente_tomas\"}"
export A2A_BASE="${A2A_BASE:-http://127.0.0.1:2024}"
export A2A_GRAFOS_LOCALES="${A2A_GRAFOS_LOCALES:-agente_ezequiel}"
export URLS_AGENTES="$REMOTO"
echo "Catálogo: local[$A2A_GRAFOS_LOCALES] + remoto[$REMOTO]"
uv run python -m src.coordinador.graph
uv run python tools/guardar_evidencias.py
