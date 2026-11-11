# --8<-- encabezado-grupo
# Archivo: tools/guardar_evidencias.py
# Objetivo: Guarda evidencias del coordinador a `evidencias/` (Paso 7–8 del taller).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1952
# Última modificación: 20261110 2322
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


def _con_encabezado(path: Path) -> None:
    """Objetivo: poner el encabezado del grupo (CONVENCIONES.md) a una evidencia recién escrita.
    Antes se escribían sin encabezado y `aplicar_encabezados.py --check` fallaba.
    Entradas: path (Path) del archivo. Salida: None (si la herramienta falla, solo avisa)."""
    try:
        sys.path.insert(0, str(RAIZ / "tools"))
        import aplicar_encabezados  # noqa: PLC0415

        aplicar_encabezados.procesar(path, check=False)
    except Exception as exc:  # noqa: BLE001 - la evidencia ya está escrita
        print(f"  (aviso: no se pudo poner el encabezado a {path.name}: {exc})")


def _suf(etiqueta: str) -> str:
    """Objetivo: sufijo de archivo según la etiqueta. Entradas: etiqueta (str). Salida: str ('-mac', '')."""
    return f"-{etiqueta}" if etiqueta else ""


def guardar_catalogo(etiqueta: str = "") -> None:
    """Objetivo: guardar el catálogo de agentes del coordinador como evidencia.
    Entradas: etiqueta (str) sufijo por equipo. Salida: None (escribe 04-catalogo[-etiqueta].txt)."""
    EV.mkdir(exist_ok=True)
    texto = texto_catalogo(construir_catalogo())
    nombre = f"04-catalogo{_suf(etiqueta)}.txt"
    (EV / nombre).write_text(texto + "\n", encoding="utf-8")
    _con_encabezado(EV / nombre)
    print(f"✓ evidencias/{nombre}")
    print(texto)


def guardar_ronda(preguntas: list[str], etiqueta: str = "") -> None:
    """Objetivo: correr una ronda de preguntas por el coordinador y guardar la evidencia.
    Entradas: preguntas (list[str]), etiqueta (str). Salida: None (escribe 05-ronda[-etiqueta].md)."""
    try:
        from langchain_core.messages import HumanMessage  # noqa: PLC0415

        from src.coordinador.graph import graph  # import tardío: construye Gemini (requiere key)
    except Exception as exc:  # noqa: BLE001
        print(f"· ronda omitida: {exc}\n  (requiere GOOGLE_API_KEY y `langgraph dev` arriba)")
        return

    import platform
    import uuid
    from datetime import datetime, timezone

    quien = etiqueta or platform.node()
    lineas = [f"# Ronda de preguntas · evidencia ({quien})\n",
              f"_Generada el {datetime.now(timezone.utc).isoformat(timespec='seconds')} desde `{platform.node()}`._\n"]
    for p in preguntas:
        # Hilo nuevo por pregunta: cada enrutamiento es independiente (ruta/estado limpios).
        hilo = {"configurable": {"thread_id": f"evidencia-{uuid.uuid4().hex[:8]}"}}
        r = graph.invoke({"messages": [HumanMessage(content=p)]}, hilo)
        ruta = " → ".join(r.get("ruta", []))
        lineas.append(f"**> {p}**\n\n- ruta: {ruta}\n- {r.get('respuesta', '')}\n")
        print(f"  > {p}\n    {ruta} :: {r.get('respuesta', '')[:80]}")
    EV.mkdir(exist_ok=True)
    nombre = f"05-ronda{_suf(etiqueta)}.md"
    (EV / nombre).write_text("\n".join(lineas), encoding="utf-8")
    _con_encabezado(EV / nombre)
    print(f"✓ evidencias/{nombre}")


def main() -> None:
    """Objetivo: CLI de evidencias. Entradas: --preguntas, --etiqueta. Salida: None (escribe en evidencias/)."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--preguntas", nargs="*", default=None)
    ap.add_argument("--etiqueta", default="", help="Sufijo para las evidencias (p. ej. mac / windows).")
    args = ap.parse_args()
    guardar_catalogo(args.etiqueta)
    guardar_ronda(args.preguntas or PREGUNTAS_DEF, args.etiqueta)


if __name__ == "__main__":
    main()
