# --8<-- encabezado-grupo
# Archivo: tools/monitor_web.py
# Objetivo: Backoffice WEB (navegador) del puente A2A: muestra la traza del log, con login por clave.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261112 1030
# Última modificación: 20261112 1030
# --8<-- fin-encabezado-grupo

"""Backoffice WEB del puente A2A — la misma traza que el monitor Tkinter, pero en el navegador.

Solo LEE el archivo de accesos del puente (`PUENTE_LOG` / `MONITOR_WEB_LOG`); no toca el puente ni
el túnel. Sirve una página que se autorefresca (tabla hora/IP/qué hizo/ruta/código + resumen) y un
endpoint JSON `/api/eventos`. Protegido con **HTTP Basic Auth**: usuario y clave vienen de variables
de entorno; si no hay clave configurada, NIEGA todo (no se expone sin clave).

Variables de entorno:
    MONITOR_WEB_LOG    ruta del log de accesos (def. logs/puente-acceso.log del repo)
    MONITOR_WEB_USER   usuario para el login (def. "monitor")
    MONITOR_WEB_PASS   clave para el login (OBLIGATORIA; sin ella no deja entrar a nadie)
    MONITOR_WEB_HOST   interfaz donde escuchar (def. 127.0.0.1; detrás de un proxy TLS)
    MONITOR_WEB_PORT   puerto (def. 8793)
    MONITOR_WEB_TITULO nombre del agente para el encabezado (def. PUENTE_GRAFO o agente_ezequiel)

Uso:
    MONITOR_WEB_PASS=xxxx uv run python tools/monitor_web.py
"""
from __future__ import annotations

import hmac
import html
import json
import os
import re
from base64 import b64decode
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LOG = Path(os.environ.get("MONITOR_WEB_LOG") or os.environ.get("PUENTE_LOG")
           or (RAIZ / "logs" / "puente-acceso.log"))
USUARIO = os.environ.get("MONITOR_WEB_USER", "monitor")
CLAVE = os.environ.get("MONITOR_WEB_PASS", "")
HOST = os.environ.get("MONITOR_WEB_HOST", "127.0.0.1")
PORT = int(os.environ.get("MONITOR_WEB_PORT", "8793"))
TITULO = os.environ.get("MONITOR_WEB_TITULO") or os.environ.get("PUENTE_GRAFO") or "agente_ezequiel"

_RE = re.compile(r'^(?P<ts>\S+)\t(?P<ip>[^\t]+)\t"(?P<metodo>\S+)\s+(?P<ruta>\S+)[^"]*"\s+(?P<cod>\d{3})')


def _interpretar(metodo: str, ruta: str) -> str:
    if ruta.startswith("/.well-known/agent-card.json"):
        return "📇 Leyó la ficha (descubrimiento)"
    if metodo == "POST" and ruta == "/":
        return "💬 Envió una consulta (message/send)"
    if ruta.startswith("/ok"):
        return "💚 Health check"
    return f"{metodo} {ruta}"


def _clase(metodo: str, ruta: str) -> str:
    if metodo == "POST" and ruta == "/":
        return "consulta"
    if ruta.startswith("/.well-known"):
        return "ficha"
    return ""


def _leer_eventos(maximo: int = 1000) -> list[dict]:
    """Objetivo: parsear las últimas líneas del log a una lista de eventos (dict). Salida: list."""
    eventos: list[dict] = []
    try:
        if LOG.exists():
            lineas = LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-maximo:]
            for ln in lineas:
                m = _RE.match(ln)
                if not m:
                    continue
                eventos.append({
                    "ts": m["ts"], "ip": m["ip"], "metodo": m["metodo"], "ruta": m["ruta"],
                    "cod": m["cod"], "que": _interpretar(m["metodo"], m["ruta"]),
                    "clase": _clase(m["metodo"], m["ruta"]),
                })
    except Exception:  # noqa: BLE001 - nunca romper el servidor
        pass
    return eventos


