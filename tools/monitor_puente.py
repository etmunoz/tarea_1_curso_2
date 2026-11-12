# --8<-- encabezado-grupo
# Archivo: tools/monitor_puente.py
# Objetivo: Backoffice de escritorio (Tkinter) para VER en vivo quién y qué accede al puente A2A.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261111 1723
# Última modificación: 20261111 2049
# --8<-- fin-encabezado-grupo

"""Backoffice de escritorio (Tkinter) para VER en vivo quién y qué accede al puente A2A.

Solo LEE el archivo de accesos del puente (`logs/puente-acceso.log`); no toca el puente ni el
túnel, así que se puede abrir mientras un compañero lo está probando. Muestra una tabla que se
va actualizando (hora, IP del cliente, qué hizo, ruta, código) y un resumen (total de accesos,
IPs distintas, cuántas fichas vs consultas, último acceso).

Admite VARIOS orígenes y un selector para cambiar entre ellos en vivo:
- Local: el archivo `logs/puente-acceso.log` de este equipo.
- Remoto (p. ej. el VPS `agente.etmk.cl`): lee el log del servidor por SSH (`tail -F`), sin
  copiar nada; necesita acceso SSH por llave al servidor.

El puente escribe ese log cuando corre con la variable `PUENTE_LOG` apuntando a un archivo
(ver `src/puente_a2a/servidor.py`).

Uso:
    uv run python tools/monitor_puente.py                 # solo origen Local
    uv run python tools/monitor_puente.py --vps           # agrega 'agente.etmk.cl (VPS)' por SSH
    uv run python tools/monitor_puente.py --remota usuario@host:/ruta/al/puente-acceso.log
    uv run python tools/monitor_puente.py --log ruta/al/puente-acceso.log

El VPS por defecto usa las variables MONITOR_VPS_SSH y MONITOR_VPS_LOG (o valores por defecto
del despliegue actual). Cambia el origen con el desplegable "Origen" arriba de la tabla.
"""
from __future__ import annotations

import argparse
import os
import queue
import re
import shlex
import subprocess
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk

RAIZ = Path(__file__).resolve().parent.parent
LOG_DEF = RAIZ / "logs" / "puente-acceso.log"

# Valores por defecto para el origen remoto --vps (del despliegue actual; override por entorno).
VPS_SSH_DEF = os.environ.get("MONITOR_VPS_SSH", "etmkuseragente@etmk.cl")
VPS_LOG_DEF = os.environ.get(
    "MONITOR_VPS_LOG",
    "/var/www/clients/client1/web1/home/etmkuseragente/tarea_1_curso_2/logs/puente-acceso.log",
)

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


class FuenteLocal:
    """Objetivo: origen de líneas desde un archivo LOCAL (lee lo nuevo por offset)."""

    def __init__(self, nombre: str, path: str | Path):
        self.nombre = nombre
        self.path = Path(path)
        self._offset = 0
        self.estado = "archivo local"

    @property
    def descripcion(self) -> str:
        return str(self.path)

    def iniciar(self) -> None:
        self._offset = 0  # al (re)seleccionar, mostrar desde el inicio

    def nuevas_lineas(self) -> list[str]:
        """Devuelve las líneas nuevas desde la última lectura."""
        out: list[str] = []
        try:
            if self.path.exists():
                tam = self.path.stat().st_size
                if tam < self._offset:   # el log se truncó/rotó
                    self._offset = 0
                with self.path.open("r", encoding="utf-8", errors="replace") as f:
                    f.seek(self._offset)
                    out = [ln.rstrip("\n") for ln in f.readlines()]
                    self._offset = f.tell()
                self.estado = "archivo local"
            else:
                self.estado = "archivo no encontrado aún"
        except Exception as exc:  # noqa: BLE001 - el monitor nunca debe caerse
            self.estado = f"aviso: {exc}"
        return out

    def detener(self) -> None:
        pass


