# --8<-- encabezado-grupo
# Archivo: src/coordinador/catalogo.py
# Objetivo: Catálogo de agentes del coordinador: de dónde salen y sus fichas.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1933
# Última modificación: 20261110 2349
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
import time
from dataclasses import dataclass

from dotenv import load_dotenv

from src.coordinador import a2a

load_dotenv()

# Caché de fichas compartida por todo el proceso: (base, graph) → (instante, card).
# El grafo arma el catálogo varias veces por pregunta (enrutar, _rama, consultar,
# sin_agente); sin esta caché cada vez pedía las fichas otra vez por el túnel, y si una
# fallaba a mitad de camino el agente aparecía con su id de grafo en vez de su nombre.
# Solo se guardan las respuestas exitosas; se renuevan cada CARD_TTL segundos.
CARD_TTL = float(os.environ.get("A2A_CARD_TTL", "120"))
_cards: dict[tuple[str, str], tuple[float, dict]] = {}


@dataclass
class AgenteRemoto:
    """Objetivo: representar un agente del catálogo (local o remoto) y hablar con él.
    Atributos: base_url (str) del servidor, graph (str) id del grafo,
    local (bool) True si corre en el servidor propio (A2A_BASE), False si es de un compañero."""

    base_url: str
    graph: str
    local: bool = False

    def card(self) -> dict:
        """Objetivo: devolver la Agent Card del agente (con la caché compartida y TTL).
        Entradas: ninguna. Salida: dict — la tarjeta A2A. Lanza excepción si no responde."""
        clave = (self.base_url.rstrip("/"), self.graph)
        guardada = _cards.get(clave)
        if guardada and time.monotonic() - guardada[0] < CARD_TTL:
            return guardada[1]
        card = a2a.agent_card(self.base_url, self.graph)
        _cards[clave] = (time.monotonic(), card)
        return card

    @property
    def nombre(self) -> str:
        """Objetivo: nombre legible del agente (de la ficha, o el id del grafo si no responde).
        Entradas: ninguna. Salida: str."""
        try:
            return self.card().get("name") or self.graph
        except Exception:  # noqa: BLE001 - si el agente no responde, usamos el grafo
            return self.graph

    def descripcion(self) -> str:
        """Objetivo: descripción + skills del agente para el prompt del supervisor.
        Entradas: ninguna. Salida: str — descripción (o '(ficha no disponible)')."""
        try:
            c = self.card()
            skills = "; ".join(s.get("name", "") for s in c.get("skills", []) if s.get("name"))
            desc = c.get("description", "")
            return f"{desc} (skills: {skills})" if skills else desc
        except Exception:  # noqa: BLE001
            return "(ficha no disponible)"

    def preguntar(self, texto: str, context_id: str) -> str:
        """Objetivo: enviar una pregunta a este agente por A2A.
        Entradas: texto (str), context_id (str) UUID de la conversación.
        Salida: str — la respuesta del agente."""
        return a2a.enviar_mensaje(self.base_url, self.graph, texto, context_id)


def _parse_urls_agentes(valor: str) -> list[tuple[str, str]]:
    """Objetivo: parsear la variable URLS_AGENTES en pares (url, grafo).
    Entradas: valor (str) lista separada por comas de `url` o `url#grafo`.
    Salida: list[tuple[str, str]] — (url, grafo); grafo por defecto 'agente'."""
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
    catalogo = [AgenteRemoto(base, g.strip(), local=True) for g in locales.split(",") if g.strip()]
    for url, graph in _parse_urls_agentes(os.environ.get("URLS_AGENTES", "")):
        catalogo.append(AgenteRemoto(url, graph, local=False))
    return catalogo


def texto_catalogo(catalogo: list[AgenteRemoto]) -> str:
    """Listado legible (nombre → descripción) para el prompt del supervisor."""
    return "\n".join(f"- {a.nombre}: {a.descripcion()}" for a in catalogo)
