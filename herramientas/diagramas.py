#!/usr/bin/env python3
"""Genera diagramas.html con los diagramas de los agentes del Taller 05.

- El grafo interno de cada agente se saca del CÓDIGO real (graph.get_graph().draw_mermaid()),
  ejecutando el Python del .venv de cada proyecto. Si cambias herramientas o el grafo, vuelve a correrlo.
- La arquitectura A2A (notebook/supervisor, servidores, túneles) va escrita a mano en Mermaid.

Uso:  python herramientas/diagramas.py   →   xdg-open docs/diagramas.html
"""
import html
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent  # taller1/
PROYECTOS = [
    ("Agente Fabio · bioinformática", "mi-agente", "agente_fabio", 2025),
    ("ProteinMAN · IA y Data Science aplicada a bioinformática", "segundo-agente", "proteinman", 2026),
]
CODIGO = "from src.agente_viajes.graph import graph; print(graph.get_graph().draw_mermaid())"


def mermaid_de(carpeta: str) -> str:
    proyecto = RAIZ / "entrega" / carpeta
    salida = subprocess.run([str(proyecto / ".venv/bin/python"), "-c", CODIGO], cwd=proyecto,
                            capture_output=True, text=True, check=True)
    return salida.stdout.strip()


ARQUITECTURA = """flowchart LR
  subgraph PC["Tu computador (Debian)"]
    direction LR
    NB["Notebook a2a-test.ipynb<br/>preguntar.py · chat.html"]
    SUP{{"Supervisor<br/>Gemini + Decision<br/>(lee las tarjetas)"}}
    subgraph S1["langgraph dev :2025"]
      F["Agente Fabio<br/>grafo agente_fabio"]
      FT[("consultar_mis_apuntes")]
    end
    subgraph S2["langgraph dev :2026"]
      E["ProteinMAN<br/>grafo proteinman"]
      ET[("recomendar_tecnica · metricas_recomendadas<br/>elegir_modelo · consultar_modelos (SQLite)")]
    end
    NB --> SUP
    SUP -- "A2A message/send" --> F
    SUP -- "A2A message/send" --> E
    F --- FT
    E --- ET
  end
  CF1(["Túnel Cloudflare<br/>https://….trycloudflare.com"]) --> F
  CF2(["Túnel Cloudflare<br/>https://….trycloudflare.com"]) --> E
  COMP["Compañeros<br/>(su notebook / chat.html)"] -- "A2A por internet" --> CF1
  COMP -- "A2A por internet" --> CF2
  G[["Gemini API"]]
  F -. "LLM" .-> G
  E -. "LLM" .-> G
  SUP -. "LLM" .-> G"""

CONVERSACION = """sequenceDiagram
  autonumber
  participant N as Notebook
  participant A as Agente Fabio (:2025)
  participant B as ProteinMAN (:2026)
  N->>A: Reto + «Propón tres ideas desde tu especialidad»
  A->>A: consultar_mis_apuntes()
  A-->>N: 3 flujos (BLASTp/Swiss-Prot, HMMER/Pfam, API de UniProt)
  N->>B: Reto + ideas de Fabio + «Mejora la propuesta»
  B->>B: recomendar_tecnica · elegir_modelo · metricas_recomendadas
  B-->>N: Partición por identidad (MMseqs2) + ESM-2 + clasificador, F1 macro
  N->>A: Respuesta de ProteinMAN + «Integra un plan conjunto» (mismo contextId)
  A->>A: consultar_mis_apuntes()
  A-->>N: Plan conjunto en 4 pasos, con el autor de cada paso"""


def bloque(titulo: str, texto: str, codigo: str) -> str:
    return (f'<section><h2>{html.escape(titulo)}</h2><p>{texto}</p>'
            f'<div class="diagrama"><pre class="mermaid">{html.escape(codigo)}</pre></div></section>')


secciones = [
    bloque("Arquitectura A2A del taller",
           "Cada agente corre en su propio servidor <code>langgraph dev</code>. El notebook y el supervisor les "
           "hablan por A2A, y los túneles de Cloudflare los publican para tus compañeros.", ARQUITECTURA),
    bloque("Conversación de tres turnos (A → B → A)",
           "El notebook lleva los mensajes de un agente al otro. Fabio conserva su <code>contextId</code> "
           "entre el turno 1 y el 3, así recuerda su propuesta.", CONVERSACION),
]
for titulo, carpeta, grafo, puerto in PROYECTOS:
    secciones.append(bloque(
        f"Grafo interno · {titulo}",
        f"Generado desde el código (<code>entrega/{carpeta}/src/agente_viajes/graph.py</code>, grafo "
        f"<code>{grafo}</code>, puerto {puerto}). Es un agente ReAct: el modelo decide si llama a una "
        "herramienta, lee el resultado y vuelve a decidir, hasta responder.",
        mermaid_de(carpeta)))

pagina = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Diagramas de agentes</title>
<style>
  :root {{ --bg:#f6f7f4; --panel:#fff; --ink:#1d2320; --muted:#5f6b65; --line:#dfe3dd; }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#121614; --panel:#1a1f1c; --ink:#e6ebe7; --muted:#9aa69f; --line:#2c3430; }} }}
  :root[data-theme="dark"] {{ --bg:#121614; --panel:#1a1f1c; --ink:#e6ebe7; --muted:#9aa69f; --line:#2c3430; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 system-ui, sans-serif; }}
  main {{ max-width:1000px; margin:0 auto; padding:16px; }}
  h1 {{ font-size:20px; margin:8px 0 4px; }} h2 {{ font-size:16px; margin:0 0 4px; }}
  p {{ color:var(--muted); margin:0 0 10px; }}
  section {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px; margin:14px 0; }}
  .diagrama {{ overflow-x:auto; background:#fff; border-radius:8px; padding:8px; }}
  code {{ font-size:13px; }}
</style>
</head>
<body>
<main>
  <h1>Diagramas de los agentes · Taller 05</h1>
  <p>Generado por <code>herramientas/diagramas.py</code>. Los grafos internos salen del código de cada proyecto.</p>
  {''.join(secciones)}
</main>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js" integrity="sha384-WmdflGW9aGfoBdHc4rRyWzYuAjEmDwMdGdiPNacbwfGKxBW/SO6guzuQ76qjnSlr" crossorigin="anonymous"></script>
<script>
  mermaid.initialize({{ startOnLoad: true, theme: "default", securityLevel: "loose", flowchart: {{ htmlLabels: true }} }});
</script>
</body>
</html>
"""
(RAIZ / "docs" / "diagramas.html").write_text(pagina, encoding="utf-8")
print("Listo:", RAIZ / "docs" / "diagramas.html")
