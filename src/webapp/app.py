# --8<-- encabezado-grupo
# Archivo: src/webapp/app.py
# Objetivo: App web simple para probar los agentes: uno a uno (A2A) y vía el coordinador.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2140
# Última modificación: 20261111 1343
# --8<-- fin-encabezado-grupo

"""App web simple para probar los agentes: uno a uno (A2A) y vía el coordinador.

La MISMA app sirve en ambos equipos; su configuración (qué agentes son locales y cuáles
remotos) sale del entorno, así la app del Mac y la del Windows muestran lo suyo:

  A2A_BASE            langgraph dev local (def. http://127.0.0.1:2024)
  A2A_GRAFOS_LOCALES  grafos locales (def. agente_viajes,agente_ezequiel,agente_cocina,agente_tomas)
  URLS_AGENTES        agentes remotos (url#grafo, separados por comas) — el otro equipo
  APP_ROL             etiqueta que muestra la app (def. "nodo local")
  WEBAPP_PORT         puerto (def. 8800)

Sin dependencias extra: usa la librería estándar. El coordinador y el A2A reutilizan
`src.coordinador`.
"""
from __future__ import annotations

import json
import os
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from dotenv import load_dotenv

from src.coordinador import a2a
from src.coordinador.catalogo import construir_catalogo

load_dotenv()

ROL = os.environ.get("APP_ROL", "nodo local")
PORT = int(os.environ.get("WEBAPP_PORT", "8800"))


def _agentes() -> list[dict]:
    """Objetivo: listar los agentes del catálogo para el selector de la app.
    Entradas: ninguna. Salida: list[dict] — {nombre, graph, base_url, tipo: local|remoto}."""
    salida = []
    for ag in construir_catalogo():
        salida.append({"nombre": ag.nombre, "graph": ag.graph, "base_url": ag.base_url,
                       "tipo": "local" if "127.0.0.1" in ag.base_url or "localhost" in ag.base_url else "remoto"})
    return salida


def _preguntar(destino: str, texto: str, context_id: str) -> dict:
    """Objetivo: responder una consulta, vía el coordinador o directo a un agente por A2A.
    Entradas: destino (str) '__coordinador__' o 'base_url#graph'; texto (str); context_id (str).
    Salida: dict — {respuesta, ruta}."""
    if destino == "__coordinador__":
        from langchain_core.messages import HumanMessage  # import tardío (requiere key)

        from src.coordinador.graph import graph
        r = graph.invoke({"messages": [HumanMessage(content=texto)]},
                         {"configurable": {"thread_id": context_id}})
        return {"respuesta": r.get("respuesta", ""), "ruta": " → ".join(r.get("ruta", []))}
    # destino = "base_url#graph" — el contextId de A2A debe ser un UUID.
    base_url, graph_id = destino.split("#", 1)
    try:
        uuid.UUID(str(context_id))
        cid = context_id
    except (ValueError, TypeError):
        cid = str(uuid.uuid5(uuid.NAMESPACE_URL, str(context_id)))  # UUID estable por conversación
    return {"respuesta": a2a.enviar_mensaje(base_url, graph_id, texto, cid), "ruta": "directo"}


