#!/usr/bin/env bash
# Lanza el Taller 05: los dos agentes (2025 y 2026), sus tarjetas y los túneles de Cloudflare.
# Uso:
#   ./lanzar.sh                 # los dos agentes + túnel para cada uno
#   ./lanzar.sh --solo-fabio    # los dos agentes, pero túnel solo para el Agente Fabio (2025)
#   ./lanzar.sh --sin-tunel     # solo local, sin Cloudflare
#   ./lanzar.sh --puente        # cada túnel pasa por herramientas/puente.py: tarjeta sin assistant_id y A2A en «/»
#                               # (se combina: ./lanzar.sh --puente --solo-fabio)
# Ctrl+C detiene todo (servidores, puentes y túneles).
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENTREGA="$RAIZ/entrega"
LOGS="$RAIZ/logs"
mkdir -p "$LOGS"

TUNELES="ambos"
PUENTE="no"
for opcion in "$@"; do
  case "$opcion" in
    --solo-fabio) TUNELES="fabio" ;;
    --sin-tunel)  TUNELES="ninguno" ;;
    --puente)     PUENTE="si" ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "Opción desconocida: $opcion (usa --help)"; exit 1 ;;
  esac
done
[ "$PUENTE" = "si" ] && [ "$TUNELES" = "ninguno" ] && echo "Nota: --puente sin túnel deja los puentes solo en local."
declare -A PUERTO_PUENTE=([fabio]=8791 [proteinman]=8792)
declare -A NOMBRE_TARJETA=([fabio]="Agente Fabio" [proteinman]="ProteinMAN")

# nombre|carpeta|puerto|grafo|nombre de tarjeta|descripción de tarjeta
AGENTES=(
  "fabio|mi-agente|2025|agente_fabio|Agente Fabio|Especialista en bioinformática. Puede: explicar conceptos de bioinformática, comparar herramientas y bases de datos con criterios claros, diseñar un pipeline de análisis paso a paso."
  "proteinman|segundo-agente|2026|proteinman|ProteinMAN|Especialista en IA y Data Science aplicada a bioinformática. Puede: recomendar técnicas de machine learning para problemas con datos biológicos, sugerir métricas para evaluar modelos bioinformáticos, elegir un modelo según el tipo de dato biológico (secuencias, expresión génica, estructuras)."
)

PIDS=()
detener() {
  echo
  echo "Deteniendo servidores y túneles…"
  for pid in "${PIDS[@]}"; do kill "$pid" 2>/dev/null; done
  wait 2>/dev/null
  echo "Listo. Las URLs públicas ya no funcionan."
}
trap detener EXIT
trap 'exit 130' INT TERM

fallar() { echo "ERROR: $*" >&2; exit 1; }

# ── comprobaciones previas ────────────────────────────────────────────────────
command -v curl >/dev/null || fallar "falta curl"
command -v python3 >/dev/null || fallar "falta python3"
[ "$TUNELES" = "ninguno" ] || command -v cloudflared >/dev/null || fallar "falta cloudflared (o usa --sin-tunel)"

for a in "${AGENTES[@]}"; do
  IFS='|' read -r _ dir puerto _ _ _ <<<"$a"
  [ -x "$ENTREGA/$dir/.venv/bin/langgraph" ] || fallar "no existe $dir/.venv con langgraph (crea el entorno e instala requirements.txt)"
  grep -qE '^GOOGLE_API_KEY=.+' "$ENTREGA/$dir/.env" 2>/dev/null || fallar "$dir/.env no tiene GOOGLE_API_KEY (cp .env.example .env y pega la clave)"
  if curl -s -o /dev/null "http://127.0.0.1:$puerto/ok"; then
    fallar "el puerto $puerto ya está en uso (¿quedó otro langgraph dev abierto?)"
  fi
done
if [ "$PUENTE" = "si" ]; then
  [ -f "$RAIZ/herramientas/puente.py" ] || fallar "falta herramientas/puente.py"
  for id in fabio proteinman; do
    curl -s -o /dev/null "http://127.0.0.1:${PUERTO_PUENTE[$id]}/ok" && fallar "el puerto ${PUERTO_PUENTE[$id]} (puente) ya está en uso"
  done
fi

