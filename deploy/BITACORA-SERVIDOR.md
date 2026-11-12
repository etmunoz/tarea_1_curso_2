<!--encabezado-grupo-->
> **Archivo:** `deploy/BITACORA-SERVIDOR.md`  
> **Objetivo:** Bitácora detallada de todo lo hecho en el servidor (VPS etmk.cl)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1532 · **Última modificación:** 20261112 1532
<!--/encabezado-grupo-->

# Bitácora del servidor — VPS `etmk.cl`

Registro detallado de todo lo que se montó en la VPS para pasar de "URLs de túnel efímeras" a un
despliegue **permanente con HTTPS**: el agente, el puente para compañeros, el backoffice y el
coordinador web, más el endurecimiento del equipo y el correo. Complementa a
[`README.md`](README.md) (que tiene la receta reproducible) con el **por qué** y el **cómo** de cada
decisión.

- **Host:** Ubuntu 24.04.5 LTS, virtualización KVM/QEMU, kernel 6.8.0-149.
- **IP pública:** 69.197.134.192 · **Dominio:** `etmk.cl` · **Hostname:** `server28.etmk.cl`.
- **Panel:** ISPConfig (Apache, Postfix, Dovecot, rspamd). DNS externo (no PowerDNS local).
- **Zona horaria del server:** UTC (Santiago = UTC−3; los logs van en UTC).

---

## 0. Motivación

Las pruebas A2A entre compañeros usaban **túneles Cloudflare efímeros** (`*.trycloudflare.com`),
cuya URL cambia en cada corrida y caduca. Eso complicaba que el grupo consumiera el agente de
Ezequiel de forma estable. Decisión: **publicar el agente de forma permanente** en el dominio y la
VPS propios (`etmk.cl`), con HTTPS, y de paso dar al coordinador una interfaz web.

---

## 1. Acceso al servidor

- **Panel ISPConfig:** acceso web para administrar websites, DNS, correo y usuarios shell.
- **Usuarios de sistema:**
  - `administrator` — usuario con **sudo**. Para tareas de root (systemd, Apache, paquetes) se le
    dejó un `NOPASSWD` **temporal** en `/etc/sudoers.d/90-administrator-nopasswd`
    (**pendiente de revocar**, ver §11).
  - `etmkuseragente` — **Shell-User** creado en ISPConfig (mapeado al usuario de sistema `web1`,
    grupo `client1`). Es el dueño de la repo y bajo el que corren los servicios. **No** tiene sudo.
- **SSH:** autenticación por clave. El usuario generó el par y subió la pública (esto lo hizo él en
  su terminal; el asistente no manipula llaves privadas). Hubo un baneo temporal de IP por intentos
  fallidos de fail2ban mientras calzaban las llaves; se resolvió.
- **Rutas clave:**
  - Repo: `/var/www/clients/client1/web1/home/etmkuseragente/tarea_1_curso_2`
  - `uv`: `/var/www/clients/client1/web1/home/etmkuseragente/.local/bin/uv`
  - Nota: en SSH **no interactivo** el PATH no incluye `~/.local/bin`; por eso las units systemd y
    los comandos manuales usan la ruta absoluta de `uv`.

## 2. Preparación del entorno

- Instalación de **`uv`** en el HOME de `etmkuseragente`.
- **Clonado** de la repo en el `WorkingDirectory` de arriba.
- `.env` del proyecto con `GOOGLE_API_KEY` (Gemini) — **no versionado**.
- `uv sync` para resolver dependencias (en una corrida quedó un proceso `uv sync` zombie que se
  mató; no afectó al despliegue).

## 3. Persistencia: de cron a systemd

Primer intento de mantener vivo el agente con un **cron keepalive** de ISPConfig falló: el cron corre
**chrooted** como `web2` (sin `uv` ni `curl` en ese entorno). Se descartó.

Solución definitiva: **servicios systemd** (sobreviven reboot, se reinician solos, dependencias
ordenadas). Se crearon cuatro (ver [`systemd/`](systemd/)):

| Servicio | Puerto | Rol |
|---|---|---|
| `agente-langgraph` | 2024 | `langgraph dev` con los grafos nativos (Ezequiel, cocina…). Base de todo. |
| `agente-puente` | 8790 | Puente A2A **clásico** (`message/send`) → publicado en `agente.etmk.cl`. |
| `agente-monitor` | 8793 | Backoffice web de accesos al puente → `monitor.etmk.cl`. |
| `agente-coordinador` | 8794 | Chat del coordinador A2A → `coordinador.etmk.cl`. |

Detalles:
- Todos corren como `User=web1 Group=client1`, con `HOME` y `PATH` explícitos (por el tema del PATH
  no interactivo).
- `agente-puente` y `agente-coordinador` tienen `ExecStartPre` que espera a que `:2024/ok` responda
  antes de arrancar (evita carreras al bootear).
