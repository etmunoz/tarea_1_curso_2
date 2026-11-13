"""Prueba las decisiones del supervisor mediante su servidor A2A."""

import asyncio
import os
import sys
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))

from src.coordinador.cliente import obtener_cliente, preguntar


PREGUNTAS = [
    "Busca vuelos de LIM a SCL para el 15 de diciembre.",
    "¿Qué hoteles hay en Lima para 3 noches?",
    "Busca restaurantes de comida argentina en EZE.",
    "Dame el detalle de Parrilla Palermo.",
    "¿Qué me recomiendas para mi próximo viaje?",
    "¿Cómo preparo una torta de chocolate?",
]


def extraer_datos(respuesta: str) -> tuple[str, str, str]:
    """Extrae agente, motivo y el inicio de la respuesta del supervisor."""
    lineas = respuesta.splitlines()
    encabezado = lineas[0] if lineas else "[ninguno]"
    agente = encabezado.split("]", maxsplit=1)[0].removeprefix("[")
    motivo = encabezado.partition("Motivo:")[2].strip() or "Sin motivo"
    texto = " ".join(lineas[1:]).strip()
    return agente, motivo, texto[:90] + ("..." if len(texto) > 90 else "")


def mostrar_tabla(filas: list[tuple[str, str, str, str]]) -> None:
    """Imprime los resultados en una tabla sin dependencias adicionales."""
    encabezados = ("Pregunta", "Agente", "Motivo", "Inicio de respuesta")
    anchos = [
        max(len(encabezado), *(len(fila[indice]) for fila in filas))
        for indice, encabezado in enumerate(encabezados)
    ]
    separador = "+" + "+".join("-" * (ancho + 2) for ancho in anchos) + "+"
    print(separador)
    print(
        "|"
        + "|".join(
            f" {encabezado:<{anchos[indice]}} "
            for indice, encabezado in enumerate(encabezados)
        )
        + "|"
    )
    print(separador)
    for fila in filas:
        print(
            "|"
            + "|".join(
                f" {valor:<{anchos[indice]}} "
                for indice, valor in enumerate(fila)
            )
            + "|"
        )
    print(separador)


async def main() -> None:
    """Envía seis preguntas y muestra las decisiones del supervisor."""
    load_dotenv()
    url = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8002")
    cliente = None
    filas = []
    try:
        cliente = await obtener_cliente(url)
        for pregunta in PREGUNTAS:
            respuesta = await preguntar(cliente, pregunta, str(uuid4()))
            agente, motivo, inicio = extraer_datos(respuesta)
            filas.append((pregunta, agente, motivo, inicio))
        mostrar_tabla(filas)
    except Exception as error:
        detalle = str(error).splitlines()[0] or error.__class__.__name__
        print(f"No pude probar el supervisor: {detalle}")
    finally:
        if cliente is not None:
            await cliente.close()


if __name__ == "__main__":
    asyncio.run(main())
