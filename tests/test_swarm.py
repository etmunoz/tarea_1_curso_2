# --8<-- encabezado-grupo
# Archivo: tests/test_swarm.py
# Objetivo: Pruebas del swarm (vuelos + hoteles + actividades).
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1920
# Última modificación: 20261110 1941
# --8<-- fin-encabezado-grupo

"""Pruebas del swarm (vuelos + hoteles + actividades).

La herramienta de actividades se prueba sin API key. El swarm completo requiere
GOOGLE_API_KEY (construye Gemini al importar graph.py): se salta si no hay clave.
"""
import os

import pytest

from src.agente_viajes.herramientas import ACTIVIDADES, buscar_actividades


def test_buscar_actividades_lima():
    r = buscar_actividades.invoke({"ciudad": "LIM"})
    assert len(r) == 2
    assert {"actividad", "tipo", "horas", "precio_clp"} <= set(r[0])


def test_buscar_actividades_ciudad_desconocida():
    assert buscar_actividades.invoke({"ciudad": "XXX"}) == []


def test_catalogo_cubre_las_tres_ciudades():
    assert set(ACTIVIDADES) == {"LIM", "BOG", "EZE"}


@pytest.mark.skipif(not os.environ.get("GOOGLE_API_KEY"), reason="requiere GOOGLE_API_KEY")
def test_swarm_incluye_actividades():
    from src.swarm.graph import actividades, graph  # noqa: PLC0415

    assert actividades.name == "actividades"
    assert graph is not None
