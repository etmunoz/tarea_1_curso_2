# --8<-- encabezado-grupo
# Archivo: tests/test_bd_recetas.py
# Objetivo: Pruebas de la BD de recetas chilenas y el costeo. Sin API key ni servidor.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2013
# Última modificación: 20261110 2013
# --8<-- fin-encabezado-grupo

"""Pruebas de la BD de recetas chilenas y el costeo. Sin API key ni servidor."""
from src.agente_cocina import bd_recetas
from src.agente_cocina.herramientas import costear_receta, listar_recetas, ver_receta


def test_hay_unas_20_recetas():
    bd_recetas.asegurar_bd(forzar=True)
    assert len(listar_recetas.invoke({})) >= 20


def test_ver_receta_trae_ingredientes_con_unidad():
    r = ver_receta.invoke({"nombre": "Pastel de choclo"})
    assert r["nombre"] == "Pastel de choclo"
    assert all({"ingrediente", "cantidad", "unidad"} <= set(i) for i in r["ingredientes"])


def test_costeo_para_4_personas():
    r = costear_receta.invoke({"nombre": "Pastel de choclo", "personas": 4})
    # el total es la suma de los costos por ingrediente
    assert r["total_clp"] == round(sum(d["costo_clp"] for d in r["detalle"]))
    assert r["por_persona_clp"] == round(r["total_clp"] / 4)


def test_escala_por_personas():
    base = costear_receta.invoke({"nombre": "Cazuela de vacuno", "personas": 4})["total_clp"]
    doble = costear_receta.invoke({"nombre": "Cazuela de vacuno", "personas": 8})["total_clp"]
    assert abs(doble - 2 * base) <= 2  # el doble de personas ≈ el doble de costo


def test_receta_desconocida():
    assert "nota" in costear_receta.invoke({"nombre": "sushi"})
