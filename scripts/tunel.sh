#!/usr/bin/env bash

# Publica un puerto local mediante un túnel temporal de Cloudflare.

set -u

PUERTO="${1:-8000}"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "cloudflared no está instalado. Instálalo con: brew install cloudflared"
  exit 1
fi

echo "Abriendo túnel para http://127.0.0.1:${PUERTO}"
echo "Presiona Ctrl+C para cerrar el túnel."

cloudflared tunnel --url "http://127.0.0.1:${PUERTO}" 2>&1 | while IFS= read -r linea; do
  echo "$linea"
  direccion=$(printf '%s\n' "$linea" | grep -oE 'https://[-a-zA-Z0-9]+\.trycloudflare\.com' | head -n 1 || true)
  if [ -n "$direccion" ]; then
    echo
    echo "================================================================"
    echo "TÚNEL PÚBLICO: $direccion"
    echo "Pega esta dirección en URL_PUBLICA de tu .env y reinicia tu agente; pásasela a tu compañero para que la ponga en su URLS_AGENTES."
    echo "================================================================"
    echo
  fi
done
