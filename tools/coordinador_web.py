# --8<-- encabezado-grupo
# Archivo: tools/coordinador_web.py
# Objetivo: Web chat del COORDINADOR A2A (moderna) con panel de RUTEO al lado.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261112 1210
# Última modificación: 20261112 1508
# --8<-- fin-encabezado-grupo

"""Web chat del COORDINADOR A2A (moderna) con panel de RUTEO al lado.

El usuario escribe una pregunta; el **supervisor** (grafo LangGraph) decide a qué agente del
catálogo enviarla (Ezequiel, cocina, Tomás, Fabio, Gustavo…) y reenvía por A2A. La página muestra
la respuesta en el chat y, al lado, el **ruteo**: el agente elegido, el motivo y el camino que
recorrió (guardia_entrada → supervisor → agente_… → guardia_salida).

Solo lee/invoca el coordinador; no expone secretos. Protegido con **HTTP Basic Auth** (si hay
`COORD_WEB_PASS`); pensado para ir detrás de un proxy TLS (p. ej. `chat.etmk.cl`).

Variables de entorno:
    COORD_WEB_USER / COORD_WEB_PASS   login (sin PASS: NO deja entrar a nadie)
    COORD_WEB_HOST / COORD_WEB_PORT   interfaz y puerto (def. 127.0.0.1:8794)
    A2A_BASE / A2A_GRAFOS_LOCALES / URLS_AGENTES  catálogo del coordinador (agentes)
    GOOGLE_API_KEY                    para que el supervisor (Gemini) enrute

Uso:
    COORD_WEB_PASS=xxx uv run python tools/coordinador_web.py
"""
from __future__ import annotations

import hmac
import json
import os
import sys
import traceback
import uuid
from base64 import b64decode
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:  # el servicio puede correr fuera del raíz del repo
    sys.path.insert(0, str(RAIZ))

# Carga el .env del repo (GOOGLE_API_KEY, catálogo…) sin pisar lo que ya venga del entorno
# (systemd EnvironmentFile tiene prioridad: override=False por defecto).
try:
    from dotenv import load_dotenv  # noqa: PLC0415

    load_dotenv(RAIZ / ".env")
except Exception:  # noqa: BLE001
    pass

USUARIO = os.environ.get("COORD_WEB_USER", "coordinador")
CLAVE = os.environ.get("COORD_WEB_PASS", "")
HOST = os.environ.get("COORD_WEB_HOST", "127.0.0.1")
PORT = int(os.environ.get("COORD_WEB_PORT", "8794"))
TITULO = os.environ.get("COORD_WEB_TITULO", "Coordinador A2A")

# Import diferido del grafo (necesita GOOGLE_API_KEY al importar).
_graph = None
_catalogo = None


def _cargar():
    global _graph, _catalogo  # noqa: PLW0603
    if _graph is None:
        from langchain_core.messages import HumanMessage  # noqa: PLC0415, F401
        from src.coordinador import catalogo as _c  # noqa: PLC0415
        from src.coordinador.graph import graph as _g  # noqa: PLC0415
        _graph, _catalogo = _g, _c
    return _graph, _catalogo


def _preguntar(texto: str, thread: str) -> dict:
    from langchain_core.messages import HumanMessage  # noqa: PLC0415
    g, _ = _cargar()
    r = g.invoke({"messages": [HumanMessage(content=texto)]},
                 {"configurable": {"thread_id": thread or str(uuid.uuid4())}})
    return {
        "respuesta": r.get("respuesta", ""),
        "ruta": r.get("ruta", []),
        "elegido": r.get("elegido", ""),
        "motivo": r.get("motivo", ""),
    }


def _agentes() -> list[dict]:
    _, cat = _cargar()
    out = []
    for a in cat.construir_catalogo():
        try:
            disp = a.disponibilidad()
        except Exception:  # noqa: BLE001
            disp = "desconocido"
        try:
            nombre = a.nombre
            desc = a.descripcion
        except Exception:  # noqa: BLE001
            nombre, desc = a.graph, ""
        out.append({"nombre": nombre, "descripcion": (desc or "")[:160],
                    "disponibilidad": disp, "local": a.local})
    return out


