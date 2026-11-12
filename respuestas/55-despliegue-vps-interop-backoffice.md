<!--encabezado-grupo-->
> **Archivo:** `respuestas/55-despliegue-vps-interop-backoffice.md`  
> **Objetivo:** 55 · Respuesta — Despliegue permanente en VPS (agente.etmk.cl), interop y backoffice multi-origen  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 0959 · **Última modificación:** 20261112 0959
<!--/encabezado-grupo-->

# 55 · Respuesta — Despliegue permanente en VPS (agente.etmk.cl), interop y backoffice multi-origen

Prompt: [`../prompts_ejecutados/55-despliegue-vps-interop-backoffice.md`](../prompts_ejecutados/55-despliegue-vps-interop-backoffice.md)

> **Hora:** el VPS corre en **UTC**; Santiago está en **UTC−3** (verano). Server = Santiago + 3 h.
> Los logs/backoffice están en UTC.

---

## 1. Repo "redondo" + scripts de Windows

- El repo ya estaba consistente (`aplicar_encabezados.py --check` OK, árbol limpio, sync 0/0); no
  hizo falta un commit extra de normalización (correrlo de nuevo solo movería timestamps).
- **`scripts/win_puente.ps1`** (commit `535f2c3`): gemelo de `mac_puente.sh` para que Tomás exponga
  `agente_tomas` por el puente A2A (defaults `agente_tomas`, puerto `8791`, log `logs\puente-tomas.log`).
- **`scripts/win_fichas_auto.ps1`** (commit `de88d4c`): vigilante de fichas en Windows
  (`configurar_fichas.py --vigilar`).

## 2. Backoffice cross-machine — Tomás ve el tráfico del Mac (evidencia 15)

- Se coordinó con Tomás: levantó el puente delante de `agente_tomas` + túnel + monitor Tkinter.
- Desde el Mac se consumió su agente por su túnel (`https://mid-lakes-expanded-multi.trycloudflare.com`)
  con 4 consultas de Reiki. Su monitor registró **15 accesos · 2 IPs · 5 consultas · 9 fichas**,
  con la IP del edge de Cloudflare `190.215.226.163`.
- **`evidencias/15-backoffice-tomas-mac.md`** + **`15-backoffice-tomas.png`** (captura real).
- Se hizo configurable el encabezado del monitor: **`--titulo` / `PUENTE_GRAFO`** (antes decía fijo
  "Agente de Ezequiel"; en el Windows de Tomás debe decir su agente). Commits `7458473`, `a6018f8`,
  `266364d`, `60a907b` (+ README de evidencias completado filas 11–15, entrega regenerada, PDF limpio
  mapeando glifos de caja `─│└┘` a ASCII).

## 3. Interop end-to-end con Gustavo (evidencia 16)

Dos direcciones:
- **Gustavo → nosotros:** su cliente A2A clásico consume nuestro puente por `message/send`. **Probado
  en vivo y reproducible** contra la URL pública (discovery + consulta + respuesta real). El backoffice
  registró su consumo real desde su IP `186.107.24.191` (POST / 200 + GET card).
- **Compatibilidad de método:** si su cliente manda el método `SendMessage` directo a nuestro puente →
  `-32601` (implementamos `message/send`). Nuestro cliente **sí** reintenta `SendMessage` ante `-32601`.
- Suite de interop: **17 passed** (`test_interop_sendmessage_51.py` + `test_interop_a2a.py`).
- **`evidencias/16-e2e-gustavo-mac.md`** (commit `4117cfe`), pensado para enviárselo a Gustavo (incluye
  los `curl` reproducibles).

Consulta real por el puente (ejemplo):
```
POST / {message/send: "¿Qué modelo base uso para clasificación tabular con pocos datos?"}
→ "Para datos tabulares te sugiero arrancar con Gradient Boosting (XGBoost, LightGBM, CatBoost)…"
```

## 4. Fix de robustez: contextId → UUID (hallado con el agente de Fabio)

- Fabio preguntó por su `preguntar.py` (tenía `https://https://…`, doble esquema). Su agente
  (`agente_fabio`, bioinformática: ADN/proteínas, UniProt/NCBI) es **LangGraph nativo** y exige que el
  `contextId` (= `thread_id`) sea un **UUID** (`-32602 'Invalid thread ID'` si no lo es).