PAGINA = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agentes · __ROL__</title>
<style>
 :root{color-scheme:light dark}
 body{font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;max-width:760px;margin:0 auto;padding:18px}
 h1{font-size:19px;margin:0 0 2px} .rol{color:#7c3aed;font-weight:600}
 .sub{color:#666;margin:0 0 14px;font-size:13px}
 select,textarea,button{font:inherit;border-radius:10px;border:1px solid #8884;padding:9px}
 select{width:100%} textarea{width:100%;min-height:70px;margin:8px 0}
 button{background:#7c3aed;color:#fff;border:0;padding:9px 16px;cursor:pointer}
 button:disabled{opacity:.5}
 .msg{border:1px solid #8883;border-radius:12px;padding:10px 12px;margin:10px 0;white-space:pre-wrap}
 .meta{font-size:12px;color:#888;margin-bottom:4px}
 .yo{background:#7c3aed14}
</style></head><body>
<h1>Agentes · <span class="rol">__ROL__</span></h1>
<p class="sub">Elige un agente para probarlo solo (A2A), o <b>Coordinador</b> para ver el ruteo.</p>
<select id="destino"></select>
<textarea id="texto" placeholder="Escribe tu pregunta…"></textarea>
<button id="enviar" onclick="enviar()">Enviar</button>
<div id="chat"></div>
<script>
let ctx = {};
async function cargar(){
  const r = await fetch('api/agentes'); const ags = await r.json();
  const s = document.getElementById('destino');
  s.innerHTML = '<option value="__coordinador__">🧭 Coordinador (enruta automáticamente)</option>';
  for (const a of ags){
    const v = a.base_url + '#' + a.graph;
    s.innerHTML += `<option value="${v}">${a.tipo==='local'?'🟢':'🔵'} ${a.nombre} · ${a.tipo}</option>`;
  }
}
function add(cls, meta, txt){
  const d = document.getElementById('chat');
  d.insertAdjacentHTML('afterbegin', `<div class="msg ${cls}"><div class="meta">${meta}</div>${txt}</div>`);
}
async function enviar(){
  const destino = document.getElementById('destino').value;
  const texto = document.getElementById('texto').value.trim();
  if(!texto) return;
  if(!ctx[destino]) ctx[destino] = crypto.randomUUID();
  add('yo', 'tú', texto);
  document.getElementById('texto').value='';
  const b = document.getElementById('enviar'); b.disabled=true; b.textContent='…';
  try{
    const r = await fetch('api/preguntar', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({destino, texto, context_id: ctx[destino]})});
    const j = await r.json();
    add('', (j.ruta?('ruta: '+j.ruta):'')+ (j.error?'ERROR':''), j.error || j.respuesta);
  }catch(e){ add('', 'error', String(e)); }
  b.disabled=false; b.textContent='Enviar';
}
cargar();
</script></body></html>""".replace("__ROL__", ROL)


class Handler(BaseHTTPRequestHandler):
    """Objetivo: handler HTTP de la app web (sirve la página y los endpoints /api/*)."""

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        """Objetivo: enviar una respuesta HTTP.
        Entradas: code (int), body (str|bytes), ctype (str). Salida: None."""
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802
        """Objetivo: servir la página (/) y el listado de agentes (/api/agentes).
        Entradas: usa self.path. Salida: None (escribe la respuesta)."""
        if self.path in ("/", "/index.html"):
            self._send(200, PAGINA, "text/html; charset=utf-8")
        elif self.path == "/api/agentes":
            try:
                self._send(200, json.dumps(_agentes(), ensure_ascii=False))
            except Exception as exc:  # noqa: BLE001
                self._send(200, json.dumps([{"nombre": f"(error: {exc})", "graph": "", "base_url": "", "tipo": "local"}]))
        else:
            self._send(404, json.dumps({"error": "no encontrado"}))

    def do_POST(self):  # noqa: N802
        """Objetivo: atender /api/preguntar (JSON {destino, texto, context_id}) y responder.
        Entradas: cuerpo JSON de la petición. Salida: None (escribe JSON {respuesta, ruta} o {error})."""
        if self.path != "/api/preguntar":
            self._send(404, json.dumps({"error": "no encontrado"}))
            return
        n = int(self.headers.get("Content-Length", 0) or 0)
        try:
            p = json.loads(self.rfile.read(n) or b"{}")
            res = _preguntar(p.get("destino", ""), p.get("texto", ""), p.get("context_id") or uuid.uuid4().hex)
            self._send(200, json.dumps(res, ensure_ascii=False))
        except Exception as exc:  # noqa: BLE001
            self._send(200, json.dumps({"error": str(exc)}, ensure_ascii=False))

    def log_message(self, *_a):  # noqa: D401 - silencioso (sin logs por request)
        """Objetivo: silenciar el log por request. Entradas: ignoradas. Salida: None."""
        pass


def main() -> None:
    """Objetivo: arrancar el servidor web y abrir el navegador.
    Entradas: ninguna (lee ROL/PORT del entorno). Salida: None (bloquea hasta Ctrl+C)."""
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"App web «{ROL}» en {url}  (Ctrl+C para parar)")
    try:
        import webbrowser
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    except Exception:  # noqa: BLE001
        pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nparando…")
        srv.shutdown()


if __name__ == "__main__":
    main()
