"""Constructor de tarjetas A2A para los agentes del proyecto."""

from collections.abc import Sequence
import os

from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.utils.constants import PROTOCOL_VERSION_1_0
from dotenv import load_dotenv


load_dotenv()


DefinicionSkill = tuple[str, str, str, str]


def crear_tarjeta(
    nombre: str,
    descripcion: str,
    url: str,
    skills: Sequence[DefinicionSkill],
) -> AgentCard:
    """Crea la ficha A2A pública de un agente que usa mensajes de texto."""
    direccion = os.getenv("URL_PUBLICA", "").strip() or url
    habilidades = [
        AgentSkill(
            id=id_habilidad,
            name=nombre_habilidad,
            description=descripcion_habilidad,
            examples=[ejemplo],
            tags=[nombre],
            input_modes=["text/plain"],
            output_modes=["text/plain"],
        )
        for id_habilidad, nombre_habilidad, descripcion_habilidad, ejemplo in skills
    ]

    return AgentCard(
        name=nombre,
        description=descripcion,
        version="1.0.0",
        supported_interfaces=[
            AgentInterface(
                url=direccion,
                protocol_binding="JSONRPC",
                protocol_version=PROTOCOL_VERSION_1_0,
            )
        ],
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=habilidades,
    )
