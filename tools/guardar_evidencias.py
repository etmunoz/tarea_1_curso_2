# --8<-- encabezado-grupo
# Archivo: tools/guardar_evidencias.py
# Objetivo: Guarda evidencias del coordinador a `evidencias/` (Paso 7–8 del taller).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1952
# Última modificación: 20261110 2009
# --8<-- fin-encabezado-grupo

"""Guarda evidencias del coordinador a `evidencias/` (Paso 7–8 del taller).

- `04-catalogo.txt`: el catálogo de agentes con sus fichas (solo necesita el servidor).
- `05-ronda.md`: una ronda de preguntas con la ruta del supervisor y la respuesta
  `[Nombre] …` (necesita el servidor Y `GOOGLE_API_KEY`).

Las fichas JSON (`02-ficha-<grafo>.json`) las guarda `tools/configurar_fichas.py`.
Las capturas PNG (01, 03) son manuales (ver `evidencias/README.md`).

Uso:
    python tools/guardar_evidencias.py
    python tools/guardar_evidencias.py --preguntas "¿Qué es Cho Ku Rei?" "¿Qué técnica para pocos datos?"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))  # permite `python tools/…` con imports `src.*`

from dotenv import load_dotenv  # noqa: E402

from src.coordinador.catalogo import construir_catalogo, texto_catalogo  # noqa: E402

load_dotenv()
EV = RAIZ / "evidencias"

PREGUNTAS_DEF = [
    "¿Qué técnica uso si tengo desbalance de clases?",
    "¿Para qué sirve el símbolo Cho Ku Rei en Reiki?",
    "¿Cuánto cuesta un vuelo de Santiago a Lima?",
    "¿Quién ganó el mundial de 1962?",
]


def guardar_catalogo() -> None:
    EV.mkdir(exist_ok=True)
    texto = texto_catalogo(construir_catalogo())
    (EV / "04-catalogo.txt").write_text(texto + "\n", encoding="utf-8")
    print("✓ evidencias/04-catalogo.txt")
    print(texto)


def guardar_ronda(preguntas: list[str]) -> None:
    try:
        from langchain_core.messages import HumanMessage  # noqa: PLC0415

        from src.coordinador.graph import graph  # import tardío: construye Gemini (requiere key)
    except Exception as exc:  # noqa: BLE001
        print(f"· ronda omitida: {exc}\n  (requiere GOOGLE_API_KEY y `langgraph dev` arriba)")
        return

    hilo = {"configurable": {"thread_id": "evidencia-ronda"}}
    lineas = ["# Ronda de preguntas · evidencia\n"]
    for p in preguntas:
        r = graph.invoke({"messages": [HumanMessage(content=p)]}, hilo)
        ruta = " → ".join(r.get("ruta", []))
        lineas.append(f"**> {p}**\n\n- ruta: {ruta}\n- {r.get('respuesta', '')}\n")
        print(f"  > {p}\n    {ruta} :: {r.get('respuesta', '')[:80]}")
    EV.mkdir(exist_ok=True)
    (EV / "05-ronda.md").write_text("\n".join(lineas), encoding="utf-8")
    print("✓ evidencias/05-ronda.md")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--preguntas", nargs="*", default=None)
    args = ap.parse_args()
    guardar_catalogo()
    guardar_ronda(args.preguntas or PREGUNTAS_DEF)


if __name__ == "__main__":
    main()
