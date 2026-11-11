# --8<-- encabezado-grupo
# Archivo: tools/empaquetar_entrega.py
# Objetivo: Arma el zip de entrega del grupo con la estructura del Paso 9 del taller.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1941
# Última modificación: 20261110 2113
# --8<-- fin-encabezado-grupo

"""Arma el zip de entrega del grupo con la estructura del Paso 9 del taller.

Estructura del zip (ver taller-a2a/09-entrega-y-evaluacion.md):

    grupo-<N>-taller-a2a.zip
    ├── documento-entrega.pdf   (o .md si no se exportó el PDF)
    ├── blueprint-ezequiel.md
    ├── companeros.md
    ├── proyecto/               el proyecto COMPLETO (todo lo versionado en git)
    └── evidencias/             capturas y ficha

`proyecto/` se arma con `git ls-files`: así entra todo lo versionado y NUNCA `.env`
ni `.venv` (están en .gitignore). El script avisa de evidencias faltantes y de
campos ⟨pendiente⟩ en el documento, pero no bloquea.

Uso:  python tools/empaquetar_entrega.py --grupo 1
"""
from __future__ import annotations

import argparse
import subprocess
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _git_ls_files() -> list[str]:
    out = subprocess.run(["git", "-C", str(RAIZ), "ls-files"], capture_output=True, text=True, check=True)
    return [l for l in out.stdout.splitlines() if l.strip()]


def empaquetar(grupo: str) -> Path:
    dist = RAIZ / "dist"
    dist.mkdir(exist_ok=True)
    destino = dist / f"grupo-{grupo}-taller-a2a.zip"

    tracked = _git_ls_files()
    avisos: list[str] = []

    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        # 1) proyecto/ = todo lo versionado (sin secretos; .env/.venv no están en git)
        for rel in tracked:
            if rel.startswith("dist/"):
                continue
            z.write(RAIZ / rel, f"proyecto/{rel}")

        # 2) documento de entrega en la raíz del zip (PDF si existe, si no el .md)
        pdf = RAIZ / "entrega" / "documento-entrega.pdf"
        md = RAIZ / "entrega" / "documento-entrega.md"
        if pdf.exists():
            z.write(pdf, "documento-entrega.pdf")
        elif md.exists():
            z.write(md, "documento-entrega.md")
            avisos.append("no hay documento-entrega.pdf; se incluyó el .md (exportar a PDF antes de entregar)")
            if "⟨pendiente⟩" in md.read_text(encoding="utf-8") or "⟨" in md.read_text(encoding="utf-8"):
                avisos.append("el documento tiene campos ⟨pendiente⟩ sin completar")
        else:
            avisos.append("falta entrega/documento-entrega.(md|pdf)")

        # 3) blueprint(s) y companeros.md en la raíz
        for src, arc in [
            (RAIZ / "blueprint-ezequiel.md", "blueprint-ezequiel.md"),
            (RAIZ / "entrega" / "companeros.md", "companeros.md"),
        ]:
            if src.exists():
                z.write(src, arc)
            else:
                avisos.append(f"falta {src.relative_to(RAIZ)}")

        # 4) evidencias/ en la raíz
        ev_dir = RAIZ / "evidencias"
        requeridas = ["01-saltos.png", "02-ficha.json", "03-tunel.png", "04-catalogo.png", "05-ronda.png"]
        for p in sorted(ev_dir.glob("*")):
            if p.is_file():
                z.write(p, f"evidencias/{p.name}")
        faltan_ev = [e for e in requeridas if not (ev_dir / e).exists()]
        if faltan_ev:
            avisos.append("evidencias faltantes: " + ", ".join(faltan_ev))

    print(f"✓ Zip creado: {destino.relative_to(RAIZ)}  ({destino.stat().st_size} bytes)")
    print(f"  proyecto/: {len(tracked)} archivos versionados")
    if avisos:
        print("Avisos (completar antes de entregar):")
        for a in avisos:
            print("  - " + a)
    return destino


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--grupo", default="N", help="Número del grupo (p. ej. 1).")
    empaquetar(ap.parse_args().grupo)


if __name__ == "__main__":
    main()