- `agente-puente` corre además `ExecStartPost` con `tools/configurar_fichas.py` para registrar las
  fichas (agent cards) de `agente_ezequiel` y `agente_cocina` al levantar.
- Secretos fuera de las units, en `EnvironmentFile` (`/etc/agente-*.env`).

## 4. Subdominios + HTTPS (Apache + Let's Encrypt)

Para cada subdominio: Website en ISPConfig + certificado **Let's Encrypt** (acme.sh) + *Redirect*
tipo **proxy** al puerto local.

- `agente.etmk.cl` → `http://127.0.0.1:8790/`
- `monitor.etmk.cl` → `http://127.0.0.1:8793/`
- `coordinador.etmk.cl` → `http://127.0.0.1:8794/`

**Bug del force-HTTPS:** en `coordinador.etmk.cl`, ISPConfig puso la regla del **proxy antes** del
redirect a HTTPS en el vhost `:80`, así que `http://` llegaba al backend sin redirigir (se veía el
401 por HTTP, con la clave viajando en claro). Se corrigió insertando, **antes** de la regla de
proxy, la redirección:
```apache
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]
```
Verificado: `http → 301 → https` y `https → 401` (Basic Auth). Ahora la clave siempre viaja cifrada.

**Caveat de Chrome:** tras emitir los certificados, Chrome mostraba "No seguro" por caché de certificado;
Safari funcionaba. Se resolvió cerrando Chrome del todo (Cmd+Q) para refrescar la caché.

## 5. Endurecimiento (hardening) — software y VM

Revisión pedida explícitamente antes de usar el equipo "en serio":

- **MySQL/MariaDB**: escucha solo local.
- **Firewall**: se recortaron puertos a lo necesario (web, correo, SSH); jaula fail2ban adicional
  para el backoffice (8080/panel).
- **FTP**: deshabilitado (se usa SFTP/SSH).
- **Dovecot**: TLS forzado.
- **Kernel**: actualizado (quedó 6.8.0-149 tras reboot). El `apt full-upgrade` reinició `openssh` y
  tumbó la sesión SSH una vez → se finalizó el upgrade de forma **desacoplada** con
  `systemd-run --unit=apt-finish` para que terminara aunque cayera la conexión; resultado: 0
  paquetes pendientes, dpkg limpio.
- **sysctl**: endurecimientos de red estándar.
- **SSH**: hardening (sin password donde aplica, etc.).
- **fail2ban**: activo (fue el que baneó la IP durante el ajuste de llaves).

## 6. Correo del dominio

Se revisó la operatividad del correo y se dejó entregable:

- **SPF / DKIM / DMARC = PASS** (verificado con "Mostrar original" de Gmail). DKIM con selector
  `default`, dominio `etmk.cl`.
- **Webmail** (Roundcube) accesible con certificado válido; el panel ISPConfig se dejó con el cert
  de Let's Encrypt (se enlazó `ispserver.crt/key` → `etmk.cl-le.crt/key` porque venía autofirmado).
- **Spam**: en los primeros envíos a Gmail caían a Spam por **reputación de remitente nuevo**, no por
  configuración (SPF/DKIM/DMARC estaban OK). Mejora con el tiempo/uso.

## 7. Coordinador web (`coordinador.etmk.cl`)

App nueva: [`tools/coordinador_web.py`](../tools/coordinador_web.py) — servidor stdlib
(`ThreadingHTTPServer`), sin framework. Características:

- **Diseño** moderno dark/light (glassmorphism, fondo *aurora*, fuente Inter), toggle de tema que
  persiste en `localStorage`.
- **Chat** a la izquierda + panel **"Ruteo del coordinador"** a la derecha, que muestra el agente
  elegido por el supervisor y el camino (`guardia_entrada → supervisor → agente_remoto/consultar →
  guardia_salida`).
- **Configuración ⚙️** con las 4 URLs (Ezequiel, Tomás, Fabio, Gustavo): vacío = usar el local del
  VPS; con URL = agente remoto. Se guarda en `logs/coordinador_urls.json` y se traduce a
  `A2A_GRAFOS_LOCALES` + `URLS_AGENTES` que el catálogo lee en cada consulta.
- **Basic Auth** (usuario `coordinador`), detrás del HTTPS de Apache.

### 7.1 Fix `No module named 'src'`

El servicio corría sin el raíz del repo en `sys.path`, así que `from src.coordinador…` fallaba y el
chat respondía `error del coordinador: No module named 'src'` (ruteo "ninguno"). Fix:
```python
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
```
Commit `e94e995`, desplegado con `git reset --hard origin/main` + `systemctl restart`.

### 7.2 Prueba cross-machine (VPS → Ezequiel del Mac)

