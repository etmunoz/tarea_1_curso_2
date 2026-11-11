# --8<-- encabezado-grupo
# Archivo: tests/test_bd_modelos.py
# Objetivo: Pruebas de la base SQLite de modelos de ciencia de datos. Sin API key ni servidor.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2009
# Última modificación: 20261111 1413
# --8<-- fin-encabezado-grupo

"""Pruebas de la base SQLite de modelos de ciencia de datos. Sin API key ni servidor."""
import sqlite3

from src.agente_ezequiel import bd_modelos
from src.agente_ezequiel.herramientas import consultar_modelos


def test_bd_se_crea_y_puebla():
    """Prueba: bd se crea y puebla."""
    p = bd_modelos.asegurar_bd(forzar=True)
    assert p.exists()
    con = sqlite3.connect(p)
    try:
        assert con.execute("SELECT COUNT(*) FROM modelos").fetchone()[0] >= 15
    finally:
        con.close()


def test_tipos_presentes():
    """Prueba: tipos presentes."""
    tipos = {m["tipo"] for m in bd_modelos.consultar(limite=100)}
    assert {"supervisado", "no supervisado", "refuerzo"} <= tipos


def test_consultar_por_tipo_refuerzo():
    """Prueba: consultar por tipo refuerzo."""
    r = consultar_modelos.invoke({"tipo": "refuerzo"})
    assert r and all(m["tipo"] == "refuerzo" for m in r)


def test_consultar_trae_las_columnas():
    """Prueba: consultar trae las columnas."""
    r = consultar_modelos.invoke({"consulta": "xgboost"})
    assert r
    assert {"nombre", "tipo", "para_que", "como_se_utiliza", "librerias", "ejemplo_python"} <= set(r[0])


def test_consulta_vacia_sin_coincidencias():
    """Prueba: consulta vacia sin coincidencias."""
    assert consultar_modelos.invoke({"consulta": "zzzzzzz-no-existe"}) == []