class FuenteRemota:
    """Objetivo: origen de líneas desde un log REMOTO por SSH (`tail -F`), sin copiar nada.

    Lanza `ssh <destino> tail -n 300 -F <ruta>` y un hilo lee su salida hacia una cola; el bucle
    de Tk la drena. Solo lectura; requiere acceso SSH por llave al servidor."""

    def __init__(self, nombre: str, destino: str, ruta: str):
        self.nombre = nombre
        self.destino = destino
        self.ruta = ruta
        self._q: queue.Queue[str] = queue.Queue()
        self._proc: subprocess.Popen | None = None
        self._hilo: threading.Thread | None = None
        self._parar = threading.Event()
        self.estado = "—"

    @property
    def descripcion(self) -> str:
        return f"{self.destino}:{self.ruta}"

    def iniciar(self) -> None:
        self._parar.clear()
        self.estado = "conectando…"
        cmd = [
            "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
            "-o", "ServerAliveInterval=15", "-o", "StrictHostKeyChecking=accept-new",
            self.destino, f"tail -n 300 -F {shlex.quote(self.ruta)}",
        ]
        try:
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
            )
        except Exception as exc:  # noqa: BLE001
            self.estado = f"error al lanzar ssh: {exc}"
            return
        self._hilo = threading.Thread(target=self._leer, daemon=True)
        self._hilo.start()

    def _leer(self) -> None:
        proc = self._proc
        if not proc or not proc.stdout:
            return
        self.estado = "conectado (SSH)"
        try:
            for linea in proc.stdout:
                if self._parar.is_set():
                    break
                self._q.put(linea.rstrip("\n"))
        except Exception:  # noqa: BLE001
            pass
        finally:
            if not self._parar.is_set():
                err = ""
                try:
                    err = (proc.stderr.read() or "").strip().splitlines()[-1][:140] if proc.stderr else ""
                except Exception:  # noqa: BLE001
                    err = ""
                self.estado = f"desconectado — {err}" if err else "desconectado (ssh terminó)"

    def nuevas_lineas(self) -> list[str]:
        out: list[str] = []
        try:
            while True:
                out.append(self._q.get_nowait())
        except queue.Empty:
            pass
        return out

    def detener(self) -> None:
        self._parar.set()
        if self._proc:
            try:
                self._proc.terminate()
            except Exception:  # noqa: BLE001
                pass
        self._proc = None