- Al consumirlo con nuestro cliente se reprodujo el bug: `enviar_mensaje` usaba el `contextId` **crudo**.
  **Fix** (commit `52eba04`): ahora coacciona con `a_uuid()` para **todos** los dialectos (un UUID estable
  es válido en langgraph, clásico y SendMessage). + test de regresión. Suite completa: **147 passed, 1 skipped**.

## 5. URLs efímeras → decisión de migrar al VPS

- Los *quick tunnels* `trycloudflare.com` caducan (URL aleatoria + desconexión del edge tras horas). Se
  renovaron una vez (para Gustavo y para los compañeros), pero el problema de fondo es la estabilidad.
- Con **dominio propio (`etmk.cl`) + VPS**, se decidió **desplegar el agente en el VPS** con HTTPS
  permanente, en vez de depender del Mac + túneles.

## 6. ✅ Despliegue permanente en el VPS — `https://agente.etmk.cl`

**Infra del VPS:** Ubuntu 24.04, ISPConfig (Apache + correo + DNS ya en producción), wildcard `*.etmk.cl`
→ `69.197.134.192`.

Pasos:
1. **Acceso SSH sin root:** se creó un **Shell-User** en ISPConfig (`etmkuseragente`, usuario de sistema
   `web1`, grupo `client1`, **sin sudo**, shell `/bin/bash`, chroot `None`). Login **por llave** (clave
   pública pegada en el campo SSH-RSA del panel; la contraseña nunca pasó por el chat).
2. **Entorno:** `uv` instalado a nivel usuario (`uv 0.13.7`), repo clonado (`git clone`), `uv sync`
   (Python 3.13 + dependencias). La `GOOGLE_API_KEY` se llevó al servidor con **`scp` ejecutado por el
   usuario** (nunca se mostró en el chat), `.env` con permisos `600`, fuera del docroot público.
3. **Servicios (solo localhost):** `langgraph dev` en `127.0.0.1:2024` + **puente A2A** en
   `127.0.0.1:8790` (`PUENTE_URL_PUBLICA=https://agente.etmk.cl`, `PUENTE_LOG=…/logs/puente-acceso.log`).
   Fichas aplicadas (`agente_ezequiel`, `agente_cocina`).
4. **Publicación HTTPS:** en ISPConfig se creó el **Website `agente.etmk.cl`** con **SSL + Let's Encrypt**
   (PHP Disabled, Auto-Subdomain None) y luego la pestaña **Redirect → `proxy` → `http://127.0.0.1:8790/`**
   (Apache con `mod_proxy_http`).

**Verificación (desde internet):**
```
GET  https://agente.etmk.cl/.well-known/agent-card.json  → 200 application/json
     name: Agente de Ezequiel · url: https://agente.etmk.cl · transport: JSONRPC
POST https://agente.etmk.cl/ (message/send "clases desbalanceadas 95/5")
     → "…class weights, resampleo (SMOTE/undersampling) y métricas tipo F1/PR-AUC…"
Certificado: Let's Encrypt · CN=agente.etmk.cl · 12-nov-2026 → 10-feb-2027
```

**Arquitectura (cadena de 3 capas):**
Internet → **Apache (reverse proxy + Let's Encrypt, :443)** → **Puente A2A clásico (Python `http.server`,
`127.0.0.1:8790`, guardrails + log)** → **`langgraph dev` (uvicorn/ASGI, `127.0.0.1:2024`)** → agentes →
**Gemini**. (Respuesta a Fabio: uvicorn/ASGI es LangGraph por dentro; el endpoint que se consume es el
puente stdlib detrás de Apache — no uvicorn/WSGI en el borde.)

## 7. Raíz de la web → LinkedIn

