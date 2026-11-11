<!--encabezado-grupo-->
> **Archivo:** `evidencias/README.md`  
> **Objetivo:** Evidencias  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1941 · **Última modificación:** 20261110 2136
<!--/encabezado-grupo-->

# Evidencias

Capturas y archivos que pide la rúbrica (Paso 9). Guardar aquí con estos nombres.
Las que requieren el agente vivo necesitan `GOOGLE_API_KEY` + `uv run langgraph dev`.

| Archivo | Qué debe mostrar | Cómo producirla |
|---|---|---|
| `01-saltos.png` | el agente usa su herramienta con una pregunta de tu tema y **rechaza** una de otro tema | correr el notebook `notebooks/ezequiel_paso_a_paso.ipynb` (paso 3) o `message/send` por A2A y capturar |
| `02-ficha.json` | tu Agent Card final (descripción "sé/no hago" + skills) | `curl -s "http://127.0.0.1:2024/.well-known/agent-card.json?assistant_id=<uuid>" > evidencias/02-ficha.json` |
| `03-tunel.png` | la terminal de `cloudflared` con tu URL + la ficha vista desde fuera | `cloudflared tunnel --url http://127.0.0.1:2024` y abrir la URL/ficha |
| `04-catalogo.png` | el coordinador con los agentes de otros computadores en el catálogo | correr `notebooks/coordinador_paso_a_paso.ipynb` (paso 1) o `uv run python -m src.coordinador.graph` con `URLS_AGENTES` cargado |
| `05-ronda.png` | las 3 preguntas de la ronda con el agente elegido, el motivo y la respuesta `[Agente de …]` | `uv run python -m src.coordinador.graph` (muestra `ruta:` y `[Nombre] …`) |

> Mientras no existan, el empaquetado las marca como faltantes (no bloquea).