class Monitor(tk.Tk):
    """Objetivo: ventana que refleja en vivo los accesos al puente, con selector de origen."""

    def __init__(self, fuentes: list, captura: str | None = None, segundos: float = 3.0,
                 titulo: str | None = None):
        super().__init__()
        self.fuentes = fuentes
        self.fuente = fuentes[0]
        self.agente = titulo or os.environ.get("PUENTE_GRAFO") or "agente_ezequiel"
        self._captura = captura
        self._total = 0
        self._ips: set[str] = set()
        self._fichas = 0
        self._consultas = 0

        self.title("Backoffice · accesos al puente A2A")
        self.geometry("940x540")
        self.minsize(640, 360)

        cab = ttk.Frame(self, padding=(10, 8))
        cab.pack(fill="x")
        ttk.Label(cab, text=f"Accesos a {self.agente} (vía puente A2A)",
                  font=("-size", 13, "-weight", "bold")).pack(anchor="w")

        sel = ttk.Frame(cab)
        sel.pack(fill="x", pady=(4, 0))
        ttk.Label(sel, text="Origen:").pack(side="left")
        self._combo = ttk.Combobox(sel, state="readonly", width=34,
                                    values=[f.nombre for f in fuentes])
        self._combo.current(0)
        self._combo.pack(side="left", padx=(6, 0))
        self._combo.bind("<<ComboboxSelected>>", self._cambiar_fuente)

        self.resumen = ttk.Label(cab, text="Esperando accesos…", foreground="#555")
        self.resumen.pack(anchor="w", pady=(4, 0))
        self.lbl_origen = ttk.Label(cab, text="", foreground="#999")
        self.lbl_origen.pack(anchor="w")

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

        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self.fuente.iniciar()
        self._refrescar_origen()
        self._tic()
        if self._captura:
            self.after(int(segundos * 1000), self._auto_captura)

    def _refrescar_origen(self) -> None:
        self.lbl_origen.configure(text=f"Origen: {self.fuente.nombre}  ·  {self.fuente.descripcion}  ·  {self.fuente.estado}")

    def _reset_contadores(self) -> None:
        self._total = 0
        self._ips = set()
        self._fichas = 0
        self._consultas = 0
        self.tabla.delete(*self.tabla.get_children())
        self.resumen.configure(text="Esperando accesos…", foreground="#555")

    def _cambiar_fuente(self, _evt=None) -> None:
        """Objetivo: cambiar el origen activo (detiene el anterior, limpia la tabla, arranca el nuevo)."""
        idx = self._combo.current()
        nueva = self.fuentes[idx]
        if nueva is self.fuente:
            return
        try:
            self.fuente.detener()
        except Exception:  # noqa: BLE001
            pass
        self.fuente = nueva
        self._reset_contadores()
        self.fuente.iniciar()
        self._refrescar_origen()

    def _cerrar(self) -> None:
        for f in self.fuentes:
            try:
                f.detener()
            except Exception:  # noqa: BLE001
                pass
        self.destroy()

    def _auto_captura(self) -> None:
        """Objetivo: guardar una captura de ESTA ventana (para evidencia) con `screencapture`.
        Entradas: usa self._captura. Salida: None."""
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
        """Objetivo: traer las líneas nuevas del origen activo y agregarlas a la tabla. Cada 1s."""
        try:
            for linea in self.fuente.nuevas_lineas():
                self._agregar(linea)
        except Exception as exc:  # noqa: BLE001 - el monitor nunca debe caerse
            self.resumen.configure(text=f"(aviso leyendo el origen: {exc})")
        self._refrescar_origen()
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


def _construir_fuentes(args) -> list:
    """Objetivo: armar la lista de orígenes desde los argumentos. Salida: list[Fuente]."""
    fuentes: list = [FuenteLocal("Local", args.log)]
    for spec in args.remota:
        destino, _, ruta = spec.partition(":")
        if not destino or not ruta:
            print(f"· --remota ignorada (formato usuario@host:/ruta): {spec}")
            continue
        nombre = destino.split("@")[-1]
        fuentes.append(FuenteRemota(nombre, destino, ruta))
    if args.vps:
        fuentes.append(FuenteRemota("agente.etmk.cl (VPS)", VPS_SSH_DEF, VPS_LOG_DEF))
    return fuentes


def main() -> None:
    """Objetivo: CLI del monitor. Entradas: --log, --remota, --vps, --captura, --titulo. Salida: None."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--log", default=str(LOG_DEF), help="Ruta del archivo de accesos del puente (origen Local).")
    ap.add_argument("--remota", action="append", default=[], metavar="usuario@host:/ruta",
                    help="Agrega un origen remoto por SSH (tail -F del log). Repetible.")
    ap.add_argument("--vps", action="store_true",
                    help="Agrega el origen 'agente.etmk.cl (VPS)' (MONITOR_VPS_SSH / MONITOR_VPS_LOG).")
    ap.add_argument("--captura", default=None, help="Si se indica, guarda un PNG de la ventana (evidencia).")
    ap.add_argument("--segundos", type=float, default=3.0, help="Segundos antes de capturar.")
    ap.add_argument("--titulo", default=None,
                    help="Nombre del agente a mostrar en el encabezado (def. PUENTE_GRAFO o agente_ezequiel).")
    args = ap.parse_args()
    Monitor(_construir_fuentes(args), captura=args.captura, segundos=args.segundos,
            titulo=args.titulo).mainloop()


if __name__ == "__main__":
    main()