- Vía ISPConfig (Website → Redirect → `R,L` → `https://www.linkedin.com/in/ezequielmunoz/`).
- Al principio solo **`www.etmk.cl`** redirigía; el **pelado** caía en el vhost por defecto de Apache.
  **Causa (con root):** `000-default.conf` cargaba antes (000 < 100) y heredaba el `ServerName` global
  `etmk.cl`, ganándole al vhost real. **Fix:** `a2dissite 000-default` + reload. **Ahora `etmk.cl` y
  `www.etmk.cl` redirigen a LinkedIn ✅** (302). DNS descartado (ambos al mismo IP).

## 8. Evaluación de seguridad del servidor

🔴 **Importante:** MySQL (**3306**) **expuesto a internet** (`0.0.0.0:3306`) — debería escuchar solo local.
· Muchas **actualizaciones de kernel/libc pendientes** con **reinicio requerido** (corre un kernel viejo).
🟡 **Medio:** FTP (21) abierto; POP3/IMAP en claro (110/143); panel ISPConfig (8080/8081) expuesto con cert
no confiable; SSH con contraseña habilitada.
🟢 **Bien:** **fail2ban activo** (de hecho baneó intentos fallidos durante el setup); auto-updates activadas;
Redis (6379) y Memcached (11211) **solo localhost**. — Se dejó el texto para pedirle los fixes a soporte.
Nuestro agente **no agrega exposición** (escucha solo en `127.0.0.1`, se publica por Apache). Recursos:
2 vCPU, 3.8 GB RAM, 55 GB libres.

## 9. Persistencia — del cron fallido a `systemd` (✅ resuelto, probado con reinicio)

- Primero se intentó un `~/agente_keepalive.sh` + **Cron Job de ISPConfig** (`*/5`). **No funcionaba**:
  ISPConfig lo creó como `ispc_chrooted_web2` — **chrooted y como `web2`** (usuario de otro sitio), sin
  `uv`/`curl` en el jail y con rutas de `web1` inexistentes dentro del chroot. Se descartó.
- **Solución correcta (con root):** dos servicios **`systemd`** como `web1` — `agente-langgraph.service`
  y `agente-puente.service`, ambos **`enabled`** (arrancan al bootear) y **`Restart=always`** (reviven si
  se caen). El puente espera a langgraph (`ExecStartPre`) y **reaplica las fichas** (`ExecStartPost`).
- **Probado de verdad:** tras el **reinicio** del servidor, los servicios **volvieron solos** y el público
  (`https://agente.etmk.cl`) respondió sin intervención.

## 10. Monitor Tkinter multi-origen (selector Local / VPS)

- **`tools/monitor_puente.py`** reescrito: abstracción de **orígenes** con un **selector** (Combobox
  "Origen"). `FuenteLocal` (archivo local, por offset) y `FuenteRemota` (lee el log del VPS por SSH
  `tail -F`, sin copiar nada; hilo + cola). Flags nuevos: `--vps` (usa `MONITOR_VPS_SSH`/`MONITOR_VPS_LOG`)
  y `--remota usuario@host:/ruta`. Compila OK. Uso: `uv run python tools/monitor_puente.py --vps`.

## 11. Diagrama de despliegue (evidencia 17)

- **`evidencias/17-despliegue-vps.svg`**: la cadena Apache → puente → langgraph → Gemini, con los
  consumidores (Gustavo / Fabio / Tomás / coordinador). Para compartir con los compañeros.

## 12. Acceso de administración (sudo temporal)

- Se habilitó acceso SSH por **llave** para el usuario **`administrator`** (grupo `sudo`) con
  `ssh-copy-id` (clave tecleada por el usuario, nunca en el chat).
- Como `sudo` pedía contraseña, el usuario autorizó **sudo sin clave TEMPORAL** vía un drop-in
  `/etc/sudoers.d/90-administrator-nopasswd` (validado con `visudo -c`). **A revocar al terminar**
  (`sudo rm /etc/sudoers.d/90-administrator-nopasswd`). Primero diagnóstico (lectura) y confirmación
  antes de cada cambio que tocara web/correo/reinicio.

## 13. Seguridad aplicada (con root)

- **MySQL solo local:** en `50-server.cnf` se descomentó `bind-address = 127.0.0.1` + reinicio de
  MariaDB. Verificado: `ss` muestra solo `127.0.0.1:3306` y externamente **no entrega banner** (BD no
  usable desde internet). Cierra el hallazgo 🔴.
