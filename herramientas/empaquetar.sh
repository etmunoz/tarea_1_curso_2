#!/usr/bin/env bash
# Arma el zip de entrega desde entrega/, sin secretos ni archivos generados.
# Uso:  bash herramientas/empaquetar.sh [N]      → grupo-N-taller-a2a.zip en la raíz del taller
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GRUPO="${1:-N}"
ZIP="$RAIZ/grupo-$GRUPO-taller-a2a.zip"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

cp -a "$RAIZ/entrega/." "$TMP/"
cp "$RAIZ/herramientas/preguntar.py" "$TMP/preguntar.py"     # cliente de terminal (lo cita el README)
for d in mi-agente segundo-agente; do
  rm -rf "$TMP/$d/.venv" "$TMP/$d/.langgraph_api" "$TMP/$d/.env" "$TMP/$d/src/swarm" "$TMP/$d/data"
done
find "$TMP" -name __pycache__ -type d -prune -exec rm -rf {} + -o -name .ipynb_checkpoints -type d -prune -exec rm -rf {} +

rm -f "$ZIP"
(cd "$TMP" && python3 - "$ZIP" <<'PY'
import os, sys, zipfile
with zipfile.ZipFile(sys.argv[1], "w", zipfile.ZIP_DEFLATED) as z:
    for raiz, _, archivos in os.walk("."):
        for a in sorted(archivos):
            ruta = os.path.join(raiz, a)[2:]
            z.write(ruta, ruta)
PY
)
# control: nada prohibido dentro del zip
if python3 -c "import sys,zipfile; n=zipfile.ZipFile(sys.argv[1]).namelist(); sys.exit(any(x.endswith('/.env') or x=='.env' or '/.venv/' in x or '.langgraph_api' in x or 'src/swarm' in x for x in n))" "$ZIP"; then
  echo "Listo: $ZIP ($(python3 -c "import sys,zipfile; print(len(zipfile.ZipFile(sys.argv[1]).namelist()))" "$ZIP") archivos, sin .env/.venv/.langgraph_api/src/swarm)"
else
  echo "ERROR: el zip contiene archivos prohibidos" >&2; exit 1
fi
