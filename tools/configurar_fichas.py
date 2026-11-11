# --8<-- encabezado-grupo
# Archivo: tools/configurar_fichas.py
# Objetivo: Aplica las fichas (Agent Card) a los agentes de un servidor `langgraph dev`.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1952
# Última modificación: 20261111 2049
# --8<-- fin-encabezado-grupo

"""Aplica las fichas (Agent Card) a los agentes de un servidor `langgraph dev`.

Hace `PATCH /assistants/<id>` con el `name` y la `description` de `src/fichas.py`,
y puede guardar cada tarjeta resultante como evidencia. Requiere el servidor arriba
(no requiere GOOGLE_API_KEY: solo toca la tarjeta, no ejecuta el agente).

Uso:
    python tools/configurar_fichas.py                       # aplica a los grafos de src/fichas.py
    python tools/configurar_fichas.py --grafos agente_tomas # solo ese
    python tools/configurar_fichas.py --guardar-evidencia    # + guarda evidencias/02-ficha-<grafo>.json
    python tools/configurar_fichas.py --base http://127.0.0.1:2024
    python tools/configurar_fichas.py --vigilar              # re-aplica SOLO cuando langgraph las borra
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))  # permite `python tools/…` con imports `src.*`

import httpx  # noqa: E402

from src.coordinador import a2a  # noqa: E402
from src.fichas import FICHAS  # noqa: E402


def configurar(base: str, grafos: list[str], guardar: bool) -> None:
    """Objetivo: aplicar la ficha (PATCH name+description) a cada grafo y, opcional, guardar evidencia.
    Entradas: base (str) servidor, grafos (list[str]), guardar (bool) para volcar la card a evidencias/.
    Salida: None (imprime el resultado por grafo)."""
    base = base.rstrip("/")
    ev = RAIZ / "evidencias"
    for graph in grafos:
        ficha = FICHAS.get(graph)
        if not ficha:
            print(f"· {graph}: sin ficha en src/fichas.py, se omite")
            continue
        try:
            aid = a2a.assistant_id(base, graph)
            httpx.patch(f"{base}/assistants/{aid}", json=ficha, timeout=10).raise_for_status()
            card = httpx.get(f"{base}/.well-known/agent-card.json", params={"assistant_id": aid}, timeout=10).json()
            print(f"✓ {graph}: «{card.get('name')}» — {card.get('description', '')[:70]}…")
            if guardar:
                ev.mkdir(exist_ok=True)
                destino = ev / f"02-ficha-{graph}.json"
                destino.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"  evidencia → {destino.relative_to(RAIZ)}")
        except Exception as exc:  # noqa: BLE001 - reportar y seguir
            print(f"✗ {graph}: {exc}  (¿está corriendo `langgraph dev` en {base}?)")


def _nombre_actual(base: str, graph: str) -> str | None:
    """Objetivo: nombre que tiene AHORA la Agent Card de un grafo (para detectar si se reseteó).
    Entradas: base (str), graph (str). Salida: str | None (None si no se pudo consultar)."""
    base = base.rstrip("/")
    a2a._cache_aid.pop((base, graph), None)  # el reload puede cambiar el id: pedirlo fresco
    aid = a2a.assistant_id(base, graph)
    card = httpx.get(f"{base}/.well-known/agent-card.json", params={"assistant_id": aid}, timeout=10).json()
    return card.get("name")


def vigilar(base: str, grafos: list[str], intervalo: float) -> None:
    """Objetivo: mantener las fichas aplicadas AUTOMÁTICAMENTE. langgraph dev recarga en caliente y
    resetea el name/description de cada agente; este modo las re-aplica SOLO cuando detecta que una
    volvió a su nombre genérico (no hace PATCH si ya están bien). Entradas: base, grafos, intervalo
    (segundos). Salida: None (corre hasta Ctrl+C)."""
    base = base.rstrip("/")
    print(f"Vigilando fichas en {base} cada {intervalo:g}s (Ctrl+C para parar)…")
    configurar(base, grafos, guardar=False)  # aplicar al arrancar
    while True:
        time.sleep(intervalo)
        for graph in grafos:
            ficha = FICHAS.get(graph)
            if not ficha:
                continue
            try:
                if _nombre_actual(base, graph) != ficha.get("name"):
                    aid = a2a.assistant_id(base, graph)
                    httpx.patch(f"{base}/assistants/{aid}", json=ficha, timeout=10).raise_for_status()
                    print(f"[{datetime.now():%H:%M:%S}] ↻ {graph}: ficha re-aplicada «{ficha.get('name')}» (se había reseteado)")
            except Exception:  # noqa: BLE001 - servidor recargando/caído: reintenta el próximo tick
                a2a._cache_aid.pop((base, graph), None)


def main() -> None:
    """Objetivo: CLI para configurar fichas. Entradas: --base, --grafos, --guardar-evidencia,
    --vigilar, --intervalo. Salida: None."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default=os.environ.get("A2A_BASE", "http://127.0.0.1:2024"))
    ap.add_argument("--grafos", default=",".join(FICHAS), help="Grafos a configurar, separados por comas.")
    ap.add_argument("--guardar-evidencia", action="store_true")
    ap.add_argument("--vigilar", action="store_true",
                    help="Queda corriendo y re-aplica las fichas automáticamente tras cada recarga.")
    ap.add_argument("--intervalo", type=float, default=float(os.environ.get("FICHAS_INTERVALO", "5")),
                    help="Segundos entre chequeos en modo --vigilar (def. 5).")
    args = ap.parse_args()
    grafos = [g.strip() for g in args.grafos.split(",") if g.strip()]
    if args.vigilar:
        try:
            vigilar(args.base, grafos, args.intervalo)
        except KeyboardInterrupt:
            print("\nVigilancia detenida.")
    else:
        configurar(args.base, grafos, args.guardar_evidencia)


if __name__ == "__main__":
    main()
