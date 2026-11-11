# --8<-- encabezado-grupo
# Archivo: tests/test_coordinador.py
# Objetivo: Pruebas del coordinador (supervisor).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1933
# Última modificación: 20261110 2259
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
    """Prueba: parse urls agentes."""
    r = catalogo._parse_urls_agentes("https://a.io#agente_ana, https://b.io , c.io#g")
    assert r == [("https://a.io", "agente_ana"), ("https://b.io", "agente"), ("c.io", "g")]


def test_catalogo_local_desde_env(monkeypatch):
    """Prueba: catalogo local desde env."""
    monkeypatch.setenv("A2A_BASE", "http://127.0.0.1:2024")
    monkeypatch.setenv("A2A_GRAFOS_LOCALES", "agente_viajes,agente_ezequiel")
    monkeypatch.setenv("URLS_AGENTES", "")
    cat = catalogo.construir_catalogo()
    assert [(a.base_url, a.graph) for a in cat] == [
        ("http://127.0.0.1:2024", "agente_viajes"),
        ("http://127.0.0.1:2024", "agente_ezequiel"),
    ]


def test_catalogo_marca_locales_y_remotos(monkeypatch):
    """Prueba: los grafos de A2A_GRAFOS_LOCALES quedan local=True y los de URLS_AGENTES local=False."""
    monkeypatch.setenv("A2A_BASE", "http://127.0.0.1:2024")
    monkeypatch.setenv("A2A_GRAFOS_LOCALES", "agente_tomas")
    monkeypatch.setenv("URLS_AGENTES", "https://mac.example#agente_ezequiel")
    cat = catalogo.construir_catalogo()
    assert [(a.graph, a.local) for a in cat] == [("agente_tomas", True), ("agente_ezequiel", False)]


def test_ficha_se_pide_una_vez_y_nombre_consistente(monkeypatch):
    """Prueba: aunque el catálogo se rearme, la ficha se pide UNA vez; si luego el remoto
    fallara, el nombre sigue siendo el de la ficha (no el id del grafo)."""
    llamadas = []

    def falsa_card(base, graph, timeout=10):
        llamadas.append((base, graph))
        if len(llamadas) > 1:
            raise RuntimeError("el túnel no respondió")
        return {"name": "Agente de Ezequiel", "description": "IA"}

    monkeypatch.setattr(catalogo, "_cards", {})
    monkeypatch.setattr(catalogo.a2a, "agent_card", falsa_card)
    monkeypatch.setenv("A2A_GRAFOS_LOCALES", "")
    monkeypatch.setenv("URLS_AGENTES", "https://mac.example#agente_ezequiel")
    nombres = [a.nombre for _ in range(3) for a in catalogo.construir_catalogo()]
    assert nombres == ["Agente de Ezequiel"] * 3
    assert len(llamadas) == 1


def test_texto_de_resultado_recorre_artifacts():
    """Prueba: texto de resultado recorre artifacts."""
    res = {"status": {"state": "completed"}, "artifacts": [{"parts": [{"kind": "text", "text": "ok"}]}]}
    assert a2a._texto_de_resultado(res) == "ok"


def test_texto_de_resultado_no_duplica_ni_repite_la_pregunta():
    """Prueba: con history + artifacts (forma real de langgraph dev) sale la respuesta UNA vez."""
    res = {
        "kind": "task",
        "history": [
            {"role": "user", "parts": [{"kind": "text", "text": "¿Cuáles son los principios?"}]},
            {"role": "agent", "parts": [{"kind": "text", "text": "Solo por hoy…"}]},
        ],
        "status": {"state": "completed"},
        "artifacts": [{"parts": [{"kind": "text", "text": "Solo por hoy…"}]}],
    }
    assert a2a._texto_de_resultado(res) == "Solo por hoy…"


def test_texto_de_resultado_sin_artifacts_usa_ultimo_mensaje_del_agente():
    """Prueba: sin artifacts, toma el último mensaje del agente en history (no la pregunta)."""
    res = {"history": [
        {"role": "user", "parts": [{"kind": "text", "text": "pregunta"}]},
        {"role": "agent", "parts": [{"kind": "text", "text": "respuesta"}]},
    ]}
    assert a2a._texto_de_resultado(res) == "respuesta"


@pytest.mark.skipif(not os.environ.get("GOOGLE_API_KEY"), reason="requiere GOOGLE_API_KEY")
def test_grafo_supervisor_compila():
    """Prueba: grafo supervisor compila."""
    from src.coordinador.graph import graph  # noqa: PLC0415

    assert graph is not None
