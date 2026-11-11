# --8<-- encabezado-grupo
# Archivo: tools/monitor_puente.py
# Objetivo: Backoffice de escritorio (Tkinter) para VER en vivo quién y qué accede al puente A2A.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 1723
# Última modificación: 20261111 1857
# --8<-- fin-encabezado-grupo

"""Backoffice de escritorio (Tkinter) para VER en vivo quién y qué accede al puente A2A.

Solo LEE el archivo de accesos del puente (`logs/puente-acceso.log`); no toca el puente ni el
túnel, así que se puede abrir mientras un compañero lo está probando. Muestra una tabla que se
va actualizando (hora, IP del cliente, qué hizo, ruta, código) y un resumen (total de accesos,
IPs distintas, cuántas fichas vs consultas, último acceso).

El puente escribe ese log cuando corre con la variable `PUENTE_LOG` apuntando a un archivo
(ver `src/puente_a2a/servidor.py`).

Uso:
    uv run python tools/monitor_puente.py
    uv run python tools/monitor_puente.py --log ruta/al/puente-acceso.log
"""
from __future__ import annotations

import argparse
import re
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk

RAIZ = Path(__file__).resolve().parent.parent
LOG_DEF = RAIZ / "logs" / "puente-acceso.log"

# Línea del log: "<ts>\t<ip>\t\"GET /ruta HTTP/1.1\" 200 -"
_RE = re.compile(r'^(?P<ts>\S+)\t(?P<ip>[^\t]+)\t"(?P<metodo>\S+)\s+(?P<ruta>\S+)[^"]*"\s+(?P<cod>\d{3})')


def _interpretar(metodo: str, ruta: str) -> str:
    """Objetivo: traducir método+ruta a 'qué hizo' en lenguaje claro. Salida: str."""
    if ruta.startswith("/.well-known/agent-card.json"):
        return "📇 Leyó la ficha (descubrimiento)"
    if metodo == "POST" and ruta == "/":
        return "💬 Envió una consulta (message/send)"
    if ruta.startswith("/ok"):
        return "💚 Health check"
    return f"{metodo} {ruta}"


def _hora(ts: str) -> str:
    """Objetivo: hora local legible desde un ISO-8601 UTC. Salida: str (HH:MM:SS) o el ts crudo."""
    try:
        return datetime.fromisoformat(ts).astimezone().strftime("%H:%M:%S")
    except ValueError:
        return ts


class Monitor(tk.Tk):
    """Objetivo: ventana que refleja en vivo los accesos al puente leyendo su log."""

    def __init__(self, log: Path, captura: str | None = None, segundos: float = 3.0):
        super().__init__()
        self.log = log
        self._captura = captura
        self._offset = 0
        self._total = 0
        self._ips: set[str] = set()
        self._fichas = 0
        self._consultas = 0

        self.title("Backoffice · accesos al puente A2A")
        self.geometry("920x520")
        self.minsize(640, 360)

        cab = ttk.Frame(self, padding=(10, 8))
        cab.pack(fill="x")
        ttk.Label(cab, text="Accesos al Agente de Ezequiel (vía puente A2A)",
                  font=("-size", 13, "-weight", "bold")).pack(anchor="w")
        self.resumen = ttk.Label(cab, text="Esperando accesos…", foreground="#555")
        self.resumen.pack(anchor="w", pady=(2, 0))
        ttk.Label(cab, text=f"Log: {self.log}", foreground="#999").pack(anchor="w")

        cols = ("hora", "ip", "que", "ruta", "cod")
        self.tabla = ttk.Treeview(self, columns=cols, show="headings", height=16)
        for c, txt, w in [("hora", "Hora", 90), ("ip", "IP del cliente", 160),
                          ("que", "Qué hizo", 320), ("ruta", "Ruta", 250), ("cod", "Código", 70)]:
            self.tabla.heading(c, text=txt)
            self.tabla.column(c, width=w, anchor="w")
        self.tabla.tag_configure("consulta", background="#eaf5ea")
        self.tabla.tag_configure("ficha", background="#eef4fb")
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sb.set)
        self.tabla.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
        sb.pack(side="right", fill="y", pady=(0, 10), padx=(0, 10))

        self._tic()
        if self._captura:
            self.after(int(segundos * 1000), self._auto_captura)

    def _auto_captura(self) -> None:
        """Objetivo: guardar una captura de ESTA ventana (para evidencia) con `screencapture`.
        Entradas: usa self._captura. Salida: None."""
        import subprocess  # noqa: PLC0415
        self.lift()
        self.attributes("-topmost", True)
        self.update()
        x, y = self.winfo_rootx(), self.winfo_rooty()
        w, h = self.winfo_width(), self.winfo_height()
        region = f"{x},{y},{w},{h}"
        try:
            subprocess.run(["screencapture", "-x", "-R", region, self._captura], check=False)
            print(f"captura guardada: {self._captura}")
        except Exception as exc:  # noqa: BLE001
            print(f"no se pudo capturar: {exc}")
        self.attributes("-topmost", False)

    def _tic(self) -> None:
        """Objetivo: leer las líneas nuevas del log y agregarlas a la tabla. Reprograma cada 1s."""
        try:
            if self.log.exists():
                tam = self.log.stat().st_size
                if tam < self._offset:   # el log se truncó/rotó
                    self._offset = 0
                with self.log.open("r", encoding="utf-8", errors="replace") as f:
                    f.seek(self._offset)
                    nuevas = f.readlines()
                    self._offset = f.tell()
                for linea in nuevas:
                    self._agregar(linea.rstrip("\n"))
        except Exception as exc:  # noqa: BLE001 - el monitor nunca debe caerse
            self.resumen.configure(text=f"(aviso leyendo el log: {exc})")
        self.after(1000, self._tic)

    def _agregar(self, linea: str) -> None:
        """Objetivo: parsear una línea del log y agregarla como fila. Entradas: linea (str)."""
        m = _RE.match(linea)
        if not m:
            return
        metodo, ruta, ip = m["metodo"], m["ruta"], m["ip"]
        que = _interpretar(metodo, ruta)
        tag = "consulta" if (metodo == "POST" and ruta == "/") else \
              ("ficha" if ruta.startswith("/.well-known") else "")
        self.tabla.insert("", "end", values=(_hora(m["ts"]), ip, que, ruta, m["cod"]), tags=(tag,))
        self.tabla.yview_moveto(1.0)  # auto-scroll al último
        self._total += 1
        self._ips.add(ip)
        if tag == "consulta":
            self._consultas += 1
        elif tag == "ficha":
            self._fichas += 1
        self.resumen.configure(
            text=(f"Total accesos: {self._total}   ·   IPs distintas: {len(self._ips)}   ·   "
                  f"Consultas: {self._consultas}   ·   Fichas leídas: {self._fichas}   ·   "
                  f"Último: {_hora(m['ts'])} desde {ip}"),
            foreground="#1a7a3a")


def main() -> None:
    """Objetivo: CLI del monitor. Entradas: --log. Salida: None (abre la ventana)."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--log", default=str(LOG_DEF), help="Ruta del archivo de accesos del puente.")
    ap.add_argument("--captura", default=None, help="Si se indica, guarda un PNG de la ventana (evidencia).")
    ap.add_argument("--segundos", type=float, default=3.0, help="Segundos antes de capturar.")
    args = ap.parse_args()
    Monitor(Path(args.log), captura=args.captura, segundos=args.segundos).mainloop()


if __name__ == "__main__":
    main()
