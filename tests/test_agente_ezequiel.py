# --8<-- encabezado-grupo
# Archivo: tests/test_agente_ezequiel.py
# Objetivo: Pruebas de las herramientas del agente de Ezequiel. No requieren API key ni servidor.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1603
# Última modificación: 20261111 1738
# --8<-- fin-encabezado-grupo

"""Pruebas de las herramientas del agente de Ezequiel. No requieren API key ni servidor."""
from src.agente_ezequiel.herramientas import (
    elegir_modelo,
    metricas_recomendadas,
    recomendar_tecnica,
)


def test_recomendar_tecnica_conocida():
    """Prueba: recomendar tecnica conocida."""
    r = recomendar_tecnica.invoke({"problema": "desbalance de clases"})
    assert r["problema"] == "desbalance de clases"
    assert "tecnica" in r and "por_que" in r


def test_metricas_regresion():
    """Prueba: metricas regresion."""
    r = metricas_recomendadas.invoke({"tipo_problema": "regresion"})
    assert r["tipo"] == "regresion"
    assert "RMSE" in r["metricas"]


def test_elegir_modelo_tabular():
    """Prueba: elegir modelo tabular."""
    r = elegir_modelo.invoke({"tipo_de_dato": "tabular"})
    assert "gradient boosting" in r["modelo"].lower()


def test_match_sin_acentos_y_palabra_suelta():
    # "clasificar" debe casar con la clave "clasificacion"
    """Prueba: match sin acentos y palabra suelta."""
    r = metricas_recomendadas.invoke({"tipo_problema": "clasificar correos"})
    assert r["tipo"].startswith("clasificacion")


def test_tema_ajeno_se_rechaza_en_una_linea():
    """Prueba: tema ajeno se rechaza en una linea."""
    r = recomendar_tecnica.invoke({"problema": "cómo hago un asado"})
    assert "nota" in r and "No tengo" in r["nota"]