Se levantó un túnel Cloudflare en el Mac exponiendo su `langgraph :2024`, y se puso esa URL en la
⚙️ del coordinador de la VPS (campo Ezequiel). Resultado real de la ronda:
```
URLS_AGENTES = https://<tunel-del-mac>.trycloudflare.com#agente_ezequiel
ruta     : guardia_entrada → supervisor → agente_remoto → guardia_salida
elegido  : Agente de Ezequiel
respuesta: [Agente de Ezequiel] Para el desbalance de clases… class weights, SMOTE/undersampling…
```
→ El coordinador **de la VPS** enrutó y consumió al Ezequiel que corre **en otra máquina** (el Mac).

## 8. Correo del coordinador (`coordinador@etmk.cl`)

Se creó un **buzón dedicado** `coordinador@etmk.cl` para que el agente coordinador pueda **enviar
correos** sin usar la cuenta personal.

- **Credenciales** solo en `/etc/agente-coordinador.env` (`COORD_SMTP_*`, `COORD_MAIL_*`); el
  asistente nunca vio la clave (la insertó el usuario con `read -s` directo en el servidor).
- **Envío** por SMTP submission del propio VPS: `localhost:587` + STARTTLS, autenticado como el
  buzón. En loopback se usa contexto TLS sin verificación de hostname (el cert es del hostname de
  correo, no de `localhost`).
- **Endpoints**: `GET /api/correo` (estado + allowlist) y `POST /api/enviar-correo`. En la UI, cada
  respuesta del coordinador trae un botón **"✉️ Enviar por correo"** → modal (Para=allowlist,
  Asunto, Mensaje editable).
- **Guardrail de seguridad**: solo destinatarios de la **allowlist** (`COORD_MAIL_ALLOW`, hoy solo
  `etmunoz@gmail.com`) y envío **solo** por acción del usuario en la UI; **nunca** auto-envío a
  partir de respuestas de agentes (que son contenido no confiable). Commits `3400ff5`, `9b728b4`.

### 8.1 Verificación end-to-end

`POST /api/enviar-correo` → `{"ok": true, "detalle": "enviado a etmunoz@gmail.com"}`. Log Postfix:
```
submission/smtpd: client=localhost[127.0.0.1], sasl_method=PLAIN, sasl_username=coordinador@etmk.cl
from=<coordinador@etmk.cl> … to=<etmunoz@gmail.com>, relay=gmail-smtp-in… status=sent (250 OK)
```
"Mostrar original" en Gmail del correo recibido:
```
SPF: PASS (69.197.134.192)   DKIM: PASS (@etmk.cl, s=default)   DMARC: PASS
Authenticated sender: coordinador@etmk.cl · TLS1_3
```

## 9. Backoffice / monitor

- [`tools/monitor_web.py`](../tools/monitor_web.py): web en `monitor.etmk.cl`, accesos al puente
  ordenados del más nuevo al más viejo, Basic Auth.
- [`tools/monitor_puente.py`](../tools/monitor_puente.py): monitor de terminal multi-origen (Local /
  VPS por SSH `tail -F`), con flags `--vps`/`--remota` (usa `MONITOR_VPS_SSH` y `MONITOR_VPS_LOG`).

## 10. 404 cosméticos

En el log del puente aparecían 404 de `GET /`, `/favicon.ico`, `/robots.txt` (scanners y navegadores
de paso). Se agregaron respuestas de cortesía en `src/puente_a2a/servidor.py` (texto en `/`, 204 en
favicon, robots.txt) — cosmético, sin exponer nada.

## 11. Estado final y pendientes

**Operativo y verificado:**
- `https://agente.etmk.cl` — agente de Ezequiel (A2A clásico), permanente.
- `https://monitor.etmk.cl` — backoffice (Basic Auth).
- `https://coordinador.etmk.cl` — coordinador web (Basic Auth), ruteo local + remoto y correo.
- Los 4 servicios systemd `active`; HTTPS forzado; SPF/DKIM/DMARC PASS.

**Pendientes / housekeeping:**
- **Revocar sudo temporal:** `sudo rm /etc/sudoers.d/90-administrator-nopasswd`. (Ojo: tras esto, el
  asistente ya no puede reiniciar servicios por su cuenta.)
- Sumar a los compañeros a `COORD_MAIL_ALLOW` cuando se definan sus correos.
- El túnel del Mac (Ezequiel remoto) es **efímero**; para demo estable, usar el permanente
  `https://agente.etmk.cl`.
- `tools/aplicar_encabezados.py` sin argumentos recalcula la fecha de **todos** los archivos; al
  registrar un cambio puntual, versionar solo los archivos tocados.

## Anexo · Mapa de puertos

| Puerto | Bind | Servicio |
|---|---|---|
| 2024 | 127.0.0.1 | `langgraph dev` (grafos nativos) |
| 8790 | 127.0.0.1 | puente A2A clásico (→ agente.etmk.cl) |
| 8793 | 127.0.0.1 | backoffice monitor (→ monitor.etmk.cl) |
| 8794 | 127.0.0.1 | coordinador web (→ coordinador.etmk.cl) |
| 80/443 | público | Apache (reverse proxy + Let's Encrypt) |
| 25/587/465/993… | público | Postfix/Dovecot (correo) |
