# --8<-- encabezado-grupo
# Archivo: src/agente_tomas/rag.py
# Objetivo: RAG del agente de Tomás · documentos de Reiki en un Redis (vector store).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2009
# Última modificación: 20261111 1210
# --8<-- fin-encabezado-grupo

"""RAG del agente de Tomás · documentos de Reiki en un Redis (vector store).

Redis es local y **dockerizado** (ver `docker-compose.yml`); el profesor puede
apuntarlo a su Redis remoto cambiando `REDIS_URL` en el `.env`. Los embeddings se
calculan con Gemini (`GOOGLE_API_KEY`). Los imports pesados (langchain-redis, el
modelo de embeddings) son tardíos: importar este módulo no exige Redis ni la clave.

Variables de entorno:
  REDIS_URL     conexión a Redis (def. redis://localhost:6379)
  REDIS_INDEX   nombre del índice vectorial (def. reiki)
  MODELO_EMBEDDINGS   modelo de embeddings de Gemini (def. models/gemini-embedding-001)
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

RAIZ = Path(__file__).resolve().parent.parent.parent
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
REDIS_INDEX = os.environ.get("REDIS_INDEX", "reiki")
CARPETA_DOCS = Path(os.environ.get("REIKI_DOCS", RAIZ / "data" / "reiki"))


def _embeddings():
    """Objetivo: crear el modelo de embeddings de Gemini (import tardío; requiere GOOGLE_API_KEY).
    Entradas: ninguna. Salida: GoogleGenerativeAIEmbeddings."""
    from langchain_google_genai import GoogleGenerativeAIEmbeddings  # import tardío (requiere key)

    return GoogleGenerativeAIEmbeddings(model=os.environ.get("MODELO_EMBEDDINGS", "models/gemini-embedding-001"))


def _vector_store(from_existing: bool):
    """Objetivo: crear el vector store Redis del RAG.
    Entradas: from_existing (bool) True para abrir el índice ya creado.
    Salida: RedisVectorStore."""
    from langchain_redis import RedisConfig, RedisVectorStore  # import tardío

    config = RedisConfig(index_name=REDIS_INDEX, redis_url=REDIS_URL, from_existing=from_existing)
    return RedisVectorStore(_embeddings(), config=config)


def _sin_encabezado(texto: str) -> str:
    """Quita el encabezado de grupo (<!--encabezado-grupo--> … <!--/encabezado-grupo-->)
    para no indexarlo como contenido del RAG."""
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


def cargar(carpeta: Path | None = None, reiniciar: bool = True) -> int:
    """Carga los documentos de `carpeta` (def. data/reiki) al índice de Redis.

    Trocea cada documento y lo indexa. Devuelve el nº de fragmentos indexados.
    Requiere Redis accesible y `GOOGLE_API_KEY`.
    """
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    carpeta = carpeta or CARPETA_DOCS
    crudos = _leer_documentos(carpeta)
    if not crudos:
        raise RuntimeError(f"No hay documentos en {carpeta} (.md/.txt/.pdf).")

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    fragmentos: list[Document] = []
    for texto, fuente in crudos:
        for trozo in splitter.split_text(texto):
            fragmentos.append(Document(page_content=trozo, metadata={"fuente": fuente}))

    if reiniciar:
        _borrar_indice()
    store = _vector_store(from_existing=False)
    store.add_documents(fragmentos)
    return len(fragmentos)


def _borrar_indice() -> None:
    """Objetivo: borrar el índice del RAG en Redis (si existe), para re-ingestar limpio.
    Entradas: ninguna. Salida: None."""
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


def buscar(consulta: str, k: int = 4) -> list[dict]:
    """Recupera los `k` fragmentos más relevantes del índice. [{texto, fuente}]."""
    store = _vector_store(from_existing=True)
    docs = store.similarity_search(consulta, k=k)
    return [{"texto": d.page_content, "fuente": d.metadata.get("fuente", "")} for d in docs]


def disponible() -> bool:
    """True si Redis responde (sin tocar embeddings ni la clave)."""
    try:
        from redis import Redis

        return bool(Redis.from_url(REDIS_URL).ping())
    except Exception:  # noqa: BLE001
        return False