# --- Configuración de URLs de los agentes (editable desde la web) -------------------------------
URLS_FILE = Path(os.environ.get("COORD_URLS_FILE", str(RAIZ / "logs" / "coordinador_urls.json")))
# (clave, grafo A2A, puede_ser_local): Ezequiel y Tomás corren local en el VPS; Fabio/Gustavo son remotos.
AGENTES_CFG = [
    ("ezequiel", "agente_ezequiel", True),
    ("tomas", "agente_tomas", True),
    ("fabio", "agente_fabio", False),
    ("gustavo", "agente_meteorologo", False),
]


def _cargar_config() -> dict:
    base = {k: "" for k, _, _ in AGENTES_CFG}
    try:
        base.update(json.loads(URLS_FILE.read_text("utf-8")))
    except Exception:  # noqa: BLE001
        pass
    return {k: base.get(k, "") for k, _, _ in AGENTES_CFG}


def _aplicar_config(cfg: dict) -> None:
    """Traduce la config a A2A_GRAFOS_LOCALES + URLS_AGENTES (el catálogo los lee en cada consulta)."""
    locales, remotos = ["agente_cocina"], []
    for clave, grafo, local in AGENTES_CFG:
        url = (cfg.get(clave) or "").strip().rstrip("/")
        if url:
            remotos.append(f"{url}#{grafo}")
        elif local:
            locales.append(grafo)
    os.environ["A2A_GRAFOS_LOCALES"] = ",".join(locales)
    os.environ["URLS_AGENTES"] = ",".join(remotos)


def _guardar_config(cfg: dict) -> dict:
    limpio = {}
    for k, _, _ in AGENTES_CFG:
        v = (cfg.get(k) or "").strip()
        if v and not (v.startswith("http://") or v.startswith("https://")):
            v = "https://" + v
        limpio[k] = v
    URLS_FILE.parent.mkdir(parents=True, exist_ok=True)
    URLS_FILE.write_text(json.dumps(limpio, ensure_ascii=False, indent=2), "utf-8")
    _aplicar_config(limpio)
    return limpio


