<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/31-windows-bom-en-ps1.md`  
> **Objetivo:** 31 · Windows: arreglar la codificación de los `.ps1` (UTF-8 con BOM)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2226 · **Última modificación:** 20261111 1224
<!--/encabezado-grupo-->

# 31 · Windows: arreglar la codificación de los `.ps1` (UTF-8 con BOM)

> **Nota de numeración:** este registro se escribió como el 30 y se renumeró a 31 por el 29 que Ezequiel publicó desde el Mac; las citas del chat que decían «29 y 30» o «30» se ajustaron a «30 y 31» o «31».

**Fecha:** 2026-11-10 · **Equipo:** Windows (nodo Tomás)

## Prompt

> Sí, arréglala

*(respuesta a "¿Arreglo ahora la codificación de los .ps1 mientras llega la URL del Mac?")*

## Verificación pedida

- Que Windows PowerShell 5.1 lea bien las tildes y la "¿" de los `.ps1`, en especial las
  preguntas de `win_coordinador.ps1` que van a los agentes y a las evidencias.
- Que no se rompa nada: los scripts siguen parseando y la herramienta de encabezados sigue pasando.
