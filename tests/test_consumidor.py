# --8<-- encabezado-grupo
# Archivo: tests/test_consumidor.py
# Objetivo: Pruebas del agente conversacional (consumidor).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1629
# Última modificación: 20261110 2147
# --8<-- fin-encabezado-grupo

"""Pruebas del agente conversacional (consumidor).

Las del precio BTC y el mapeo de contextId no requieren API key ni servidor.
Las que tocan el A2A real se saltan si `langgraph dev` no está arriba.
"""
import os

import httpx
import pytest

from src.consumidor import a2a_cliente

BASE = os.environ.get("A2A_VIAJES_URL", "http://127.0.0.1:2024")


def _servidor_arriba() -> bool:
    """Objetivo: decir si el servidor langgraph dev responde. Salida: bool."""
    try:
        return httpx.get(f"{BASE}/ok", timeout=3).status_code == 200
    except Exception:
        return False


def test_precio_btc_sin_dependencias():
    # Import local para no instanciar el modelo (graph.py construye Gemini al importar).
    """Prueba: precio btc sin dependencias."""
    from src.consumidor.herramientas import precio_btc  # noqa: PLC0415

    r = precio_btc.invoke({})
    assert r["activo"] == "BTC"
    assert 10_000 < r["precio_usd"] < 1_000_000


def test_context_id_estable_por_hilo():
    """Prueba: context id estable por hilo."""
    from src.consumidor.herramientas import _context_id_para  # noqa: PLC0415

    cfg = {"configurable": {"thread_id": "t1"}}
    a = _context_id_para(cfg)
    b = _context_id_para(cfg)
    c = _context_id_para({"configurable": {"thread_id": "t2"}})
    assert a == b           # mismo hilo → mismo contextId (el remoto recuerda)
    assert a != c           # hilos distintos → contextId distinto


def test_nuevo_context_id_es_uuid():
    """Prueba: nuevo context id es uuid."""
    import uuid

    uuid.UUID(a2a_cliente.nuevo_context_id())  # no lanza si es un UUID válido


@pytest.mark.skipif(not _servidor_arriba(), reason="langgraph dev no está corriendo")
def test_a2a_contra_viajes():
    """Prueba: a2a contra viajes."""
    ctx = a2a_cliente.nuevo_context_id()
    resp = a2a_cliente.enviar_mensaje("Quiero un vuelo de Santiago a Lima el 2026-11-10", context_id=ctx)
    assert "LATAM" in resp or "SKY" in resp
