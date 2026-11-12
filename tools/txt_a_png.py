# --8<-- encabezado-grupo
# Archivo: tools/txt_a_png.py
# Objetivo: Renderiza un archivo de texto/markdown a un PNG estilo terminal (para evidencias).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261112 1120
# Última modificación: 20261112 1120
# --8<-- fin-encabezado-grupo

"""Renderiza un archivo de texto/markdown a un PNG estilo terminal.

Sirve para dejar evidencias que la rúbrica pide como imagen (p. ej. `04-catalogo.png`,
`05-ronda.png`) a partir del contenido de texto que ya tenemos, sin re-correr nada.
Quita el encabezado de grupo del archivo y dibuja el resto en una tarjeta oscura con
fuente monoespaciada.

Uso:
    uv run --with pillow python tools/txt_a_png.py <entrada.txt|.md> <salida.png> ["Título"]
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont  # type: ignore

FUENTES = ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Monaco.ttf",
           "/Library/Fonts/Menlo.ttc"]
COLS = 96            # ancho en caracteres antes de envolver
SIZE = 15
PAD = 22
BG = (30, 31, 35)    # fondo terminal
FG = (223, 225, 230) # texto
TIT = (120, 200, 140)  # título verde


def _sin_encabezado(texto: str) -> list[str]:
    """Quita el bloque encabezado-grupo (estilos `# --8<--` y `<!-- -->`) y devuelve líneas."""
    out, saltando = [], False
    for ln in texto.splitlines():
        s = ln.strip()
        if s.startswith("<!--encabezado-grupo-->") or s.startswith("# --8<-- encabezado-grupo"):
            saltando = True
            continue
        if s.startswith("<!--/encabezado-grupo-->") or s.startswith("# --8<-- fin-encabezado-grupo"):
            saltando = False
            continue
        if saltando:
            continue
        out.append(ln.replace("\t", "    "))
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def _fuente(size: int) -> ImageFont.FreeTypeFont:
    for f in FUENTES:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:  # noqa: BLE001
                pass
    return ImageFont.load_default()


def render(entrada: str, salida: str, titulo: str | None = None) -> None:
    """Objetivo: dibujar `entrada` como PNG estilo terminal en `salida`. Salida: None."""
    lineas = _sin_encabezado(Path(entrada).read_text(encoding="utf-8"))
    envueltas: list[str] = []
    for ln in lineas:
        if len(ln) <= COLS:
            envueltas.append(ln)
        else:
            sub = ln[: len(ln) - len(ln.lstrip())]  # conservar la sangría
            for i, w in enumerate(textwrap.wrap(ln, COLS) or [""]):
                envueltas.append((sub + w) if i else w)

    font = _fuente(SIZE)
    fuente_tit = _fuente(SIZE + 3)
    asc, desc = font.getmetrics()
    lh = asc + desc + 5
    cw = font.getlength("M") or SIZE * 0.6
    tit_h = (lh + 16) if titulo else 0

    ancho = int(PAD * 2 + cw * COLS)
    alto = int(PAD * 2 + tit_h + lh * len(envueltas))
    img = Image.new("RGB", (ancho, alto), BG)
    d = ImageDraw.Draw(img)

    y = PAD
    if titulo:
        d.text((PAD, y), titulo, font=fuente_tit, fill=TIT)
        y += lh + 16
        d.line([(PAD, y - 8), (ancho - PAD, y - 8)], fill=(70, 72, 80), width=1)
    for ln in envueltas:
        d.text((PAD, y), ln, font=font, fill=FG)
        y += lh

    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    img.save(salida)
    print(f"✓ {salida}  ({ancho}x{alto})")


def main() -> None:
    """CLI: entrada, salida, [título]."""
    if len(sys.argv) < 3:
        print("uso: txt_a_png.py <entrada> <salida.png> [\"Título\"]")
        raise SystemExit(2)
    titulo = sys.argv[3] if len(sys.argv) > 3 else None
    render(sys.argv[1], sys.argv[2], titulo)


if __name__ == "__main__":
    main()