PAGINA = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Backoffice · __TITULO__</title>
<style>
 :root{color-scheme:light}
 body{margin:0;font:14px/1.4 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:#f4f6fa;color:#1f2a3a}
 header{padding:14px 18px;background:#fff;border-bottom:1px solid #e3e8f0}
 h1{margin:0;font-size:18px}
 .sub{color:#5a6b82;margin-top:4px}
 .resumen{margin:10px 18px;padding:10px 14px;background:#eafaf1;border:1px solid #bfe6cd;border-radius:8px;color:#176b3a;font-weight:600}
 table{width:calc(100% - 36px);margin:0 18px 24px;border-collapse:collapse;background:#fff;border:1px solid #e3e8f0;border-radius:8px;overflow:hidden}
 th,td{padding:8px 10px;text-align:left;border-bottom:1px solid #eef1f6;font-size:13px}
 th{background:#f0f3f8;color:#3a4a60;position:sticky;top:0}
 tr.consulta{background:#eaf5ea} tr.ficha{background:#eef4fb}
 .cod{font-variant-numeric:tabular-nums}
 .wrap{overflow-x:auto}
 footer{color:#8795a8;font-size:12px;margin:0 18px 20px}
</style></head><body>
<header><h1>Accesos a __TITULO__ · backoffice web</h1>
<div class="sub">Traza del puente A2A (solo lectura). Autorefresco cada 2 s. Más reciente arriba. Horas en tu zona local.</div></header>
<div class="resumen" id="resumen">Cargando…</div>
<div class="wrap"><table id="tabla"><thead><tr>
 <th>Hora</th><th>IP del cliente</th><th>Qué hizo</th><th>Ruta</th><th>Código</th></tr></thead>
<tbody id="cuerpo"></tbody></table></div>
<footer>__LOG__</footer>
<script>
function hhmmss(iso){try{return new Date(iso).toLocaleTimeString()}catch(e){return iso}}
async function tick(){
 try{
  const r = await fetch('api/eventos',{headers:{'Accept':'application/json'}});
  if(!r.ok) return;
  const ev = await r.json();
  const cuerpo = document.getElementById('cuerpo');
  // Más reciente arriba: invertimos el orden cronológico que entrega la API.
  cuerpo.innerHTML = ev.slice().reverse().map(e=>`<tr class="${e.clase}"><td>${hhmmss(e.ts)}</td>`+
    `<td>${e.ip}</td><td>${e.que}</td><td>${e.ruta}</td><td class="cod">${e.cod}</td></tr>`).join('');
  const ips = new Set(ev.map(e=>e.ip));
  const cons = ev.filter(e=>e.clase==='consulta').length;
  const fich = ev.filter(e=>e.clase==='ficha').length;
  const ult = ev.length? (hhmmss(ev[ev.length-1].ts)+' desde '+ev[ev.length-1].ip):'—';
  document.getElementById('resumen').textContent =
    `Total accesos: ${ev.length}   ·   IPs distintas: ${ips.size}   ·   Consultas: ${cons}   ·   Fichas leídas: ${fich}   ·   Último: ${ult}`;
 }catch(e){}
}
tick(); setInterval(tick, 2000);
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "monitor-web/1.0"

    def _autorizado(self) -> bool:
        if not CLAVE:
            return False  # sin clave configurada: no se entra
        cab = self.headers.get("Authorization", "")
        if not cab.startswith("Basic "):
            return False
        try:
            usr, _, pwd = b64decode(cab[6:]).decode("utf-8", "replace").partition(":")
        except Exception:  # noqa: BLE001
            return False
        return hmac.compare_digest(usr, USUARIO) and hmac.compare_digest(pwd, CLAVE)

    def _pedir_login(self) -> None:
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Backoffice A2A"')
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Necesitas clave.\n".encode())

    def do_GET(self) -> None:  # noqa: N802
        if not self._autorizado():
            return self._pedir_login()
        ruta = self.path.split("?", 1)[0]
        if ruta in ("/", "/index.html"):
            cuerpo = (PAGINA.replace("__TITULO__", html.escape(TITULO))
                            .replace("__LOG__", html.escape(f"Log: {LOG}"))).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
        elif ruta == "/api/eventos":
            datos = json.dumps(_leer_eventos(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(datos)))
            self.end_headers()
            self.wfile.write(datos)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *a):  # silenciar el log de acceso propio
        pass


def main() -> None:
    """Objetivo: levantar el backoffice web. Salida: None (corre hasta Ctrl+C)."""
    if not CLAVE:
        print("ADVERTENCIA: MONITOR_WEB_PASS no está definida; el sitio NO dejará entrar a nadie.")
    print(f"Backoffice web en http://{HOST}:{PORT}  (log: {LOG}, usuario: {USUARIO})")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
