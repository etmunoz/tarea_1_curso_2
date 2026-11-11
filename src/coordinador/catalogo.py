# --8<-- encabezado-grupo
# Archivo: src/coordinador/catalogo.py
# Objetivo: Catálogo de agentes del coordinador: de dónde salen y sus fichas.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1933
# Última modificación: 20261111 1406
# --8<-- fin-encabezado-grupo

"""Catálogo de agentes del coordinador: de dónde salen y sus fichas.

Las direcciones vienen del entorno (nunca del código, regla de AGENTS.md):

  A2A_BASE            base del servidor local de langgraph dev (def. http://127.0.0.1:2024)
  A2A_GRAFOS_LOCALES  grafos locales a incluir, separados por comas (def. agente_viajes,agente_ezequiel,agente_cocina,agente_tomas)
  URLS_AGENTES        agentes de compañeros: lista separada por comas de `url` o `url#grafo`
                      (si no se indica grafo, se asume 'agente'); cada url es su túnel público
  A2A_AGENTES_PERMITIDOS  allow-list opcional de grafos permitidos (coma-separada); si está
                      definida, solo esos agentes entran al catálogo (los "tools" del coordinador)

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

# Última ficha conocida por (base, graph), SIN expiración: guarda las CAPACIDADES del agente
# aunque ahora esté caído, para distinguir "inexistente" (nunca se supo qué hace) de
# "desconectado" (sí sabemos qué hace, pero no responde ahora).
_ultima_card: dict[tuple[str, str], dict] = {}

# Caché corta del estado de disponibilidad, para no sondear la red en cada rearmado del
# catálogo (enrutar, _rama, consultar… construyen el catálogo varias veces por pregunta).
DISP_TTL = float(os.environ.get("A2A_DISP_TTL", "15"))
_disp: dict[tuple[str, str], tuple[float, bool, str]] = {}


@dataclass
class AgenteRemoto:
    """Objetivo: representar un agente del catálogo (local o remoto) y hablar con él.
    Atributos: base_url (str) del servidor, graph (str) id del grafo,
    local (bool) True si corre en el servidor propio (A2A_BASE), False si es de un compañero."""

    base_url: str
    graph: str
    local: bool = False

    @property
    def _clave(self) -> tuple[str, str]:
        return (self.base_url.rstrip("/"), self.graph)

    def card(self) -> dict:
        """Objetivo: devolver la Agent Card FRESCA (caché con TTL). La guarda también como
        'última conocida' (sin expiración) para conservar las capacidades si luego cae.
        Entradas: ninguna. Salida: dict. Lanza excepción si no responde."""
        clave = self._clave
        guardada = _cards.get(clave)
        if guardada and time.monotonic() - guardada[0] < CARD_TTL:
            return guardada[1]
        card = a2a.agent_card(self.base_url, self.graph)
        _cards[clave] = (time.monotonic(), card)
        _ultima_card[clave] = card
        return card

    def card_conocida(self) -> dict | None:
        """Objetivo: la ÚLTIMA ficha conocida del agente (capacidades), aunque ahora esté caído.
        Entradas: ninguna. Salida: dict | None (None si nunca se descubrió)."""
        return _ultima_card.get(self._clave)

    def estado(self) -> tuple[bool, str]:
        """Objetivo: decir si el agente responde AHORA (con caché corta para no sondear de más).
        Entradas: ninguna. Salida: (disponible (bool), motivo (str) vacío si está bien)."""
        clave = self._clave
        guardado = _disp.get(clave)
        if guardado and time.monotonic() - guardado[0] < DISP_TTL:
            return guardado[1], guardado[2]
        try:
            self.card()
            disp, motivo = True, ""
        except a2a.ErrorA2A as exc:
            disp, motivo = False, exc.motivo
        except Exception as exc:  # noqa: BLE001
            disp, motivo = False, str(exc)[:80]
        _disp[clave] = (time.monotonic(), disp, motivo)
        return disp, motivo

    def disponible(self) -> bool:
        """Objetivo: azúcar de `estado()` — True si responde ahora. Salida: bool."""
        return self.estado()[0]

    def conocido(self) -> bool:
        """Objetivo: True si alguna vez supimos sus capacidades (tiene ficha conocida).
        Distingue 'desconectado pero conocido' de 'inexistente'. Salida: bool."""
        return self.card_conocida() is not None

    @property
    def nombre(self) -> str:
        """Objetivo: nombre legible del agente, usando la ficha conocida si ahora no responde.
        Entradas: ninguna. Salida: str (nombre o id del grafo)."""
        conocida = self.card_conocida()
        if conocida and conocida.get("name"):
            return conocida["name"]
        try:
            return self.card().get("name") or self.graph
        except Exception:  # noqa: BLE001 - si el agente no responde ni hay ficha previa
            return self.graph

    def descripcion(self) -> str:
        """Objetivo: descripción + skills para el prompt del supervisor, usando la ficha CONOCIDA
        (capacidades) aunque esté caído. Entradas: ninguna. Salida: str ('(sin ficha)' si nunca
        se descubrió)."""
        c = self.card_conocida()
        if c is None:
            try:
                c = self.card()
            except Exception:  # noqa: BLE001
                return "(sin ficha)"
        skills = "; ".join(s.get("name", "") for s in c.get("skills", []) if s.get("name"))
        desc = c.get("description", "")
        return f"{desc} (skills: {skills})" if skills else (desc or "(sin descripción)")

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


def _agentes_permitidos() -> set[str] | None:
    """Objetivo: allow-list EXPLÍCITO de grafos que el coordinador puede invocar.
    Los "tools" del coordinador son los agentes; esta lista blanca (variable
    `A2A_AGENTES_PERMITIDOS`, grafos separados por comas) acota cuáles corren, aunque
    `URLS_AGENTES`/`A2A_GRAFOS_LOCALES` traigan otros (defensa ante mala configuración o
    un túnel colado). Entradas: ninguna. Salida: set[str] con los permitidos, o None si
    no se definió la variable (entonces se permiten todos, compatible hacia atrás)."""
    v = os.environ.get("A2A_AGENTES_PERMITIDOS", "").strip()
    permitidos = {g.strip() for g in v.split(",") if g.strip()}
    return permitidos or None


def construir_catalogo() -> list[AgenteRemoto]:
    """Arma el catálogo desde el entorno: grafos locales + agentes de compañeros,
    filtrado por el allow-list `A2A_AGENTES_PERMITIDOS` si está definido."""
    base = os.environ.get("A2A_BASE", "http://127.0.0.1:2024").rstrip("/")
    locales = os.environ.get("A2A_GRAFOS_LOCALES", "agente_viajes,agente_ezequiel,agente_cocina,agente_tomas")
    catalogo = [AgenteRemoto(base, g.strip(), local=True) for g in locales.split(",") if g.strip()]
    for url, graph in _parse_urls_agentes(os.environ.get("URLS_AGENTES", "")):
        catalogo.append(AgenteRemoto(url, graph, local=False))
    permitidos = _agentes_permitidos()
    if permitidos is not None:
        catalogo = [a for a in catalogo if a.graph in permitidos]
    return catalogo


def texto_catalogo(catalogo: list[AgenteRemoto]) -> str:
    """Objetivo: listado legible para el prompt del supervisor. Muestra las CAPACIDADES de cada
    agente (desde su última ficha conocida) y una etiqueta de disponibilidad, de modo que un
    agente desconectado pero CONOCIDO siga siendo elegible por su especialidad (el sistema
    maneja la indisponibilidad al consultar). Resiliente: nunca rompe por un agente caído.
    Entradas: catalogo. Salida: str."""
    lineas = []
    for a in catalogo:
        disp, _motivo = a.estado()
        if disp:
            lineas.append(f"- {a.nombre}: {a.descripcion()}")
        elif a.conocido():
            lineas.append(f"- {a.nombre}: {a.descripcion()} "
                          "[estado: temporalmente NO disponible; elígelo igual si es el especialista]")
        else:
            lineas.append(f"- {a.nombre}: (agente no descubierto / sin ficha; no elegible ahora)")
    return "\n".join(lineas)
