"""Comprueba las rutas públicas de un servidor A2A."""

import argparse
import asyncio

import httpx


async def consultar(url: str) -> tuple[int, object]:
    """Consulta una URL con un timeout explícito."""
    async with httpx.AsyncClient(timeout=10.0) as cliente:
        respuesta = await cliente.get(url)
        respuesta.raise_for_status()
        return respuesta.status_code, respuesta.json()


async def comprobar(base_url: str) -> None:
    """Comprueba salud y tarjeta del servidor A2A indicado."""
    base_url = base_url.rstrip("/")
    rutas = {
        "Salud": f"{base_url}/health",
        "Agent Card": f"{base_url}/.well-known/agent-card.json",
    }

    for nombre, url in rutas.items():
        try:
            estado, contenido = await consultar(url)
            print(f"{nombre}: {estado} OK")
            print(contenido)
        except httpx.HTTPError as error:
            detalle = str(error).splitlines()[0] or error.__class__.__name__
            print(f"{nombre}: no fue posible consultar {url}: {detalle}")


def main() -> None:
    """Lee la dirección del servidor y ejecuta las comprobaciones."""
    parser = argparse.ArgumentParser(
        description="Comprueba la salud y la Agent Card de un servidor A2A."
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8080",
        help="Dirección base del servidor A2A.",
    )
    argumentos = parser.parse_args()
    asyncio.run(comprobar(argumentos.url))


if __name__ == "__main__":
    main()
