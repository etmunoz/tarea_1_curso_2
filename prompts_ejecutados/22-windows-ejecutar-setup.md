<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/22-windows-ejecutar-setup.md`  
> **Objetivo:** 22 · Windows: ejecutar setup_windows.ps1 (clave Gemini y AVG)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2208 · **Última modificación:** 20261110 2208
<!--/encabezado-grupo-->

# 22 · Windows: ejecutar `setup_windows.ps1` (clave Gemini y AVG)

**Fecha:** 2026-11-10 · **Equipo:** Windows (nodo Tomás)

## Prompts (en orden, durante la misma ejecución)

> luego debes ejecutar .\scripts\setup_windows.ps1

> ya la agregué al .env directamente

*(se refiere a la `GOOGLE_API_KEY`, que el script pedía por consola)*

> lo paré yo

*(el usuario cortó con Ctrl+C la prueba de Gemini, que quedó reintentando)*

> dime qué excepcion pongo en AVG

> Ya la agregué

## Verificación pedida

- Que el setup corra completo: uv + Python 3.13, `uv sync`, `.env`, prueba de la clave,
  Redis local y carga del RAG.
- Que la clave de Gemini funcione desde Python.
