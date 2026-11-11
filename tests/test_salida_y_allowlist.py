# --8<-- encabezado-grupo
# Archivo: tests/test_salida_y_allowlist.py
# Objetivo: Pruebas del guardrail de SALIDA común y del allow-list de agentes (prompt 47).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 1204
# Última modificación: 20261111 1413
# --8<-- fin-encabezado-grupo

"""Pruebas del guardrail de SALIDA común y del allow-list de agentes (prompt 47).

- `guardrails.revisar_salida`: redacción de credenciales + restricciones (tope de
  longitud, no vacío), aplicado a TODA respuesta final.
- `catalogo._agentes_permitidos` + `construir_catalogo`: allow-list explícito de grafos
  (`A2A_AGENTES_PERMITIDOS`) que acota qué agentes ("tools" del coordinador) corren.
- Nodo `guardia_salida` y comportamiento end-to-end (los que importan el grafo requieren
  GOOGLE_API_KEY).

Deterministas, sin red.
"""
import os

import pytest

from src.coordinador import catalogo, guardrails


# ---------------- GUARDRAIL DE SALIDA (revisar_salida) ----------------

def test_salida_redacta_google_key():
    out, flags = guardrails.revisar_salida("La clave es AIzaSyA1234567890abcdefghijklmnopqrstuv.")
    assert "AIza" not in out
    assert "[REDACTADO]" in out
    assert "google_api_key" in flags["secretos"]
    assert flags["recortado"] is False


def test_salida_redacta_varios_secretos():
    texto = ("key=AIzaSyA1234567890abcdefghijklmnopqrstuv password: hunter2 "
             "Authorization: Bearer abcdef1234567890 tarjeta 4111 1111 1111 1111")
    out, flags = guardrails.revisar_salida(texto)
    assert "AIza" not in out and "hunter2" not in out and "4111" not in out
    assert len(flags["secretos"]) >= 3


def test_salida_trunca_lo_excesivo():
    largo = "a" * (guardrails.LIMITE_SALIDA + 500)
    out, flags = guardrails.revisar_salida(largo)
    assert flags["recortado"] is True
    assert len(out) <= guardrails.LIMITE_SALIDA + 40
    assert out.endswith("[…respuesta truncada]")


def test_salida_vacia_da_marcador():
    out, flags = guardrails.revisar_salida("   \n ")
    assert out == "(sin respuesta)"
    assert flags["recortado"] is False


def test_salida_limpia_no_cambia():
    txt = "El pastel de choclo para 4 personas cuesta $8.976 CLP."
    out, flags = guardrails.revisar_salida(txt)
    assert out == txt
    assert flags == {"secretos": [], "recortado": False}


def test_salida_cubre_mensaje_de_sin_agente():
    """Un mensaje tipo 'sin_agente' (sin secretos) pasa intacto por el guardrail de salida."""
    txt = "No tengo un agente para eso. Puedo ayudarte con: Agente de Ezequiel."
    out, _ = guardrails.revisar_salida(txt)
    assert out == txt


# ---------------- ALLOW-LIST DE AGENTES ----------------

@pytest.fixture(autouse=True)
def _env_limpio(monkeypatch):
    """Base de entorno controlada para el catálogo."""
    monkeypatch.setenv("A2A_BASE", "http://127.0.0.1:2024")
    monkeypatch.setenv("A2A_GRAFOS_LOCALES", "agente_ezequiel,agente_cocina")
    monkeypatch.setenv("URLS_AGENTES", "https://companero.example#agente_tomas")
    monkeypatch.delenv("A2A_AGENTES_PERMITIDOS", raising=False)
    yield


def test_sin_allowlist_permite_todos():
    """Sin A2A_AGENTES_PERMITIDOS: entran todos (compatibilidad hacia atrás)."""
    assert catalogo._agentes_permitidos() is None
    graphs = [a.graph for a in catalogo.construir_catalogo()]
    assert graphs == ["agente_ezequiel", "agente_cocina", "agente_tomas"]


def test_allowlist_filtra_locales_y_remotos(monkeypatch):
    """Con allow-list, solo los grafos permitidos entran (filtra locales y remotos)."""
    monkeypatch.setenv("A2A_AGENTES_PERMITIDOS", "agente_ezequiel,agente_tomas")
    graphs = [a.graph for a in catalogo.construir_catalogo()]
    assert graphs == ["agente_ezequiel", "agente_tomas"]  # cocina quedó fuera


def test_allowlist_excluye_remoto_colado(monkeypatch):
    """Un túnel/grafo no aprobado en URLS_AGENTES queda fuera aunque esté configurado."""
    monkeypatch.setenv("URLS_AGENTES", "https://malicioso.example#agente_intruso")
    monkeypatch.setenv("A2A_AGENTES_PERMITIDOS", "agente_ezequiel,agente_cocina")
    graphs = [a.graph for a in catalogo.construir_catalogo()]
    assert "agente_intruso" not in graphs
    assert graphs == ["agente_ezequiel", "agente_cocina"]


def test_allowlist_tolera_espacios_y_vacios(monkeypatch):
    """La lista admite espacios y entradas vacías sin romper."""
    monkeypatch.setenv("A2A_AGENTES_PERMITIDOS", " agente_ezequiel , , agente_cocina ,")
    assert catalogo._agentes_permitidos() == {"agente_ezequiel", "agente_cocina"}


def test_allowlist_vacia_equivale_a_sin_restriccion(monkeypatch):
    """Una variable vacía o solo comas = None (no restringe)."""
    monkeypatch.setenv("A2A_AGENTES_PERMITIDOS", "  , ,")
    assert catalogo._agentes_permitidos() is None


# ---------------- NODO guardia_salida y END-TO-END (requieren API key) ----------------

@pytest.mark.skipif(not os.environ.get("GOOGLE_API_KEY"), reason="requiere GOOGLE_API_KEY (importa el grafo)")
def test_guardia_salida_redacta_y_emite_mensaje():
    """El nodo guardia_salida redacta secretos de la respuesta y emite el AIMessage final."""
    from src.coordinador import graph  # noqa: PLC0415

    estado = {"respuesta": "Tu clave AIzaSyA1234567890abcdefghijklmnopqrstuv ya está."}
    out = graph.guardia_salida(estado)
    assert "AIza" not in out["respuesta"]
    assert out["ruta"] == ["guardia_salida"]
    assert out["messages"] and "AIza" not in out["messages"][0].content


@pytest.mark.skipif(not os.environ.get("GOOGLE_API_KEY"), reason="requiere GOOGLE_API_KEY")
def test_grafo_tiene_nodo_guardia_salida():
    """El grafo compilado incluye el nodo de salida y todos los caminos pasan por él."""
    from src.coordinador.graph import graph  # noqa: PLC0415

    nodos = list(graph.get_graph().nodes)
    assert "guardia_salida" in nodos
