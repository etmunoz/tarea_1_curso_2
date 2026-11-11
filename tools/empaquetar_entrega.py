# --8<-- encabezado-grupo
# Archivo: tools/empaquetar_entrega.py
# Objetivo: Arma el zip de entrega del grupo con la estructura del Paso 9 del taller.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1941
# Última modificación: 20261111 1429
# --8<-- fin-encabezado-grupo

"""Arma el zip de entrega del grupo con la estructura del Paso 9 del taller.

Todo cuelga de UNA carpeta raíz con el nombre de la repo (`tarea_1_curso_2/`), de
modo que al deszipear quede ordenado en una sola carpeta:

    grupo-<N>-tarea_1_curso_2.zip
    └── tarea_1_curso_2/
        ├── LEEME.txt               qué hacer tras deszipear
        ├── documento-entrega.pdf   (o .md si no se exportó el PDF)
        ├── blueprint-ezequiel.md
        ├── companeros.md
        ├── evidencias/             fichas (JSON), catálogos y rondas (Mac y Windows)
        └── proyecto/               el proyecto COMPLETO (todo lo versionado en git)

Además deja esa misma estructura (sin `proyecto/`, que es la repo entera) como una
carpeta versionada dentro de la repo: `entrega/tarea_1_curso_2/`. Así se ve la
entrega sin tener que armar el zip. Esa carpeta la REGENERA este script: vuelve a
correrlo antes de entregar.

`proyecto/` se arma con `git ls-files`: entra todo lo versionado y NUNCA `.env` ni
`.venv` (están en .gitignore). El script avisa de pendientes pero no bloquea.

Uso:  python tools/empaquetar_entrega.py --grupo 1
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ.name  # nombre de la repo = carpeta raíz de la entrega (tarea_1_curso_2)

# Evidencias que deberían estar (las dos .png son capturas manuales).
EVIDENCIAS_REQUERIDAS = [
    "01-saltos.png",
    "02-ficha-agente_ezequiel.json",
    "03-tunel.png",
    "04-catalogo-mac.txt",
    "05-ronda-mac.md",
]


def _git_ls_files() -> list[str]:
    """Objetivo: listar los archivos versionados (así el zip nunca incluye .env/.venv).
    Entradas: ninguna. Salida: list[str] — rutas relativas."""
    out = subprocess.run(["git", "-C", str(RAIZ), "ls-files"], capture_output=True, text=True, check=True)
    return [l for l in out.stdout.splitlines() if l.strip()]


def construir_carpeta_entrega() -> tuple[Path, list[str]]:
    """Objetivo: materializar `entrega/<repo>/` con los entregables (sin el código).
    Copia LEEME, documento (PDF o MD), blueprint, companeros y evidencias/.
    Entradas: ninguna. Salida: (Path de la carpeta, avisos list[str])."""
    base = RAIZ / "entrega" / CARPETA
    if base.exists():
        shutil.rmtree(base)
    (base / "evidencias").mkdir(parents=True)
    avisos: list[str] = []

    # LEEME.txt (qué hacer al deszipear)
    leeme = RAIZ / "entrega" / "LEEME.txt"
    if leeme.exists():
        shutil.copy2(leeme, base / "LEEME.txt")
    else:
        avisos.append("falta entrega/LEEME.txt")

    # Documento: PDF si existe, si no el .md (y avisa)
    pdf = RAIZ / "entrega" / "documento-entrega.pdf"
    md = RAIZ / "entrega" / "documento-entrega.md"
    if pdf.exists():
        shutil.copy2(pdf, base / "documento-entrega.pdf")
    elif md.exists():
        shutil.copy2(md, base / "documento-entrega.md")
        avisos.append("no hay documento-entrega.pdf; se incluyó el .md (exportar a PDF antes de entregar)")
        if "⟨" in md.read_text(encoding="utf-8"):
            avisos.append("el documento tiene campos ⟨pendiente⟩ sin completar")
    else:
        avisos.append("falta entrega/documento-entrega.(md|pdf)")

    # Blueprints (todos los blueprint-*.md del repo) y companeros
    blueprints = sorted(RAIZ.glob("blueprint-*.md"))
    if not blueprints:
        avisos.append("no hay ningún blueprint-*.md")
    for src in blueprints:
        shutil.copy2(src, base / src.name)
    companeros = RAIZ / "entrega" / "companeros.md"
    if companeros.exists():
        shutil.copy2(companeros, base / "companeros.md")
    else:
        avisos.append("falta entrega/companeros.md")

    # Evidencias (todo lo que haya en evidencias/, menos su README)
    ev_dir = RAIZ / "evidencias"
    for p in sorted(ev_dir.glob("*")):
        if p.is_file():
            shutil.copy2(p, base / "evidencias" / p.name)
    faltan = [e for e in EVIDENCIAS_REQUERIDAS if not (ev_dir / e).exists()]
    if faltan:
        avisos.append("evidencias faltantes: " + ", ".join(faltan))

    return base, avisos


def empaquetar(grupo: str) -> Path:
    """Objetivo: armar el zip de entrega (carpeta raíz = nombre de la repo) y la
    carpeta `entrega/<repo>/` versionada. Entradas: grupo (str). Salida: Path del .zip."""
    base, avisos = construir_carpeta_entrega()

    dist = RAIZ / "dist"
    dist.mkdir(exist_ok=True)
    destino = dist / f"grupo-{grupo}-{CARPETA}.zip"
    tracked = _git_ls_files()

    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        # 1) la carpeta de entrega materializada -> tarea_1_curso_2/<...>
        for p in sorted(base.rglob("*")):
            if p.is_file():
                z.write(p, f"{CARPETA}/{p.relative_to(base).as_posix()}")

        # 2) proyecto/ = todo lo versionado, bajo tarea_1_curso_2/proyecto/
        #    (se excluye dist/ y la propia carpeta de entrega para no duplicarla)
        prefijo_entrega = f"entrega/{CARPETA}/"
        n_proyecto = 0
        for rel in tracked:
            if rel.startswith("dist/") or rel.startswith(prefijo_entrega):
                continue
            z.write(RAIZ / rel, f"{CARPETA}/proyecto/{rel}")
            n_proyecto += 1

    print(f"✓ Carpeta de entrega: {base.relative_to(RAIZ)}/ (versionada en la repo)")
    print(f"✓ Zip creado: {destino.relative_to(RAIZ)}  ({destino.stat().st_size} bytes)")
    print(f"  raíz del zip: {CARPETA}/ · proyecto/: {n_proyecto} archivos versionados")
    if avisos:
        print("Avisos (completar antes de entregar):")
        for a in avisos:
            print("  - " + a)
    return destino


def main() -> None:
    """Objetivo: CLI del empaquetador. Entradas: --grupo. Salida: None (crea dist/grupo-N-….zip)."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--grupo", default="N", help="Número del grupo (p. ej. 1).")
    empaquetar(ap.parse_args().grupo)


if __name__ == "__main__":
    main()
