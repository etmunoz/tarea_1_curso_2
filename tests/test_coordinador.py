# --8<-- encabezado-grupo
# Archivo: tests/test_coordinador.py
# Objetivo: Pruebas del coordinador (supervisor).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1933
# Última modificación: 20261110 1941
# --8<-- fin-encabezado-grupo

"""Pruebas del coordinador (supervisor).

El parseo del catálogo y la extracción de texto A2A no requieren API key ni servidor.
El grafo supervisor completo requiere GOOGLE_API_KEY (construye Gemini al importar
graph.py): se salta si no hay clave.
"""
import os

import pytest

from src.coordinador import a2a, catalogo


def test_parse_urls_agentes():
    r = catalogo._parse_urls_agentes("https://a.io#agente_ana, https://b.io , c.io#g")
    assert r == [("https://a.io", "agente_ana"), ("https://b.io", "agente"), ("c.io", "g")]


def test_catalogo_local_desde_env(monkeypatch):
    monkeypatch.setenv("A2A_BASE", "http://127.0.0.1:2024")
    monkeypatch.setenv("A2A_GRAFOS_LOCALES", "agente_viajes,agente_ezequiel")
    monkeypatch.setenv("URLS_AGENTES", "")
    cat = catalogo.construir_catalogo()
    assert [(a.base_url, a.graph) for a in cat] == [
        ("http://127.0.0.1:2024", "agente_viajes"),
        ("http://127.0.0.1:2024", "agente_ezequiel"),
    ]


def test_texto_de_resultado_recorre_artifacts():
    res = {"status": {"state": "completed"}, "artifacts": [{"parts": [{"kind": "text", "text": "ok"}]}]}
    assert a2a._texto_de_resultado(res) == "ok"


@pytest.mark.skipif(not os.environ.get("GOOGLE_API_KEY"), reason="requiere GOOGLE_API_KEY")
def test_grafo_supervisor_compila():
    from src.coordinador.graph import graph  # noqa: PLC0415

    assert graph is not None
