"""Esqueleto del agente de restaurantes."""


def responder(texto: str, context_id: str | None) -> str:
    """Devuelve el aviso temporal mientras el agente no está implementado."""
    return "El agente de restaurantes todavía no existe."


def saltos(texto: str) -> str:
    """Informa que el agente todavía no tiene nodos ni herramientas."""
    return "El agente de restaurantes todavía no existe: no hay nodos ni herramientas por recorrer."


def diagrama() -> str:
    """Devuelve el diagrama temporal sin ejecutar el agente."""
    return "graph TD\n    Inicio[Agente de restaurantes pendiente]"
