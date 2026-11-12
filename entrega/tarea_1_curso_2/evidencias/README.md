<!--encabezado-grupo-->
> **Archivo:** `evidencias/README.md`  
> **Objetivo:** Evidencias  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1941 · **Última modificación:** 20261112 1508
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
| `11-robustez-48-mac.md` | robustecimiento final (prompt 48): resiliencia, guardrails, auth/authz, allow-list | ronda de ataques + `tools/evidencia_robustez.py` |
| `12-backoffice-monitor-mac.svg` | el monitor Tkinter del puente mostrando accesos (quién consume el agente) | `tools/monitor_puente.py` sobre `logs/puente-acceso.log` |
| `13-interop-gustavo-mac.md` | interoperabilidad NOSOTROS → agente de Gustavo (dialecto `SendMessage`) | cliente A2A contra el túnel de Gustavo |
| `14-ronda-mac-windows-gustavo-mac.md` | ronda end-to-end Mac ↔ Windows ↔ Gustavo (3 orígenes por A2A) | `./scripts/mac_coordinador.sh "<túnel-windows>"` con el catálogo cargado |
| `15-backoffice-tomas-mac.md` | el monitor de Tomás (Windows) registra el tráfico entrante desde el Mac | `win_puente.ps1` + `win_fichas_auto.ps1` en Windows; cliente A2A desde el Mac |
| `16-e2e-gustavo-mac.md` | interop A2A end-to-end con Gustavo (para enviarle): discovery + `message/send` + guardrails + compat de método | `curl` contra la URL pública del puente + suite `pytest` de interop |
| `17-despliegue-vps.svg` | arquitectura del despliegue permanente: Apache → puente → langgraph → Gemini (VPS) | diagrama del grupo |

> Mientras no existan, el empaquetado las marca como faltantes (no bloquea).
