# --8<-- encabezado-grupo
# Archivo: tools/aplicar_encabezados.py
# Objetivo: Inserta/actualiza el encabezado de grupo en los archivos del repo (idempotente).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1746
# Última modificación: 20261110 2001
# --8<-- fin-encabezado-grupo

"""Inserta/actualiza el encabezado de grupo en los archivos del repo (idempotente).

Si el archivo ya tiene el encabezado (al inicio), conserva la fecha de Creación y
solo refresca la de Última modificación. Ver CONVENCIONES.md para el formato.

La detección y el borrado están anclados al INICIO del archivo (tras un posible
shebang): así el script puede procesarse a sí mismo y a CONVENCIONES.md aunque su
cuerpo mencione los centinelas como texto.

Uso:
    python tools/aplicar_encabezados.py           # aplica/actualiza
    python tools/aplicar_encabezados.py --check    # sale !=0 si falta en algún archivo
"""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

GRUPO = "Fabio Durán - Gustavo Reyes - Ezequiel Muñoz"
AHORA = datetime.now().strftime("%Y%m%d %H%M")
RAIZ = Path(__file__).resolve().parent.parent

HASH_EXT = {".py", ".toml", ".txt", ".sh", ".ps1", ".cfg", ".ini"}
MARKUP_EXT = {".md", ".html", ".htm"}
HASH_FILES = {".gitignore", ".env.example", ".dockerignore"}

EXCLUIR_EXT = {".json", ".lock", ".bru", ".woff2", ".png", ".jpg", ".svg", ".ipynb"}
EXCLUIR_NOMBRE = {"uv.lock", ".python-version"}
EXCLUIR_DIR = {".git", ".venv", "__pycache__", ".langgraph_api", ".ipynb_checkpoints"}

# Centinelas. En almohadilla (.py, etc.) el encabezado es texto visible.
_TAG = "--8<-- encabezado-grupo"
_TAG_FIN = "--8<-- fin-encabezado-grupo"
INI_HASH, FIN_HASH = f"# {_TAG}", f"# {_TAG_FIN}"
# En markup (.md/.html) el encabezado es un blockquote VISIBLE al renderizar,
# entre centinelas HTML invisibles. (El formato viejo era un comentario HTML oculto.)
INI_MK, FIN_MK = "<!--encabezado-grupo-->", "<!--/encabezado-grupo-->"
INI_MK_VIEJO, FIN_MK_VIEJO = "<!-- --8<-- encabezado-grupo", "--8<-- fin-encabezado-grupo -->"


def _git_creacion(rel: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(RAIZ), "log", "--diff-filter=A", "--follow",
             "--format=%ad", "--date=format:%Y%m%d %H%M", "-1", "--", rel],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return out or None
    except subprocess.CalledProcessError:
        return None


def _objetivo(path: Path, ext: str, cuerpo: str) -> str:
    if ext == ".py":
        m = re.search(r'"""(.+?)(?:\n|""")', cuerpo, re.S)
        if m:
            return m.group(1).strip()
    if ext in MARKUP_EXT:
        for linea in cuerpo.splitlines():
            s = linea.strip()
            if s.startswith("#"):
                return s.lstrip("# ").strip()
            if s.startswith("<title>"):
                return re.sub(r"</?title>", "", s).strip()
    genericos = {
        ".gitignore": "Archivos y carpetas ignorados por git.",
        ".env.example": "Plantilla de variables de entorno (sin secretos).",
        "pyproject.toml": "Configuración del proyecto y dependencias (uv).",
        "requirements.txt": "Dependencias del proyecto (pip).",
    }
    return genericos.get(path.name, f"{path.name} del proyecto.")


def _construir(rel: str, objetivo: str, creacion: str, markup: bool) -> str:
    if markup:
        # Blockquote visible al renderizar, entre centinelas HTML.
        return "\n".join([
            INI_MK,
            f"> **Archivo:** `{rel}`  ",
            f"> **Objetivo:** {objetivo}  ",
            f"> **Grupo del curso:** {GRUPO}  ",
            f"> **Creación:** {creacion} · **Última modificación:** {AHORA}",
            FIN_MK,
        ])
    campos = [
        f"Archivo: {rel}",
        f"Objetivo: {objetivo}",
        f"Grupo del curso: {GRUPO}",
        f"Creación: {creacion}",
        f"Última modificación: {AHORA}",
    ]
    return "\n".join([INI_HASH, *[f"# {c}" for c in campos], FIN_HASH])


def _split_shebang(texto: str) -> tuple[str, str]:
    if texto.startswith("#!"):
        nl = texto.find("\n")
        if nl != -1:
            return texto[: nl + 1], texto[nl + 1:]
    return "", texto


def _tiene_encabezado_inicio(cuerpo: str, markup: bool) -> bool:
    c = cuerpo.lstrip("\n")
    if markup:
        return c.startswith(INI_MK) or c.startswith(INI_MK_VIEJO)
    return c.startswith(INI_HASH)


def _quitar_encabezado_inicio(cuerpo: str, markup: bool) -> str:
    c = cuerpo.lstrip("\n")
    if markup:
        # Quita el encabezado al inicio, en formato nuevo (visible) o viejo (comentario).
        for ini, fin in ((INI_MK, FIN_MK), (INI_MK_VIEJO, FIN_MK_VIEJO)):
            if c.startswith(ini):
                idx = c.find(fin)
                if idx != -1:
                    return c[idx + len(fin):].lstrip("\n")
        return cuerpo
    if not c.startswith(INI_HASH):
        return cuerpo
    idx = c.find(FIN_HASH)
    if idx == -1:
        return cuerpo
    return c[idx + len(FIN_HASH):].lstrip("\n")


