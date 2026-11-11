# --8<-- encabezado-grupo
# Archivo: tools/cargar_rag_reiki.py
# Objetivo: Carga los documentos de Reiki (`data/reiki/`) al RAG en Redis.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2009
# Última modificación: 20261111 0730
# --8<-- fin-encabezado-grupo

"""Carga los documentos de Reiki (`data/reiki/`) al RAG en Redis.

Requiere Redis accesible (local dockerizado o remoto por REDIS_URL) y GOOGLE_API_KEY.

Uso:
    docker compose up -d                 # levanta el Redis local
    uv run python tools/cargar_rag_reiki.py
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))  # permite `python tools/…` con imports `src.*`

from src.agente_tomas import rag  # noqa: E402


def main() -> int:
    """Objetivo: cargar los documentos de Reiki (data/reiki) al RAG en Redis.
    Entradas: ninguna (usa REDIS_URL del entorno). Salida: int — 0 si indexó, 1 si falló."""
    if not rag.disponible():
        print(f"✗ Redis no responde en {rag.REDIS_URL}. Levántalo con: docker compose up -d")
        return 1
    print(f"Cargando {rag.CARPETA_DOCS} → índice '{rag.REDIS_INDEX}' en {rag.REDIS_URL} …")
    try:
        n = rag.cargar()
    except Exception as exc:  # noqa: BLE001
        print(f"✗ {exc}")
        return 1
    print(f"✓ {n} fragmentos indexados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
