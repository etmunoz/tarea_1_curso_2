#!/usr/bin/env bash
# --8<-- encabezado-grupo
# Archivo: scripts/mac_tunel.sh
# Objetivo: mac_tunel.sh del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1952
# Última modificación: 20261110 2322
# --8<-- fin-encabezado-grupo

# Mac · abre un túnel https a tu langgraph dev (:2024). Copia la URL que imprime.
set -euo pipefail
command -v cloudflared >/dev/null || { echo "Instala cloudflared: brew install cloudflared"; exit 1; }
exec cloudflared tunnel --url http://127.0.0.1:2024
