# --8<-- encabezado-grupo
# Archivo: tests/test_agente_tomas.py
# Objetivo: Pruebas de las herramientas del agente de Tomás (Maestro Reiki). Sin API key ni servidor.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1952
# Última modificación: 20261110 2140
# --8<-- fin-encabezado-grupo

"""Pruebas de las herramientas del agente de Tomás (Maestro Reiki). Sin API key ni servidor."""
from src.agente_tomas.herramientas import info_simbolo, posiciones_manos, principios_reiki


def test_principios_son_cinco():
    r = principios_reiki.invoke({})
    assert len(r) == 5
    assert all(p.lower().startswith("solo por hoy") for p in r)


def test_posiciones_zona_conocida():
    r = posiciones_manos.invoke({"zona": "espalda"})
    assert r["zona"] == "espalda" and len(r["posiciones"]) >= 2


def test_posiciones_zona_desconocida():
    r = posiciones_manos.invoke({"zona": "rodilla"})
    assert "nota" in r


def test_info_simbolo_distancia():
    r = info_simbolo.invoke({"nombre": "Hon Sha Ze Sho Nen"})
    assert r["nivel"] == "II" and "distancia" in r["para_que"]


def test_tema_ajeno_se_rechaza():
    r = info_simbolo.invoke({"nombre": "bitcoin"})
    assert "nota" in r and "No tengo" in r["nota"]
