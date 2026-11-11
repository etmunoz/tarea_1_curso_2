# --8<-- encabezado-grupo
# Archivo: tools/probar_gemini.py
# Objetivo: Prueba mínima y directa de la GOOGLE_API_KEY contra Gemini.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2030
# Última modificación: 20261111 1738
# --8<-- fin-encabezado-grupo

"""Prueba mínima y directa de la GOOGLE_API_KEY contra Gemini.

Verifica que la clave del `.env` está presente y que una llamada simple al modelo
responde. Diagnostica los errores típicos (clave inválida, sin saldo/cuota) con un
mensaje claro, sin volcar el traceback completo.

Uso:
    uv run python tools/probar_gemini.py
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import os  # noqa: E402

from dotenv import load_dotenv  # noqa: E402

load_dotenv(RAIZ / ".env")  # ruta explícita: funciona aunque se ejecute desde stdin


def main() -> int:
    """Objetivo: validar la GOOGLE_API_KEY con una llamada simple a Gemini, con diagnóstico.
    Entradas: ninguna (lee .env). Salida: int — 0 si responde, 1 si falla (con el motivo)."""
    clave = os.environ.get("GOOGLE_API_KEY", "")
    modelo = os.environ.get("MODELO", "gemini-3.5-flash-lite")
    print(f"GOOGLE_API_KEY presente: {bool(clave)} · longitud: {len(clave)} · modelo: {modelo}")
    if not clave:
        print("✗ Falta GOOGLE_API_KEY en .env (cópiala de .env.example y pon tu clave).")
        return 1

    from langchain_google_genai import ChatGoogleGenerativeAI  # import tardío

    try:
        m = ChatGoogleGenerativeAI(model=modelo)
        r = m.invoke("Responde solo con la palabra: OK")
        texto = getattr(r, "content", str(r))
        print(f"✓ Gemini respondió: {texto!r}")
        print("La API key funciona.")
        return 0
    except Exception as exc:  # noqa: BLE001 - diagnóstico amable
        msg = str(exc)
        if "RESOURCE_EXHAUSTED" in msg or "402" in msg or "credits" in msg.lower():
            print("✗ La clave es válida pero el proyecto no tiene saldo/cuota (RESOURCE_EXHAUSTED / 402).")
            print("  → Vincula facturación o usa un proyecto con free tier: https://ai.studio/projects")
        elif "API_KEY_INVALID" in msg or "API key not valid" in msg or "400" in msg:
            print("✗ La clave parece inválida. Revísala en https://aistudio.google.com/apikey")
        elif "PERMISSION_DENIED" in msg or "403" in msg or "SERVICE_DISABLED" in msg:
            print("✗ Permiso denegado. Habilita la 'Generative Language API' en el proyecto de la clave.")
        elif "NOT_FOUND" in msg or "404" in msg:
            print(f"✗ Modelo '{modelo}' no encontrado para esta clave. Prueba otro valor de MODELO en .env.")
        else:
            print(f"✗ Error llamando a Gemini: {msg[:300]}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
