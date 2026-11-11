# --8<-- encabezado-grupo
# Archivo: tests/test_rag_tomas.py
# Objetivo: Pruebas del RAG de Tomás que no requieren Redis ni API key.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2009
# Última modificación: 20261111 1406
# --8<-- fin-encabezado-grupo

"""Pruebas del RAG de Tomás que no requieren Redis ni API key.

La lectura de documentos y la degradación de la tool se prueban sin dependencias;
la indexación y la búsqueda reales requieren Redis + GOOGLE_API_KEY (no se prueban aquí).
"""
from src.agente_tomas import rag
from src.agente_tomas.herramientas import buscar_reiki


def test_lee_los_documentos_de_reiki():
    """Prueba: lee los documentos de reiki."""
    docs = rag._leer_documentos(rag.CARPETA_DOCS)
    nombres = {fuente for _, fuente in docs}
    assert len(docs) >= 4
    assert any("nivel-1" in n for n in nombres)
    assert all(texto.strip() for texto, _ in docs)


def test_disponible_devuelve_bool():
    """Prueba: disponible devuelve bool."""
    assert isinstance(rag.disponible(), bool)


def test_buscar_reiki_degrada_sin_redis():
    """Prueba: buscar reiki degrada sin redis."""
    if rag.disponible():
        import pytest

        pytest.skip("Redis está disponible; la degradación no aplica")
    r = buscar_reiki.invoke({"consulta": "¿qué es el nivel 2?"})
    assert isinstance(r, dict) and "nota" in r
