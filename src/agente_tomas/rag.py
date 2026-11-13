# --8<-- encabezado-grupo
# Archivo: src/agente_tomas/rag.py
# Objetivo: RAG del agente de Tomás · documentos de Reiki. Backend LOCAL (ultraliviano) o Redis.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2009
# Última modificación: 20261113 1100
# --8<-- fin-encabezado-grupo

"""RAG del agente de Tomás · documentos de Reiki.

Dos backends, seleccionables con `RAG_BACKEND`:

- **local** (por defecto): vector store **embebido y ultraliviano** `InMemoryVectorStore` de
  `langchain-core` (sin servidor, sin Docker), **persistido** a un archivo JSON
  (`logs/reiki_rag.json`). Ideal para máquinas chicas: los embeddings se calculan una vez con
  Gemini y quedan guardados.
- **redis**: `langchain-redis` sobre un Redis (dockerizado o remoto). Se mantiene para el profesor.

Los embeddings se calculan con Gemini (`GOOGLE_API_KEY`). Los imports pesados son tardíos: importar
este módulo no exige Redis, la clave ni el archivo.

Variables de entorno:
  RAG_BACKEND         'local' (def.) o 'redis'
  RAG_LOCAL_FILE      archivo del índice local (def. logs/reiki_rag.json)
  REDIS_URL           conexión a Redis (def. redis://localhost:6379)  [solo backend redis]
  REDIS_INDEX         nombre del índice vectorial (def. reiki)        [solo backend redis]
  MODELO_EMBEDDINGS   modelo de embeddings de Gemini (def. models/gemini-embedding-001)
  REIKI_DOCS          carpeta de documentos (def. data/reiki)
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

RAIZ = Path(__file__).resolve().parent.parent.parent
BACKEND = os.environ.get("RAG_BACKEND", "local").lower()
LOCAL_FILE = Path(os.environ.get("RAG_LOCAL_FILE", RAIZ / "logs" / "reiki_rag.json"))
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
REDIS_INDEX = os.environ.get("REDIS_INDEX", "reiki")
CARPETA_DOCS = Path(os.environ.get("REIKI_DOCS", RAIZ / "data" / "reiki"))


def _embeddings():
    """Objetivo: crear el modelo de embeddings de Gemini (import tardío; requiere GOOGLE_API_KEY)."""
    from langchain_google_genai import GoogleGenerativeAIEmbeddings  # import tardío (requiere key)

    return GoogleGenerativeAIEmbeddings(model=os.environ.get("MODELO_EMBEDDINGS", "models/gemini-embedding-001"))


# --- backend redis -----------------------------------------------------------------------------
def _vector_store_redis(from_existing: bool):
    from langchain_redis import RedisConfig, RedisVectorStore  # import tardío

    config = RedisConfig(index_name=REDIS_INDEX, redis_url=REDIS_URL, from_existing=from_existing)
    return RedisVectorStore(_embeddings(), config=config)


def _borrar_indice_redis() -> None:
    try:
        from redis import Redis

        from langchain_redis import RedisVectorStore  # noqa: F401 (asegura dependencia)

        cliente = Redis.from_url(REDIS_URL)
        try:
            cliente.ft(REDIS_INDEX).dropindex(delete_documents=True)
        except Exception:  # noqa: BLE001 - el índice puede no existir aún
            pass
    except Exception:  # noqa: BLE001
        pass


# --- utilidades de documentos ------------------------------------------------------------------
def _sin_encabezado(texto: str) -> str:
    """Quita el encabezado de grupo para no indexarlo como contenido del RAG."""
    import re

    return re.sub(r"<!--encabezado-grupo-->.*?<!--/encabezado-grupo-->\s*", "", texto, count=1, flags=re.S)


def _leer_documentos(carpeta: Path) -> list[tuple[str, str]]:
    """Devuelve [(texto, fuente)] de los .md/.txt/.pdf de la carpeta."""
    docs: list[tuple[str, str]] = []
    for p in sorted(carpeta.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() in {".md", ".txt"}:
            docs.append((_sin_encabezado(p.read_text(encoding="utf-8", errors="replace")), p.name))
        elif p.suffix.lower() == ".pdf":
            from pypdf import PdfReader  # import tardío

            texto = "\n".join((pg.extract_text() or "") for pg in PdfReader(str(p)).pages)
            if texto.strip():
                docs.append((texto, p.name))
    return docs


def _fragmentos(carpeta: Path):
    """Objetivo: trocear los documentos en Documents para indexar."""
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    crudos = _leer_documentos(carpeta)
    if not crudos:
        raise RuntimeError(f"No hay documentos en {carpeta} (.md/.txt/.pdf).")
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    frags: list[Document] = []
    for texto, fuente in crudos:
        for trozo in splitter.split_text(texto):
            frags.append(Document(page_content=trozo, metadata={"fuente": fuente}))
    return frags


# --- API pública (igual para ambos backends) ---------------------------------------------------
def cargar(carpeta: Path | None = None, reiniciar: bool = True) -> int:
    """Carga los documentos (def. data/reiki) al índice. Devuelve el nº de fragmentos indexados.

    Backend 'local': calcula embeddings una vez y persiste el índice a `LOCAL_FILE` (sin Redis).
    Backend 'redis': indexa en Redis. Ambos requieren `GOOGLE_API_KEY`.
    """
    carpeta = carpeta or CARPETA_DOCS
    frags = _fragmentos(carpeta)
    if BACKEND == "redis":
        if reiniciar:
            _borrar_indice_redis()
        store = _vector_store_redis(from_existing=False)
        store.add_documents(frags)
        return len(frags)
    # backend local
    from langchain_core.vectorstores import InMemoryVectorStore

    store = InMemoryVectorStore(_embeddings())
    store.add_documents(frags)
    LOCAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    store.dump(str(LOCAL_FILE))  # persiste chunks + vectores a JSON (sin servidor)
    return len(frags)


def buscar(consulta: str, k: int = 4) -> list[dict]:
    """Recupera los `k` fragmentos más relevantes. [{texto, fuente}]."""
    if BACKEND == "redis":
        store = _vector_store_redis(from_existing=True)
    else:
        from langchain_core.vectorstores import InMemoryVectorStore

        store = InMemoryVectorStore.load(str(LOCAL_FILE), _embeddings())
    docs = store.similarity_search(consulta, k=k)
    return [{"texto": d.page_content, "fuente": d.metadata.get("fuente", "")} for d in docs]


def disponible() -> bool:
    """True si el RAG está listo para consultar (sin tocar embeddings ni la clave)."""
    if BACKEND == "redis":
        try:
            from redis import Redis

            return bool(Redis.from_url(REDIS_URL).ping())
        except Exception:  # noqa: BLE001
            return False
    return LOCAL_FILE.exists()
