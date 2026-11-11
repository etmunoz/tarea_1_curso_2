# --8<-- encabezado-grupo
# Archivo: tools/exportar_pdf.py
# Objetivo: Exporta entrega/documento-entrega.md a entrega/documento-entrega.pdf.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2334
# Última modificación: 20261111 1429
# --8<-- fin-encabezado-grupo

"""Exporta entrega/documento-entrega.md a entrega/documento-entrega.pdf.

Reproducible y sin dependencias de sistema: markdown -> HTML -> PDF con xhtml2pdf
(reportlab, todo Python puro). Las dependencias van embebidas (PEP 723), así que
corre con `uv run` sin tocar el pyproject:

    uv run tools/exportar_pdf.py

Helvetica no tiene algunos glifos (→ ↔ ⟨ ⟩); se sustituyen a ASCII solo en el PDF.
"""
# /// script
# dependencies = ["markdown>=3.5", "xhtml2pdf>=0.2.11"]
# ///
from __future__ import annotations

import pathlib

import markdown
from xhtml2pdf import pisa

RAIZ = pathlib.Path(__file__).resolve().parent.parent
MD = RAIZ / "entrega" / "documento-entrega.md"
PDF = RAIZ / "entrega" / "documento-entrega.pdf"

# Glifos que Helvetica no dibuja -> equivalente ASCII (solo para el PDF).
SUSTITUCIONES = {"→": " -> ", "↔": " <-> ", "⟨": "<", "⟩": ">", "…": "..."}

CSS = """
body { font-family: Helvetica; font-size: 11px; color: #222; }
h1 { font-size: 19px; } h2 { font-size: 13px; color: #1a1a1a; }
table { border: 1px solid #999; } td, th { border: 1px solid #999; padding: 4px; font-size: 10px; }
code, pre { font-family: Courier; background: #f4f4f4; }
blockquote { color: #555; border-left: 3px solid #ccc; padding-left: 8px; }
"""


def exportar() -> pathlib.Path:
    """Objetivo: convertir el documento de entrega .md a .pdf.
    Entradas: ninguna (lee entrega/documento-entrega.md). Salida: Path del PDF creado."""
    texto = MD.read_text(encoding="utf-8")
    for a, b in SUSTITUCIONES.items():
        texto = texto.replace(a, b)
    cuerpo = markdown.markdown(texto, extensions=["tables", "fenced_code"])
    html = f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{cuerpo}</body></html>'
    with open(PDF, "wb") as f:
        estado = pisa.CreatePDF(html, dest=f)
    if estado.err:
        raise SystemExit(f"✗ xhtml2pdf devolvió {estado.err} errores")
    print(f"✓ PDF creado: {PDF.relative_to(RAIZ)}  ({PDF.stat().st_size} bytes)")
    return PDF


if __name__ == "__main__":
    exportar()
