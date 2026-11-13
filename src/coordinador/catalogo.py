"""Descubrimiento de agentes A2A disponibles para el supervisor."""

import os

from dotenv import load_dotenv

from src.coordinador.cliente import TARJETAS, obtener_cliente


load_dotenv()
URL_VIAJES = os.getenv("URL_VIAJES", "http://127.0.0.1:8080")
URL_RESTAURANTES = os.getenv("URL_RESTAURANTES", "http://127.0.0.1:8001")
URLS_AGENTES = os.getenv("URLS_AGENTES", "")
CATALOGO: list[dict] = []


async def descubrir() -> list[dict]:
    """Descubre los agentes disponibles y conserva sus clientes A2A."""
    CATALOGO.clear()
    urls = [URL_VIAJES, URL_RESTAURANTES] + [
        url.strip() for url in URLS_AGENTES.split(",") if url.strip()
    ]
    for url in dict.fromkeys(urls):
        try:
            cliente = await obtener_cliente(url)
            tarjeta = TARJETAS[url]
            CATALOGO.append(
                {
                    "nombre": tarjeta.name,
                    "descripcion": tarjeta.description,
                    "cliente": cliente,
                }
            )
        except Exception as error:
            detalle = str(error).splitlines()[0] or error.__class__.__name__
            print(f"No pude descubrir el agente en {url}: {detalle}")
    return CATALOGO
