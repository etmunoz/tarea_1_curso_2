"""Comprueba que el coordinador conserva una conversación A2A."""

import asyncio
import os
import sys
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
import httpx


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))

from src.coordinador.cliente import obtener_cliente, preguntar


async def comprobar_salud(url: str) -> None:
    """Comprueba que el servidor del coordinador está disponible."""
    async with httpx.AsyncClient(timeout=10.0) as cliente_http:
        respuesta = await cliente_http.get(f"{url.rstrip('/')}/health")
        respuesta.raise_for_status()


def respuesta_valida(respuesta: str) -> bool:
    """Identifica respuestas útiles y descarta errores de delegación."""
    errores = (
        "No pude consultar al agente de viajes:",
        "El agente no pudo responder:",
        "El agente no devolvió una respuesta.",
    )
    return bool(respuesta.strip()) and not respuesta.startswith(errores)


def mostrar_intercambio(numero: int, pregunta: str, respuesta: str) -> None:
    """Imprime una consulta y su respuesta en un formato fácil de leer."""
    print(f"\n{'=' * 68}")
    print(f"CONSULTA {numero}")
    print(f"Pregunta: {pregunta}")
    print(f"{'-' * 68}")
    print("Respuesta:")
    print(respuesta)
    print(f"{'=' * 68}")


async def main() -> bool:
    """Hace dos consultas consecutivas con el mismo contexto al coordinador."""
    load_dotenv()
    url = os.getenv("URL_COORDINADOR", "http://127.0.0.1:8002")
    context_id = str(uuid4())
    cliente = None
    try:
        await comprobar_salud(url)
        cliente = await obtener_cliente(url)
        pregunta_uno = "Busca vuelos de LIM a SCL para el 15 de diciembre."
        pregunta_dos = "¿Cuál es la opción más económica de las que mencionaste?"
        primera = await preguntar(
            cliente,
            pregunta_uno,
            context_id,
        )
        segunda = await preguntar(
            cliente,
            pregunta_dos,
            context_id,
        )
        print(f"\nContexto compartido: {context_id}")
        mostrar_intercambio(1, pregunta_uno, primera)
        mostrar_intercambio(2, pregunta_dos, segunda)
        if not respuesta_valida(primera) or not respuesta_valida(segunda):
            print("La prueba falló: el coordinador no devolvió dos respuestas válidas.")
            return False
        print("Prueba completada: ambas consultas usaron el mismo contexto.")
        return True
    except Exception as error:
        detalle = str(error).splitlines()[0] or error.__class__.__name__
        print(f"No pude comprobar el coordinador: {detalle}")
        return False
    finally:
        if cliente is not None:
            await cliente.close()


if __name__ == "__main__":
    raise SystemExit(0 if asyncio.run(main()) else 1)