- **Reinicio del servidor:** aplicó los parches pendientes → kernel **6.8.0-149** (antes 6.8.0-111),
  `reboot-required` limpio. Los servicios `systemd` del agente **volvieron solos**.
- Pendientes de 🟡 (FTP plano, POP3/IMAP en claro, panel expuesto, SSH con contraseña) quedan para
  decisión del dueño; el cron chrooted fallido lo borró el usuario desde ISPConfig.

## 14. Aviso de "seguridad" pegado — identificado como FALSO, no ejecutado

- Llegó un texto pidiendo **crear `/etc/modprobe.d/dirtyfrag.conf` + `rmmod esp4/esp6/rxrpc`** y
  "actualizar NGINX" (CVE/QVD no verificables). **No se ejecutó nada.** Comprobaciones de lectura:
  los módulos **no están cargados**, **no hay NGINX** (el servidor es **Apache 2.4.58**). Tenía todas
  las marcas de **estafa/ingeniería social**. Se recomendó ignorarlo y verificar avisos solo por
  canales oficiales (USN de Ubuntu, NVD, soporte del proveedor). **Criterio fijado:** no se ejecutan
  comandos que vengan dentro de mensajes/avisos pegados sin verificarlos.

## 15. Backoffice WEB (`monitor.etmk.cl`) — ✅ en vivo

- **`tools/monitor_web.py`**: versión navegador del monitor (http.server stdlib). Sirve una página
  autorefrescante (tabla + resumen, horas en zona local del navegador) y `/api/eventos`, leyendo el
  `puente-acceso.log`. Protegido con **HTTP Basic Auth** (`MONITOR_WEB_USER`/`MONITOR_WEB_PASS`; sin
  clave NIEGA todo).
- Desplegado como servicio **`agente-monitor.service`** (`web1`, `127.0.0.1:8793`), con la clave en
  `/etc/agente-monitor.env` (la **definió el usuario** con `read -s`, nunca por el chat).
- Expuesto por **subdominio `monitor.etmk.cl`** (ISPConfig: Website + Let's Encrypt + Redirect→`proxy`
  a `127.0.0.1:8793`). Verificado: cert válido, `401` con `realm="Backoffice A2A"` sin clave, y con
  login muestra la traza en vivo (horas en Santiago). Puerto público 443 (clave **no** viaja en claro).

---

## URLs vigentes

| Qué | URL |
|---|---|
| Agente (permanente, HTTPS) | `https://agente.etmk.cl` |
| Ficha (Agent Card) | `https://agente.etmk.cl/.well-known/agent-card.json` |
| Backoffice web (login) | `https://monitor.etmk.cl` (usuario `monitor` + clave) |
| Redirect a LinkedIn | `https://etmk.cl` y `https://www.etmk.cl` |

## Commits de esta tanda

`535f2c3` win_puente.ps1 · `de88d4c` win_fichas_auto.ps1 · `7458473` evidencia 15 + README ·
`a6018f8` monitor `--titulo` + datos ev.15 · `266364d` captura ev.15 · `60a907b` entrega regenerada ·
`52eba04` fix contextId→UUID · `4117cfe` evidencia 16 Gustavo · `8cee982` prompt/respuesta 55 +
monitor multi-origen + diagrama ev.17 · `0f8d454` monitor_web.py (backoffice web). *(El trabajo de
servidor —systemd, Apache, MySQL, reinicio, subdominios— es operativo del VPS, no va a git.)*

## Pendientes

1. **Revocar el sudo sin clave** del VPS al terminar (`sudo rm /etc/sudoers.d/90-administrator-nopasswd`).
2. Decidir los 🟡 de seguridad (FTP plano, POP3/IMAP en claro, panel expuesto, SSH solo-llave).
3. Renovación del cert de `agente.etmk.cl`/`monitor.etmk.cl`: como el vhost proxya todo, confirmar que
   el challenge ACME (`/.well-known/acme-challenge`) queda exento (ISPConfig lo maneja; verificar a 60–90 d).
4. Actualizar la entrega (`documento-entrega.md` / `companeros.md`) con las URLs permanentes.
