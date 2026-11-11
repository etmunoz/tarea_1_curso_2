<!--encabezado-grupo-->
> **Archivo:** `evidencias/README.md`  
> **Objetivo:** Evidencias  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1941 · **Última modificación:** 20261111 1438
<!--/encabezado-grupo-->

# Evidencias

Capturas y archivos que pide la rúbrica (Paso 9). Guardar aquí con estos nombres.
Las que requieren el agente vivo necesitan `GOOGLE_API_KEY` + `uv run langgraph dev`.

| Archivo | Qué debe mostrar | Cómo producirla |
|---|---|---|
| `01-saltos.png` | el agente usa su herramienta con una pregunta de tu tema y **rechaza** una de otro tema | correr el notebook `notebooks/ezequiel_paso_a_paso.ipynb` (paso 3) o `message/send` por A2A y capturar |
| `02-ficha-agente_*.json` | tu Agent Card final (descripción "sé/no hago" + skills) | `uv run python tools/configurar_fichas.py --guardar-evidencia` |
| `03-tunel.png` | la terminal de `cloudflared` con tu URL + la ficha vista desde fuera | `cloudflared tunnel --url http://127.0.0.1:2024` y abrir la URL/ficha |
| `04-catalogo-{mac,windows}.txt` | el coordinador con los agentes de otros computadores en el catálogo | `uv run python tools/guardar_evidencias.py --etiqueta mac` (con `URLS_AGENTES` cargado) |
| `05-ronda-{mac,windows}.md` | las preguntas de la ronda con el agente elegido, la ruta y la respuesta `[Agente de …]` | `./scripts/mac_coordinador.sh "<túnel-windows>"` (muestra `ruta:` y `[Nombre] …`) |
| `06-robustez-mac.md` | resiliencia (remoto caído) + guardrails de entrada/salida/A2A + allow-list de agentes | `uv run python tools/evidencia_robustez.py --remoto <url-caida> --etiqueta mac` |
| `07-grafo-coordinador.svg` | grafo del coordinador (guardia_entrada → enrutar → consultar/sin_agente → guardia_salida) | `graph.get_graph().draw_mermaid()` + SVG |
| `08-arquitectura.svg` | arquitectura A2A de todos los agentes (2 equipos por Cloudflare) | diagrama del grupo |
| `09-diagramas.md` | índice de los diagramas (mermaid auténtico + SVG) | — |
| `10-interop-puente-mac.md` | interoperabilidad A2A: puente al formato clásico (para Gustavo) | `uv run python -m src.puente_a2a.servidor` + túnel |

> Mientras no existan, el empaquetado las marca como faltantes (no bloquea).
