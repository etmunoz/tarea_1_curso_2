#!/usr/bin/env bash
# --8<-- encabezado-grupo
# Archivo: scripts/mac_coordinador.sh
# Objetivo: mac_coordinador.sh del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1953
# Última modificación: 20261110 2227
# --8<-- fin-encabezado-grupo

# Mac (Ezequiel) · coordinador BIDIRECCIONAL: enruta a lo LOCAL (Ezequiel, cocina) y a
# lo REMOTO (Tomás, en el Windows, por su túnel HTTP de Cloudflare). Guarda la evidencia
# etiquetada "mac". Todo cruza por túneles HTTP; nada por TCP/LAN.
# Uso:  ./scripts/mac_coordinador.sh "https://<tunel-windows>"
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
for _ in 1 2 3 4; do [ -n "${CONDA_DEFAULT_ENV:-}" ] && conda deactivate 2>/dev/null || break; done
TUNEL_WIN="${1:?Uso: ./scripts/mac_coordinador.sh \"https://<tunel-windows>\"}"
TUNEL_WIN="${TUNEL_WIN%/}"

export A2A_BASE="${A2A_BASE:-http://127.0.0.1:2024}"
export A2A_GRAFOS_LOCALES="agente_ezequiel,agente_cocina"
export URLS_AGENTES="${TUNEL_WIN}#agente_tomas"
echo "Catálogo: local[$A2A_GRAFOS_LOCALES] + remoto[$URLS_AGENTES]"

uv run python tools/guardar_evidencias.py --etiqueta mac --preguntas \
  "¿Qué técnica uso si tengo desbalance de clases?" \
  "¿Qué símbolos se aprenden en el nivel 2 de Reiki?" \
  "¿Cuánto cuesta hacer un pastel de choclo para 4 personas?" \
  "¿Quién ganó el mundial de 1962?"
echo "✓ Evidencias del Mac: evidencias/04-catalogo-mac.txt y 05-ronda-mac.md"
