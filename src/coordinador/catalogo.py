# --8<-- encabezado-grupo
# Archivo: src/coordinador/catalogo.py
# Objetivo: Catálogo de agentes del coordinador: de dónde salen y sus fichas.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1933
# Última modificación: 20261110 2124
# --8<-- fin-encabezado-grupo

"""Catálogo de agentes del coordinador: de dónde salen y sus fichas.

Las direcciones vienen del entorno (nunca del código, regla de AGENTS.md):

  A2A_BASE            base del servidor local de langgraph dev (def. http://127.0.0.1:2024)
  A2A_GRAFOS_LOCALES  grafos locales a incluir, separados por comas (def. agente_viajes,agente_ezequiel,agente_cocina,agente_tomas)
  URLS_AGENTES        agentes de compañeros: lista separada por comas de `url` o `url#grafo`
                      (si no se indica grafo, se asume 'agente'); cada url es su túnel público

Cada entrada del catálogo resuelve su Agent Card (nombre, descripción, skills) para
que el supervisor decida a quién enrutar. Las cards se piden una vez (lazy + cache).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

from src.coordinador import a2a

load_dotenv()


@dataclass
class AgenteRemoto:
    base_url: str
    graph: str
    _card: dict | None = field(default=None, repr=False)

    def card(self) -> dict:
        if self._card is None:
            self._card = a2a.agent_card(self.base_url, self.graph)
        return self._card

    @property
    def nombre(self) -> str:
        try:
            return self.card().get("name") or self.graph
        except Exception:  # noqa: BLE001 - si el agente no responde, usamos el grafo
            return self.graph

    def descripcion(self) -> str:
        try:
            c = self.card()
            skills = "; ".join(s.get("name", "") for s in c.get("skills", []) if s.get("name"))
            desc = c.get("description", "")
            return f"{desc} (skills: {skills})" if skills else desc
        except Exception:  # noqa: BLE001
            return "(ficha no disponible)"

    def preguntar(self, texto: str, context_id: str) -> str:
        return a2a.enviar_mensaje(self.base_url, self.graph, texto, context_id)


def _parse_urls_agentes(valor: str) -> list[tuple[str, str]]:
    salida = []
    for item in valor.split(","):
        item = item.strip()
        if not item:
            continue
        if "#" in item:
            url, graph = item.split("#", 1)
            salida.append((url.strip(), graph.strip()))
        else:
            salida.append((item, "agente"))
    return salida


def construir_catalogo() -> list[AgenteRemoto]:
    """Arma el catálogo desde el entorno: grafos locales + agentes de compañeros."""
    base = os.environ.get("A2A_BASE", "http://127.0.0.1:2024").rstrip("/")
    locales = os.environ.get("A2A_GRAFOS_LOCALES", "agente_viajes,agente_ezequiel,agente_cocina,agente_tomas")
    catalogo = [AgenteRemoto(base, g.strip()) for g in locales.split(",") if g.strip()]
    for url, graph in _parse_urls_agentes(os.environ.get("URLS_AGENTES", "")):
        catalogo.append(AgenteRemoto(url, graph))
    return catalogo


def texto_catalogo(catalogo: list[AgenteRemoto]) -> str:
    """Listado legible (nombre → descripción) para el prompt del supervisor."""
    return "\n".join(f"- {a.nombre}: {a.descripcion()}" for a in catalogo)
