#!/usr/bin/env bash
# --8<-- encabezado-grupo
# Archivo: scripts/mac_servir.sh
# Objetivo: mac_servir.sh del proyecto.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1952
# Última modificación: 20261111 1857
# --8<-- fin-encabezado-grupo

# Mac · levanta el agente Ezequiel (langgraph dev) y configura su ficha cuando esté arriba.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."
for _ in 1 2 3 4; do [ -n "${CONDA_DEFAULT_ENV:-}" ] && conda deactivate 2>/dev/null || break; done

GRAFO="${1:-agente_ezequiel}"
uv sync
[ -f .env ] || { cp .env.example .env; echo "⚠ Creé .env — pon tu GOOGLE_API_KEY antes de usar el agente."; }
grep -q '^GOOGLE_API_KEY=.\+' .env || echo "⚠ Falta GOOGLE_API_KEY en .env (el agente no responderá sin ella)."

# Cuando el servidor responda, configura la ficha y guarda la evidencia.
( until curl -s http://127.0.0.1:2024/ok >/dev/null 2>&1; do sleep 1; done
  uv run python tools/configurar_fichas.py --grafos "$GRAFO" --guardar-evidencia ) &

echo "▶ langgraph dev (:2024) — Ctrl+C para parar"
exec uv run langgraph dev