PAGINA = r"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITULO__ · chat</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#0b0d13; --panel:rgba(22,25,34,.72); --panel-brd:rgba(255,255,255,.08);
  --soft:rgba(255,255,255,.05); --soft2:rgba(255,255,255,.08); --aur:.55;
  --txt:#e8eaf0; --mut:#9aa3b6; --acc1:#7c5cff; --acc2:#22d3ee; --ok:#34d399; --warn:#fbbf24; --bad:#f87171;
}
:root[data-theme="light"]{
  --bg:#eef1f8; --panel:rgba(255,255,255,.80); --panel-brd:rgba(12,18,40,.10);
  --soft:rgba(12,18,40,.045); --soft2:rgba(12,18,40,.07); --aur:.30;
  --txt:#1a2033; --mut:#5c6578; --acc1:#6d4bff; --acc2:#0ea5c4;
}
*{box-sizing:border-box}
html,body{height:100%;margin:0}
body{font-family:Inter,system-ui,sans-serif;color:var(--txt);background:var(--bg);overflow:hidden}
/* aurora de fondo */
.aurora{position:fixed;inset:-20% -10%;z-index:0;filter:blur(90px);opacity:var(--aur);pointer-events:none}
.aurora i{position:absolute;border-radius:50%;animation:float 18s ease-in-out infinite}
.aurora i:nth-child(1){width:46vw;height:46vw;left:-6vw;top:-10vw;background:radial-gradient(circle,#7c5cff,transparent 60%)}
.aurora i:nth-child(2){width:40vw;height:40vw;right:-6vw;top:6vw;background:radial-gradient(circle,#22d3ee,transparent 60%);animation-delay:-6s}
.aurora i:nth-child(3){width:38vw;height:38vw;left:30vw;bottom:-14vw;background:radial-gradient(circle,#f472b6,transparent 60%);animation-delay:-11s}
@keyframes float{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(2vw,-3vw) scale(1.08)}}

.app{position:relative;z-index:1;height:100%;display:flex;flex-direction:column;padding:16px;gap:14px}
header{display:flex;align-items:center;gap:14px}
.logo{width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,var(--acc1),var(--acc2));display:grid;place-items:center;font-size:20px;box-shadow:0 8px 24px rgba(124,92,255,.4)}
h1{font-size:19px;margin:0;font-weight:700;letter-spacing:.2px}
header .sub{color:var(--mut);font-size:12.5px;margin-top:2px}
.chips{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap;max-width:60%}
.chip{display:flex;align-items:center;gap:7px;padding:6px 11px;border-radius:999px;background:var(--panel);border:1px solid var(--panel-brd);font-size:12.5px;backdrop-filter:blur(8px)}
.chip .dot{width:8px;height:8px;border-radius:50%;background:var(--mut)}
.chip.on .dot{background:var(--ok);box-shadow:0 0 8px var(--ok)}
.chip.off .dot{background:var(--bad)}
.tbtn{width:38px;height:38px;border-radius:11px;border:1px solid var(--panel-brd);background:var(--panel);color:var(--txt);font-size:17px;cursor:pointer;backdrop-filter:blur(8px);flex:none}
.tbtn:hover{border-color:var(--acc1)}

.grid{flex:1;display:grid;grid-template-columns:1.6fr 1fr;gap:14px;min-height:0}
.card{background:var(--panel);border:1px solid var(--panel-brd);border-radius:18px;backdrop-filter:blur(14px);box-shadow:0 20px 50px rgba(0,0,0,.35);display:flex;flex-direction:column;min-height:0}
.card .hd{padding:13px 18px;border-bottom:1px solid var(--panel-brd);font-weight:600;font-size:13.5px;color:var(--mut);display:flex;align-items:center;gap:8px}

/* chat */
#chat{flex:1;overflow:auto;padding:18px;display:flex;flex-direction:column;gap:14px}
.msg{display:flex;gap:11px;max-width:86%;animation:in .3s ease}
@keyframes in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.msg .av{width:34px;height:34px;border-radius:11px;display:grid;place-items:center;font-size:17px;flex:none;background:linear-gradient(135deg,#2a2f3e,#1a1e29);border:1px solid var(--panel-brd)}
.msg .bub{padding:11px 14px;border-radius:14px;line-height:1.5;font-size:14.5px;white-space:pre-wrap;word-break:break-word}
.msg.me{align-self:flex-end;flex-direction:row-reverse}
.msg.me .bub{background:linear-gradient(135deg,var(--acc1),#5b8cff);color:#fff;border-bottom-right-radius:5px}
.msg.me .av{background:linear-gradient(135deg,var(--acc1),var(--acc2))}
.msg.bot .bub{background:var(--soft);border:1px solid var(--panel-brd);border-bottom-left-radius:5px}
.msg .who{font-size:11.5px;color:var(--mut);margin-bottom:4px}
.typing{display:flex;gap:5px;padding:4px 2px}
.typing span{width:7px;height:7px;border-radius:50%;background:var(--acc2);animation:blink 1.2s infinite}
.typing span:nth-child(2){animation-delay:.2s}.typing span:nth-child(3){animation-delay:.4s}
@keyframes blink{0%,80%,100%{opacity:.25;transform:translateY(0)}40%{opacity:1;transform:translateY(-4px)}}

.composer{display:flex;gap:10px;padding:14px;border-top:1px solid var(--panel-brd)}
.composer input{flex:1;background:var(--soft);border:1px solid var(--panel-brd);border-radius:12px;padding:12px 14px;color:var(--txt);font-size:14.5px;font-family:inherit;outline:none}
.composer input:focus{border-color:var(--acc1);box-shadow:0 0 0 3px rgba(124,92,255,.25)}
.composer button{border:0;border-radius:12px;padding:0 18px;font-weight:700;color:#fff;background:linear-gradient(135deg,var(--acc1),var(--acc2));cursor:pointer;font-size:14px}
.composer button:disabled{opacity:.5;cursor:default}

/* panel ruteo */
#ruteo{padding:18px;overflow:auto;display:flex;flex-direction:column;gap:16px}
.decide{background:linear-gradient(135deg,rgba(124,92,255,.18),rgba(34,211,238,.12));border:1px solid var(--panel-brd);border-radius:14px;padding:14px}
.decide .lbl{font-size:11.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.6px}
.decide .agente{display:flex;align-items:center;gap:10px;margin-top:6px;font-weight:700;font-size:16px}
.decide .agente .av{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;font-size:16px;background:var(--soft2)}
.decide .motivo{color:var(--mut);font-size:13px;margin-top:8px;font-style:italic}
.steps{display:flex;flex-direction:column;gap:9px}
.step{display:flex;align-items:center;gap:11px;animation:in .35s ease both}
.step .ic{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;font-size:15px;flex:none}
.step .nm{font-size:13.5px;font-weight:600}
.step .tag{font-size:11px;color:var(--mut)}
.step .line{width:2px;height:12px;margin-left:14px;background:var(--panel-brd)}
.empty{color:var(--mut);font-size:13px;text-align:center;margin-top:30px;line-height:1.6}
code{font-family:'JetBrains Mono',monospace;font-size:12px;color:#c9d2ff}
.modal{position:fixed;inset:0;z-index:10;background:rgba(0,0,0,.5);backdrop-filter:blur(4px);display:none;place-items:center}
.modal.show{display:grid;animation:in .2s}
.sheet{width:min(92vw,470px);background:var(--panel);border:1px solid var(--panel-brd);border-radius:18px;backdrop-filter:blur(18px);padding:20px;box-shadow:0 30px 80px rgba(0,0,0,.5)}
.sheet-hd{display:flex;align-items:center;font-weight:700;font-size:16px;gap:8px}
.sheet .x{margin-left:auto;background:none;border:0;color:var(--mut);font-size:24px;cursor:pointer;line-height:1}
.sheet .hint{color:var(--mut);font-size:12.5px;line-height:1.55;margin:8px 0 16px}
.sheet label{display:block;font-size:13px;font-weight:600;margin-bottom:12px}
.sheet input{width:100%;margin-top:5px;background:var(--soft);border:1px solid var(--panel-brd);border-radius:10px;padding:10px 12px;color:var(--txt);font-size:13.5px;font-family:inherit;outline:none}
.sheet input:focus{border-color:var(--acc1);box-shadow:0 0 0 3px rgba(124,92,255,.2)}
.sheet-ft{display:flex;gap:10px;justify-content:flex-end;margin-top:6px}
.btn-ghost{background:var(--soft);border:1px solid var(--panel-brd);color:var(--txt);border-radius:10px;padding:9px 16px;cursor:pointer;font-weight:600;font-family:inherit}
.btn-acc{background:linear-gradient(135deg,var(--acc1),var(--acc2));border:0;color:#fff;border-radius:10px;padding:9px 18px;cursor:pointer;font-weight:700;font-family:inherit}
@media(max-width:860px){.grid{grid-template-columns:1fr;grid-template-rows:1.4fr 1fr}.chips{display:none}}
</style></head>
<body>
<div class="aurora"><i></i><i></i><i></i></div>
<div class="app">
  <header>
    <div class="logo">🧭</div>
    <div>
      <h1>__TITULO__</h1>
      <div class="sub">Supervisor A2A · enruta tu pregunta al agente correcto</div>
    </div>
    <div class="chips" id="chips"></div>
    <button id="cfg" class="tbtn" title="Configurar agentes">⚙️</button>
    <button id="theme" class="tbtn" title="Cambiar tema">🌙</button>
  </header>
  <div class="grid">
    <div class="card">
      <div class="hd">💬 Chat</div>
      <div id="chat"><div class="empty">Escribe una pregunta — el supervisor la enviará al agente<br>que corresponda (Ezequiel, Tomás, Fabio, Gustavo…).</div></div>
      <form class="composer" id="form" autocomplete="off">
        <input id="inp" placeholder="¿Qué técnica uso si tengo desbalance de clases?" />
        <button id="btn" type="submit">Enviar</button>
      </form>
    </div>
    <div class="card">
      <div class="hd">🧭 Ruteo del coordinador</div>
      <div id="ruteo"><div class="empty">Aquí verás, por cada pregunta, a qué<br>agente enrutó el supervisor y el camino<br>que recorrió.</div></div>
    </div>
  </div>
</div>
<div id="modal" class="modal">
  <div class="sheet">
    <div class="sheet-hd">⚙️ Configurar agentes <button id="cfgX" class="x">&times;</button></div>
    <p class="hint">Pega la URL (túnel/endpoint) de cada agente. Para <b>Ezequiel</b> y <b>Tomás</b>,
      déjalo <b>vacío</b> para usar el que corre <b>local</b> en este VPS.</p>
    <label>🤖 Ezequiel<input id="u_ezequiel" placeholder="vacío = local (agente_ezequiel)"></label>
    <label>🧘 Tomás<input id="u_tomas" placeholder="vacío = local (agente_tomas)"></label>
    <label>🧬 Fabio<input id="u_fabio" placeholder="https://…trycloudflare.com"></label>
    <label>⛅ Gustavo<input id="u_gustavo" placeholder="https://…trycloudflare.com"></label>
    <div class="sheet-ft"><button id="cfgCancel" class="btn-ghost">Cancelar</button><button id="cfgSave" class="btn-acc">Guardar</button></div>
  </div>
</div>
<script>
const thread = (sessionStorage.getItem('coord_thread') || (()=>{const t=crypto.randomUUID();sessionStorage.setItem('coord_thread',t);return t})());
const chat = document.getElementById('chat'), ruteo = document.getElementById('ruteo');

// --- tema dark/light (persistente) ---
const root=document.documentElement, tbtn=document.getElementById('theme');
if(localStorage.getItem('coord_theme')==='light')root.setAttribute('data-theme','light');
function pintarTema(){tbtn.textContent = root.getAttribute('data-theme')==='light' ? '☀️' : '🌙';}
tbtn.addEventListener('click',()=>{
  const light = root.getAttribute('data-theme')!=='light';
  if(light)root.setAttribute('data-theme','light'); else root.removeAttribute('data-theme');
  localStorage.setItem('coord_theme', light?'light':'dark'); pintarTema();
});
pintarTema();

function meta(n){
  n=(n||'').toLowerCase();
  if(n.includes('ezequiel'))return{e:'🤖',c:'#7c5cff'};
  if(n.includes('cocina'))return{e:'🍲',c:'#fb923c'};
  if(n.includes('tomás')||n.includes('tomas')||n.includes('reiki'))return{e:'🧘',c:'#34d399'};
  if(n.includes('fabio'))return{e:'🧬',c:'#2dd4bf'};
  if(n.includes('meteor')||n.includes('clima')||n.includes('gustavo'))return{e:'⛅',c:'#22d3ee'};
  return{e:'🛰️',c:'#9aa3b6'};
}
const PASOS={
  'guardia_entrada':{i:'🛡️',t:'Guardia de entrada',c:'#fbbf24'},
  'guardia_entrada:bloqueado':{i:'🛑',t:'Bloqueado (guardrail)',c:'#f87171'},
  'supervisor':{i:'🧭',t:'Supervisor (decide)',c:'#7c5cff'},
  'agente_local':{i:'🏠',t:'Agente local',c:'#34d399'},
  'agente_remoto':{i:'🌐',t:'Agente remoto',c:'#22d3ee'},
  'agente_no_disponible':{i:'⚠️',t:'Agente no disponible',c:'#fb923c'},
  'no_autorizado':{i:'🔒',t:'No autorizado',c:'#f87171'},
  'sin_agente':{i:'🤷',t:'Sin agente',c:'#9aa3b6'},
  'guardia_salida':{i:'🛡️',t:'Guardia de salida',c:'#fbbf24'},
};
function burbuja(cls, texto, nombre){
  if(chat.querySelector('.empty'))chat.querySelector('.empty').remove();
  const m=document.createElement('div');m.className='msg '+cls;
  const av=document.createElement('div');av.className='av';
  const bub=document.createElement('div');bub.className='bub';
  if(cls==='me'){av.textContent='🧑';bub.textContent=texto;}
  else{const mt=meta(nombre);av.textContent=mt.e;av.style.background='linear-gradient(135deg,'+mt.c+',rgba(255,255,255,.05))';
       if(nombre){const w=document.createElement('div');w.className='who';w.textContent=nombre;bub.appendChild(w);}
       bub.appendChild(document.createTextNode(texto));}
  m.appendChild(av);m.appendChild(bub);chat.appendChild(m);chat.scrollTop=chat.scrollHeight;return bub;
}
function typing(){
  if(chat.querySelector('.empty'))chat.querySelector('.empty').remove();
  const m=document.createElement('div');m.className='msg bot';m.id='typing';
  m.innerHTML='<div class="av">🧭</div><div class="bub"><div class="typing"><span></span><span></span><span></span></div></div>';
  chat.appendChild(m);chat.scrollTop=chat.scrollHeight;
}
function pintarRuteo(d){
  ruteo.innerHTML='';
  const mt=meta(d.elegido);
  const dec=document.createElement('div');dec.className='decide';
  const elegido = d.elegido && d.elegido!=='ninguno' ? d.elegido : 'ninguno (sin agente)';
  dec.innerHTML='<div class="lbl">Agente elegido por el supervisor</div>'+
    '<div class="agente"><span class="av" style="background:linear-gradient(135deg,'+mt.c+',rgba(255,255,255,.08))">'+mt.e+'</span>'+elegido+'</div>'+
    (d.motivo?'<div class="motivo">«'+d.motivo+'»</div>':'');
  ruteo.appendChild(dec);
  const steps=document.createElement('div');steps.className='steps';
  (d.ruta||[]).forEach((p,idx)=>{
    const info=PASOS[p]||{i:'•',t:p,c:'#9aa3b6'};
    const s=document.createElement('div');s.className='step';s.style.animationDelay=(idx*0.08)+'s';
    s.innerHTML='<span class="ic" style="background:'+info.c+'22;border:1px solid '+info.c+'55">'+info.i+'</span>'+
      '<div><div class="nm">'+info.t+'</div><div class="tag"><code>'+p+'</code></div></div>';
    steps.appendChild(s);
    if(idx<(d.ruta.length-1)){const l=document.createElement('div');l.className='line';steps.appendChild(l);}
  });
  ruteo.appendChild(steps);
}
async function cargarChips(){
  try{
    const r=await fetch('api/agentes');if(!r.ok)return;const ags=await r.json();
    document.getElementById('chips').innerHTML=ags.map(a=>{
      const mt=meta(a.nombre);const on=a.disponibilidad==='disponible';
      return '<div class="chip '+(on?'on':(a.disponibilidad==='no_disponible'?'off':''))+'"><span class="dot"></span>'+mt.e+' '+a.nombre+'</div>';
    }).join('');
  }catch(e){}
}
document.getElementById('form').addEventListener('submit', async(e)=>{
  e.preventDefault();
  const inp=document.getElementById('inp'),btn=document.getElementById('btn');
  const texto=inp.value.trim();if(!texto)return;
  inp.value='';btn.disabled=true;
  burbuja('me',texto);typing();
  try{
    const r=await fetch('api/preguntar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({texto,thread})});
    const d=await r.json();
    document.getElementById('typing')?.remove();
    burbuja('bot', d.respuesta || d.error || '(sin respuesta)', d.elegido);
    pintarRuteo(d);
  }catch(err){
    document.getElementById('typing')?.remove();
    burbuja('bot','Error de conexión: '+err);
  }finally{btn.disabled=false;inp.focus();}
});
// --- configuración de URLs de agentes ---
const modal=document.getElementById('modal'), CLAVES=['ezequiel','tomas','fabio','gustavo'];
function abrirCfg(){
  fetch('api/config').then(r=>r.json()).then(c=>{
    CLAVES.forEach(k=>document.getElementById('u_'+k).value=c[k]||'');
    modal.classList.add('show');
  }).catch(()=>modal.classList.add('show'));
}
function cerrarCfg(){modal.classList.remove('show');}
document.getElementById('cfg').addEventListener('click',abrirCfg);
document.getElementById('cfgX').addEventListener('click',cerrarCfg);
document.getElementById('cfgCancel').addEventListener('click',cerrarCfg);
modal.addEventListener('click',e=>{if(e.target===modal)cerrarCfg();});
document.getElementById('cfgSave').addEventListener('click',()=>{
  const body={};CLAVES.forEach(k=>body[k]=document.getElementById('u_'+k).value.trim());
  const b=document.getElementById('cfgSave');b.disabled=true;b.textContent='Guardando…';
  fetch('api/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
   .then(r=>r.json()).then(()=>{cerrarCfg();cargarChips();})
   .catch(()=>{}).finally(()=>{b.disabled=false;b.textContent='Guardar';});
});

cargarChips();setInterval(cargarChips,30000);
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "coordinador-web/1.0"

    def _ok(self) -> bool:
        if not CLAVE:
            return False
        cab = self.headers.get("Authorization", "")
        if not cab.startswith("Basic "):
            return False
        try:
            usr, _, pwd = b64decode(cab[6:]).decode("utf-8", "replace").partition(":")
        except Exception:  # noqa: BLE001
            return False
        return hmac.compare_digest(usr, USUARIO) and hmac.compare_digest(pwd, CLAVE)

    def _login(self) -> None:
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Coordinador A2A"')
        self.end_headers()
        self.wfile.write(b"Necesitas clave.\n")

    def _json(self, codigo: int, cuerpo: dict) -> None:
        datos = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):  # noqa: N802
        if not self._ok():
            return self._login()
        ruta = self.path.split("?", 1)[0]
        if ruta in ("/", "/index.html"):
            cuerpo = PAGINA.replace("__TITULO__", TITULO).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
        elif ruta == "/api/agentes":
            try:
                self._json(200, _agentes())  # type: ignore[arg-type]
            except Exception:  # noqa: BLE001
                self._json(200, [])
        elif ruta == "/api/config":
            self._json(200, _cargar_config())
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        if not self._ok():
            return self._login()
        ruta = self.path.split("?", 1)[0]
        try:
            largo = int(self.headers.get("Content-Length", 0) or 0)
            payload = json.loads(self.rfile.read(largo) or b"{}")
        except Exception:  # noqa: BLE001
            return self._json(400, {"error": "cuerpo inválido"})
        if ruta == "/api/config":
            return self._json(200, {"ok": True, "config": _guardar_config(payload)})
        if ruta != "/api/preguntar":
            return self._json(404, {"error": "not found"})
        try:
            texto = (payload.get("texto") or "").strip()
            if not texto:
                return self._json(400, {"error": "pregunta vacía"})
            self._json(200, _preguntar(texto, payload.get("thread", "")))
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            self._json(200, {"respuesta": "", "ruta": [], "elegido": "",
                             "error": f"error del coordinador: {exc}"})

    def log_message(self, *a):  # silencio
        pass


def main() -> None:
    """Levanta la web del coordinador."""
    if not CLAVE:
        print("ADVERTENCIA: COORD_WEB_PASS no definida; el sitio NO deja entrar a nadie.")
    _aplicar_config(_cargar_config())  # URLs guardadas → catálogo
    print(f"Coordinador web en http://{HOST}:{PORT}  (usuario: {USUARIO})")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
