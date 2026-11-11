# --8<-- encabezado-grupo
# Archivo: tools/aplicar_encabezados.py
# Objetivo: Inserta/actualiza el encabezado de grupo en los archivos del repo (idempotente).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1746
# Última modificación: 20261111 1413
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
EXCLUIR_DIR = {".git", ".venv", "__pycache__", ".langgraph_api", ".ipynb_checkpoints", ".pytest_cache"}

# Centinelas. En almohadilla (.py, etc.) el encabezado es texto visible.
_TAG = "--8<-- encabezado-grupo"
_TAG_FIN = "--8<-- fin-encabezado-grupo"
INI_HASH, FIN_HASH = f"# {_TAG}", f"# {_TAG_FIN}"
# En markup (.md/.html) el encabezado es un blockquote VISIBLE al renderizar,
# entre centinelas HTML invisibles. (El formato viejo era un comentario HTML oculto.)
INI_MK, FIN_MK = "<!--encabezado-grupo-->", "<!--/encabezado-grupo-->"
INI_MK_VIEJO, FIN_MK_VIEJO = "<!-- --8<-- encabezado-grupo", "--8<-- fin-encabezado-grupo -->"


def _git_creacion(rel: str) -> str | None:
    """Objetivo: fecha de alta del archivo en git (yyyymmdd HHMM).
    Entradas: rel (str) ruta relativa. Salida: str | None si no está versionado."""
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
    """Objetivo: deducir el "Objetivo" del encabezado (1ª línea del docstring/H1, o genérico).
    Entradas: path (Path), ext (str), cuerpo (str) sin encabezado. Salida: str."""
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
    """Objetivo: construir el bloque de encabezado (markup=blockquote visible, o hash con #).
    Entradas: rel (str), objetivo (str), creacion (str), markup (bool). Salida: str — el encabezado."""
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
    """Objetivo: separar un posible shebang del resto del archivo.
    Entradas: texto (str). Salida: (shebang, resto) — shebang '' si no hay."""
    if texto.startswith("#!"):
        nl = texto.find("\n")
        if nl != -1:
            return texto[: nl + 1], texto[nl + 1:]
    return "", texto


def _tiene_encabezado_inicio(cuerpo: str, markup: bool) -> bool:
    """Objetivo: decir si el cuerpo empieza con el encabezado (formato nuevo o viejo).
    Entradas: cuerpo (str), markup (bool). Salida: bool."""
    c = cuerpo.lstrip("\n")
    if markup:
        return c.startswith(INI_MK) or c.startswith(INI_MK_VIEJO)
    return c.startswith(INI_HASH)


def _quitar_encabezado_inicio(cuerpo: str, markup: bool) -> str:
    """Objetivo: quitar el encabezado del inicio del cuerpo (formato nuevo o viejo).
    Entradas: cuerpo (str), markup (bool). Salida: str — cuerpo sin encabezado."""
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
    """Objetivo: recuperar la fecha de Creación ya presente en un encabezado.
    Entradas: texto (str). Salida: str (yyyymmdd HHMM) | None."""
    m = re.search(r"Creaci[oó]n:\s*\**\s*(\d{8} \d{4})", texto)
    return m.group(1) if m else None


def _header_hash_lines(rel: str, objetivo: str, creacion: str) -> list[str]:
    """Objetivo: construir las líneas `#` del encabezado (para archivos con frontmatter YAML).
    Entradas: rel, objetivo, creacion (str). Salida: list[str] — líneas del encabezado."""
    campos = [
        f"Archivo: {rel}",
        f"Objetivo: {objetivo}",
        f"Grupo del curso: {GRUPO}",
        f"Creación: {creacion}",
        f"Última modificación: {AHORA}",
    ]
    return [INI_HASH, *[f"# {c}" for c in campos], FIN_HASH]


def _frontmatter(cuerpo: str) -> tuple[list[str], str] | None:
    """Objetivo: detectar frontmatter YAML al inicio (--- … ---).
    Entradas: cuerpo (str). Salida: (líneas internas, resto) | None si no hay frontmatter."""
    c = cuerpo.lstrip("\n")
    lines = c.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], "\n".join(lines[i + 1:])
    return None


def _strip_header_inner(inner: list[str]) -> list[str]:
    """Objetivo: quitar el encabezado `#` de dentro de un frontmatter YAML.
    Entradas: inner (list[str]) líneas del frontmatter. Salida: list[str] sin el encabezado."""
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
    """Objetivo: decir si hay encabezado al inicio o dentro del frontmatter.
    Entradas: cuerpo (str), markup (bool). Salida: bool."""
    if _tiene_encabezado_inicio(cuerpo, markup):
        return True
    fm = _frontmatter(cuerpo)
    return fm is not None and any(ln.strip() == INI_HASH for ln in fm[0])


def procesar(path: Path, check: bool) -> bool:
    """Objetivo: insertar/actualizar el encabezado de un archivo (o verificarlo con check).
    Entradas: path (Path), check (bool) solo verifica si True.
    Salida: bool — en check, True si tiene encabezado; al aplicar, True."""
    rel = path.relative_to(RAIZ).as_posix()
    ext = path.suffix.lower()
    markup = ext in MARKUP_EXT
    texto = path.read_text(encoding="utf-8")
    # BOM: los .ps1 lo necesitan para que Windows PowerShell 5.1 lea bien las tildes.
    # Se quita para analizar y se repone al escribir (siempre en .ps1).
    bom = "\ufeff" if (texto.startswith("\ufeff") or ext == ".ps1") else ""
    texto = texto.removeprefix("\ufeff")
    shebang, cuerpo = _split_shebang(texto)
    shebang = bom + shebang

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
    """Objetivo: poner/actualizar el encabezado como 1ª celda Markdown en cada .ipynb.
    Entradas: check (bool). Salida: list[str] — notebooks sin encabezado (en modo check)."""
    import nbformat

    faltan = []
    for path in RAIZ.rglob("*.ipynb"):
        if any(d in path.parts for d in EXCLUIR_DIR):
            continue
        rel = path.relative_to(RAIZ).as_posix()
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
    """Objetivo: iterar los archivos del repo que admiten encabezado de almohadilla/markup.
    Entradas: ninguna. Salida: generador de Path."""
    for path in sorted(RAIZ.rglob("*")):
        if not path.is_file() or any(d in path.parts for d in EXCLUIR_DIR):
            continue
        if path.name in EXCLUIR_NOMBRE or path.suffix.lower() in EXCLUIR_EXT:
            continue
        if path.suffix.lower() in HASH_EXT or path.suffix.lower() in MARKUP_EXT or path.name in HASH_FILES:
            yield path


def main() -> int:
    """Objetivo: aplicar/actualizar (o verificar con --check) el encabezado en todo el repo.
    Entradas: argv (--check opcional). Salida: int — código de salida (0 ok)."""
    check = "--check" in sys.argv[1:]
    faltan, n = [], 0
    for path in iter_archivos():
        ok = procesar(path, check)
        n += 1
        if check and not ok:
            faltan.append(path.relative_to(RAIZ).as_posix())
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
