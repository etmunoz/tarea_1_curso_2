"""Punto de entrada temporal para los agentes del proyecto."""

import argparse
import asyncio
import importlib
import inspect

RUTAS_AGENTES = {
    "viajes": "src.agente_viajes.graph",
    "restaurantes": "src.agente_restaurantes.crew",
    "coordinador": "src.coordinador.graph",
    "meteorologo": "src.agente_meteorologo.graph",
}


def cargar_agente(nombre: str):
    """Importa el módulo del agente solicitado."""
    return importlib.import_module(RUTAS_AGENTES[nombre])


def ejecutar(funcion, *argumentos):
    """Ejecuta funciones síncronas o asíncronas de los agentes."""
    resultado = funcion(*argumentos)
    if inspect.isawaitable(resultado):
        return asyncio.run(resultado)
    return resultado


def main() -> None:
    """Lee la opción elegida y ejecuta el contrato temporal del agente."""
    parser = argparse.ArgumentParser(description="Ejecuta un agente del proyecto A2A.")
    parser.add_argument("agente", choices=RUTAS_AGENTES, help="Agente a ejecutar.")
    parser.add_argument("pregunta", nargs="?", default="", help="Pregunta para el agente.")
    parser.add_argument("--saltos", action="store_true", help="Muestra los nodos y herramientas recorridos.")
    parser.add_argument("--diagrama", action="store_true", help="Imprime el diagrama Mermaid sin ejecutar.")
    argumentos = parser.parse_intermixed_args()

    agente = cargar_agente(argumentos.agente)
    if argumentos.diagrama:
        resultado = ejecutar(agente.diagrama)
    elif argumentos.saltos:
        resultado = ejecutar(agente.saltos, argumentos.pregunta)
    else:
        resultado = ejecutar(agente.responder, argumentos.pregunta, None)
    if resultado is not None:
        print(resultado)


if __name__ == "__main__":
    main()