# Extrae un campo del JSON de stdin; sin traceback: si el JSON no sirve, sale con error y no imprime nada.
json() { python3 -c "
import json, sys
try:
    d = json.load(sys.stdin); print($1)
except Exception:
    sys.exit(1)" 2>/dev/null; }

esperar_ok() {  # url, segundos, [respuestas seguidas requeridas]
  local seguidas=0 requeridas="${3:-1}"
  for _ in $(seq 1 "$2"); do
    if [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$1/ok")" = 200 ]; then
      seguidas=$((seguidas + 1))
      [ "$seguidas" -ge "$requeridas" ] && return 0
    else
      seguidas=0
    fi
    sleep 1
  done
  return 1
}

# Busca el assistant_id de un grafo, reintentando (un túnel recién creado falla de forma intermitente
# los primeros segundos mientras se propaga su DNS).
assistant_id() {  # base, grafo, intentos
  local aid
  for _ in $(seq 1 "$3"); do
    aid=$(curl -s --max-time 15 -X POST "$1/assistants/search" -H 'Content-Type: application/json' \
          -d "{\"graph_id\":\"$2\"}" | json "d[0]['assistant_id']") && [ -n "$aid" ] && { echo "$aid"; return 0; }
    sleep 2
  done
  return 1
}

nombre_tarjeta() {  # base, assistant_id, intentos
  local n
  for _ in $(seq 1 "$3"); do
    n=$(curl -s --max-time 15 "$1/.well-known/agent-card.json?assistant_id=$2" | json "d['name']") \
      && [ -n "$n" ] && { echo "$n"; return 0; }
    sleep 2
  done
  return 1
}

# ── 1 · servidores ───────────────────────────────────────────────────────────
for a in "${AGENTES[@]}"; do
  IFS='|' read -r id dir puerto _ _ _ <<<"$a"
  echo "▶ Levantando $dir en el puerto $puerto (log: logs/servidor-$id.log)"
  ( cd "$ENTREGA/$dir" && exec .venv/bin/langgraph dev --port "$puerto" --no-browser ) >"$LOGS/servidor-$id.log" 2>&1 &
  PIDS+=($!)
done

for a in "${AGENTES[@]}"; do
  IFS='|' read -r id _ puerto _ _ _ <<<"$a"
  esperar_ok "http://127.0.0.1:$puerto" 120 || fallar "el servidor $puerto no respondió; revisa logs/servidor-$id.log"
  echo "  ✓ http://127.0.0.1:$puerto listo"
done

# ── 2 · tarjetas (nombre y descripción) ───────────────────────────────────────
# Si editas el código con el servidor arriba, langgraph dev recarga el grafo y la tarjeta vuelve al nombre
# por defecto (agente_fabio). Por eso esta función también se ejecuta cada pocos segundos más abajo.
aplicar_tarjetas() {  # "inicio" imprime cada tarjeta; "vigilar" avisa solo cuando restaura una
  local modo="$1" a puerto grafo nombre desc base aid actual cuerpo
  for a in "${AGENTES[@]}"; do
    IFS='|' read -r _ _ puerto grafo nombre desc <<<"$a"
    base="http://127.0.0.1:$puerto"
    if [ "$modo" = "inicio" ]; then
      aid=$(assistant_id "$base" "$grafo" 5) || fallar "no encontré el grafo $grafo en $base"
    else
      aid=$(assistant_id "$base" "$grafo" 1) || continue   # servidor recargando: se reintenta en la próxima vuelta
      actual=$(curl -s --max-time 5 "$base/assistants/$aid" | json "d.get('name','')") || continue
      [ "$actual" = "$nombre" ] && continue
    fi
    cuerpo=$(NOMBRE="$nombre" DESC="$desc" python3 -c 'import json,os; print(json.dumps({"name":os.environ["NOMBRE"],"description":os.environ["DESC"]}))')
    curl -s -o /dev/null -X PATCH "$base/assistants/$aid" -H 'Content-Type: application/json' -d "$cuerpo"
    if [ "$modo" = "inicio" ]; then
      echo "  ✓ tarjeta «$nombre» · assistant_id $aid"
    else
      echo "  ↻ $(date +%H:%M:%S) el servidor $puerto recargó el código: tarjeta «$nombre» restaurada"
    fi
  done
}
aplicar_tarjetas inicio

# ── 2b · puentes (opcional) ──────────────────────────────────────────────────
# herramientas/puente.py publica un solo agente: tarjeta sin assistant_id y A2A en «/» (y reenvía el resto de la API).
if [ "$PUENTE" = "si" ]; then
  for a in "${AGENTES[@]}"; do
    IFS='|' read -r id dir _ _ _ _ <<<"$a"
    pp=${PUERTO_PUENTE[$id]}
    echo "▶ Levantando puente de $id en el puerto $pp (log: logs/puente-$id.log)"
    "$ENTREGA/$dir/.venv/bin/python" "$RAIZ/herramientas/puente.py" "$id" --puerto "$pp" >"$LOGS/puente-$id.log" 2>&1 &
    PIDS+=($!)
  done
  for id in fabio proteinman; do
    esperar_ok "http://127.0.0.1:${PUERTO_PUENTE[$id]}" 20 || fallar "el puente de $id no arrancó; revisa logs/puente-$id.log"
    echo "  ✓ puente http://127.0.0.1:${PUERTO_PUENTE[$id]} listo"
  done
fi

# ── 3 · túneles ──────────────────────────────────────────────────────────────
declare -A URLS=()
if [ "$TUNELES" != "ninguno" ]; then
  for a in "${AGENTES[@]}"; do
    IFS='|' read -r id _ puerto _ _ _ <<<"$a"
    [ "$TUNELES" = "fabio" ] && [ "$id" != "fabio" ] && continue
    destino=$puerto
    [ "$PUENTE" = "si" ] && destino=${PUERTO_PUENTE[$id]}   # el túnel apunta al puente, no al servidor
    echo "▶ Abriendo túnel para el puerto $destino (log: logs/tunel-$id.log)"
    # 127.0.0.1 y no localhost: langgraph dev escucha solo en IPv4 y localhost también resuelve a ::1.
    # --grace-period 2s: al detener, no esperar 30 s por peticiones en curso.
    cloudflared tunnel --no-autoupdate --grace-period 2s --url "http://127.0.0.1:$destino" >"$LOGS/tunel-$id.log" 2>&1 &
    PIDS+=($!)
  done

  for a in "${AGENTES[@]}"; do
    IFS='|' read -r id _ puerto grafo nombre _ <<<"$a"
    [ "$TUNELES" = "fabio" ] && [ "$id" != "fabio" ] && continue
    url=""
    for _ in $(seq 1 60); do
      url=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOGS/tunel-$id.log" | head -1)
      [ -n "$url" ] && break
      sleep 1
    done
    [ -n "$url" ] || fallar "cloudflared no entregó URL para $puerto; revisa logs/tunel-$id.log"
    # El DNS de la URL nueva tarda unos segundos en propagarse y al principio falla de forma
    # intermitente: se exigen 3 respuestas seguidas y cada consulta se reintenta.
    echo "  … esperando que $url responda de forma estable"
    esperar_ok "$url" 90 3 || fallar "la URL $url no responde de forma estable; revisa logs/tunel-$id.log"
    aid=$(assistant_id "$url" "$grafo" 30) || fallar "por el túnel no pude obtener el assistant_id de $grafo ($url)"
    tarjeta=$(nombre_tarjeta "$url" "$aid" 30) || fallar "por el túnel no pude leer la tarjeta de $grafo ($url)"
    [ "$tarjeta" = "$nombre" ] || fallar "la tarjeta por el túnel dice «$tarjeta» y no «$nombre»"
    if [ "$PUENTE" = "si" ]; then  # la tarjeta clásica: sin assistant_id y anunciando la URL del túnel
      clasica=""
      for _ in $(seq 1 15); do
        clasica=$(curl -s --max-time 15 "$url/.well-known/agent-card.json" | json "d['name'] + '|' + d['url']") && [ -n "$clasica" ] && break
        sleep 2
      done
      [ "$clasica" = "$nombre|$url" ] || fallar "el puente no entrega la tarjeta clásica correcta por $url (recibí «$clasica»)"
    fi
    URLS[$id]="$url"
    echo "  ✓ $nombre público en $url (tarjeta verificada desde fuera)"
  done
fi

# ── resumen ──────────────────────────────────────────────────────────────────
echo
echo "════════════════════════════════════════════════════════════════════"
echo " Todo arriba. Local:  http://127.0.0.1:2025 (Agente Fabio) · http://127.0.0.1:2026 (ProteinMAN)"
if [ "${#URLS[@]}" -gt 0 ]; then
  echo " Para tus compañeros (bloque 1 de «Ejemplo real» de su notebook):"
  echo
  echo "   SERVIDORES = ["
  echo "       \"http://127.0.0.1:2025\",  # su propio agente"
  for id in fabio proteinman; do
    [ -n "${URLS[$id]:-}" ] && echo "       \"${URLS[$id]}\",  # Agente ${id^}"
  done
  echo "   ]"
  if [ "$PUENTE" = "si" ]; then
    echo
    echo " Con puente: cualquier cliente A2A estándar sirve, sin assistant_id. Por ejemplo:"
    for id in fabio proteinman; do
      [ -n "${URLS[$id]:-}" ] || continue
      echo "   curl -s ${URLS[$id]}/.well-known/agent-card.json"
      echo "   curl -s -X POST ${URLS[$id]}/ -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":\"1\",\"method\":\"message/send\",\"params\":{\"message\":{\"role\":\"user\",\"messageId\":\"m1\",\"contextId\":\"mi-hilo\",\"parts\":[{\"kind\":\"text\",\"text\":\"Hola\"}]}}}'"
    done
  fi
  echo
  echo " Ojo: con la URL cualquiera consume tu cuota de Gemini. Compártela solo en clase."
fi
echo " Notebooks: primero segundo-agente/notebooks/a2a-test.ipynb, luego mi-agente/notebooks/a2a-test.ipynb"
echo " Ctrl+C para detener todo."
echo "════════════════════════════════════════════════════════════════════"

# mantenerse vivo mientras corran los procesos; si alguno muere, avisar y cerrar todo
# y, cada ~10 s, restaurar las tarjetas si un servidor recargó el código
vuelta=0
while true; do
  for pid in "${PIDS[@]}"; do
    if ! kill -0 "$pid" 2>/dev/null; then
      echo "Un proceso se detuvo (PID $pid). Revisa logs/. Cerrando todo."
      exit 1
    fi
  done
  vuelta=$((vuelta + 1))
  [ $((vuelta % 5)) -eq 0 ] && aplicar_tarjetas vigilar
  sleep 2
done