def _creacion_previa(texto: str) -> str | None:
    m = re.search(r"Creaci[oó]n:\s*\**\s*(\d{8} \d{4})", texto)
    return m.group(1) if m else None


def _header_hash_lines(rel: str, objetivo: str, creacion: str) -> list[str]:
    campos = [
        f"Archivo: {rel}",
        f"Objetivo: {objetivo}",
        f"Grupo del curso: {GRUPO}",
        f"Creación: {creacion}",
        f"Última modificación: {AHORA}",
    ]
    return [INI_HASH, *[f"# {c}" for c in campos], FIN_HASH]


def _frontmatter(cuerpo: str) -> tuple[list[str], str] | None:
    """Si el cuerpo empieza con frontmatter YAML (--- … ---), devuelve (líneas internas, resto)."""
    c = cuerpo.lstrip("\n")
    lines = c.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], "\n".join(lines[i + 1:])
    return None


def _strip_header_inner(inner: list[str]) -> list[str]:
    out, skip = [], False
    for ln in inner:
        if ln.strip() == INI_HASH:
            skip = True
            continue
        if skip and ln.strip() == FIN_HASH:
            skip = False
            continue
        if not skip:
            out.append(ln)
    return out


def _tiene_encabezado(cuerpo: str, markup: bool) -> bool:
    if _tiene_encabezado_inicio(cuerpo, markup):
        return True
    fm = _frontmatter(cuerpo)
    return fm is not None and any(ln.strip() == INI_HASH for ln in fm[0])


def procesar(path: Path, check: bool) -> bool:
    rel = str(path.relative_to(RAIZ))
    ext = path.suffix.lower()
    markup = ext in MARKUP_EXT
    texto = path.read_text(encoding="utf-8")
    shebang, cuerpo = _split_shebang(texto)

    if check:
        return _tiene_encabezado(cuerpo, markup)

    creacion = _creacion_previa(texto) or _git_creacion(rel) or AHORA
    # Quitar cualquier encabezado previo al inicio (esquema viejo: HTML o hash).
    cuerpo = _quitar_encabezado_inicio(_quitar_encabezado_inicio(cuerpo, True), False)

    fm = _frontmatter(cuerpo)
    if fm is not None:
        # Archivos con frontmatter YAML (p. ej. agentes OpenCode): el encabezado va
        # DENTRO del frontmatter como comentarios `#`, para no romper el `---` inicial.
        inner, resto = fm
        inner = _strip_header_inner(inner)
        desc = next((ln.split(":", 1)[1].strip() for ln in inner if ln.strip().startswith("description:")), None)
        objetivo = desc or _objetivo(path, ext, resto)
        nuevo = "\n".join(["---", *_header_hash_lines(rel, objetivo, creacion), *inner, "---"]) + "\n" + resto
        path.write_text(shebang + nuevo, encoding="utf-8")
        return True

    objetivo = _objetivo(path, ext, cuerpo)
    encabezado = _construir(rel, objetivo, creacion, markup)
    path.write_text(shebang + encabezado + "\n\n" + cuerpo, encoding="utf-8")
    return True


def _notebooks(check: bool) -> list[str]:
    import nbformat

    faltan = []
    for path in RAIZ.rglob("*.ipynb"):
        if any(d in path.parts for d in EXCLUIR_DIR):
            continue
        rel = str(path.relative_to(RAIZ))
        nb = nbformat.read(str(path), 4)
        celdas = nb.cells
        tiene = bool(celdas) and celdas[0].cell_type == "markdown" and (
            celdas[0].source.startswith(INI_MK) or celdas[0].source.startswith(INI_MK_VIEJO)
        )
        if check:
            if not tiene:
                faltan.append(rel)
            continue
        creacion = (_creacion_previa(celdas[0].source) if tiene else None) or _git_creacion(rel) or AHORA
        celda = nbformat.v4.new_markdown_cell(_construir(rel, f"Notebook: {path.stem}", creacion, markup=True))
        if tiene:
            celdas[0] = celda
        else:
            celdas.insert(0, celda)
        nbformat.write(nb, str(path))
    return faltan


def iter_archivos():
    for path in sorted(RAIZ.rglob("*")):
        if not path.is_file() or any(d in path.parts for d in EXCLUIR_DIR):
            continue
        if path.name in EXCLUIR_NOMBRE or path.suffix.lower() in EXCLUIR_EXT:
            continue
        if path.suffix.lower() in HASH_EXT or path.suffix.lower() in MARKUP_EXT or path.name in HASH_FILES:
            yield path


def main() -> int:
    check = "--check" in sys.argv[1:]
    faltan, n = [], 0
    for path in iter_archivos():
        ok = procesar(path, check)
        n += 1
        if check and not ok:
            faltan.append(str(path.relative_to(RAIZ)))
    faltan += _notebooks(check)

    if check:
        if faltan:
            print("Sin encabezado:", *faltan, sep="\n  ")
            return 1
        print(f"OK · {n} archivos con encabezado.")
        return 0
    print(f"Encabezado aplicado/actualizado en {n} archivos (+ notebooks). Modificación: {AHORA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
