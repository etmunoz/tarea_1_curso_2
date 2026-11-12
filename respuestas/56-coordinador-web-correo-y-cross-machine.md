<!--encabezado-grupo-->
> **Archivo:** `respuestas/56-coordinador-web-correo-y-cross-machine.md`  
> **Objetivo:** 56 · Respuesta — Coordinador web en la VPS: fix de import, ruteo cross-machine y correo  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1521 · **Última modificación:** 20261112 1521
<!--/encabezado-grupo-->

# 56 · Respuesta — Coordinador web en la VPS: fix de import, ruteo cross-machine y correo

Prompt: [`../prompts_ejecutados/56-coordinador-web-correo-y-cross-machine.md`](../prompts_ejecutados/56-coordinador-web-correo-y-cross-machine.md)

> **Hora:** el VPS corre en **UTC**; Santiago está en **UTC−3**. Los logs del VPS van en UTC.

## Resumen

Se dejó operativo `https://coordinador.etmk.cl` (web del coordinador A2A en la VPS): se corrigió el
error `No module named 'src'`, se probó el **ruteo cross-machine** VPS → **Ezequiel del Mac**
(remoto por túnel) y se agregó **envío de correo** desde `coordinador@etmk.cl` con guardrail.

## 1 · Fix `No module named 'src'`

El servicio `agente-coordinador.service` corre con `WorkingDirectory` del repo pero sin el raíz en
`sys.path`, así que `from src.coordinador…` fallaba. Se agregó al inicio de
`tools/coordinador_web.py`:

```python
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:  # el servicio puede correr fuera del raíz del repo
    sys.path.insert(0, str(RAIZ))
```

Commit `e94e995`. Deploy en VPS: `git reset --hard origin/main` + `systemctl restart
agente-coordinador` (vía usuario `administrator` con sudo; `etmkuseragente` no tiene sudo).

## 2 · Ruteo cross-machine (VPS → Ezequiel del Mac)

El usuario guardó en la config ⚙️ la URL del túnel del Mac. `logs/coordinador_urls.json`:

```json
{ "ezequiel": "https://reservations-defining-taught-jul.trycloudflare.com",
  "tomas": "", "fabio": "", "gustavo": "" }
```

Prueba ejecutada en el VPS importando el propio `coordinador_web` (misma lógica que el endpoint):

```
URLS_AGENTES = https://reservations-defining-taught-jul.trycloudflare.com#agente_ezequiel
--- RESULTADO ---
ruta     : ['guardia_entrada', 'supervisor', 'agente_remoto', 'guardia_salida']
elegido  : Agente de Ezequiel
respuesta: [Agente de Ezequiel] Para el desbalance de clases te recomiendo usar *class weights*,
           resampleo (SMOTE o undersampling) y métricas orientadas a la clase minoritaria…
```

→ El supervisor de la VPS eligió a Ezequiel y lo consumió por A2A en el **túnel del Mac** (otra
máquina). El túnel es efímero: al renovarlo se actualiza la URL en ⚙️.

## 3 · Envío de correo desde `coordinador@etmk.cl`

Cambios en `tools/coordinador_web.py` (commits `3400ff5`, `9b728b4`):

- Config SMTP por entorno (`COORD_SMTP_HOST/PORT/USER/PASS`, `COORD_MAIL_FROM`, allowlist
  `COORD_MAIL_ALLOW` → fallback a `COORD_MAIL_TO`). **Credenciales solo en
  `/etc/agente-coordinador.env`**, nunca en el repo.
- `_enviar_correo(para, asunto, cuerpo)`: valida allowlist, arma `EmailMessage`, envía por
  `smtplib.SMTP` 587 + STARTTLS. En loopback (`localhost`) usa contexto sin verificación de cert
  (el cert es del hostname de correo, no de `localhost`); fuera de loopback verifica normal.
- Rutas: `GET /api/correo` (estado + allowlist) y `POST /api/enviar-correo`.
- UI: botón «✉️ Enviar por correo» en cada respuesta del coordinador → modal (Para=allowlist,
  Asunto, Mensaje prellenado y editable).
- **Guardrail**: solo destinatarios de la allowlist y disparo **solo** por acción del usuario en la
  UI; nunca auto-envío a partir de respuestas de agentes (contenido no confiable). Todo detrás del
  Basic Auth del sitio.

### Verificación real del envío

`GET /api/correo`:
```json
{"configurado": true, "destinatarios": ["etmunoz@gmail.com"], "from": "coordinador@etmk.cl"}
```
`POST /api/enviar-correo` → `{"ok": true, "detalle": "enviado a etmunoz@gmail.com"}`

Log de Postfix (`/var/log/mail.log`) del envío:
```
submission/smtpd: client=localhost[127.0.0.1], sasl_method=PLAIN, sasl_username=coordinador@etmk.cl
BCC5740881: from=<coordinador@etmk.cl>, size=753, nrcpt=1
postfix/smtp: to=<etmunoz@gmail.com>, relay=gmail-smtp-in.l.google.com:25,
              dsn=2.0.0, status=sent (250 2.0.0 OK … gsmtp)
```
→ Submission autenticada en 587 como `coordinador@etmk.cl` y **Gmail aceptó (250)**. `etmk.cl` ya
tiene SPF/DKIM/DMARC en PASS, así que sale firmado.

Verificación en el **«Mostrar original» de Gmail** (headers reales del correo recibido):

```
SPF:   PASS  (coordinador@etmk.cl designates 69.197.134.192 as permitted sender)
DKIM:  PASS  (header.i=@etmk.cl  header.s=default)
DMARC: PASS  (p=NONE  header.from=etmk.cl)
Authenticated sender: coordinador@etmk.cl · TLS1_3 · Message-Id <…@server28.etmk.cl>
```

## Archivos tocados

- `tools/coordinador_web.py` — `sys.path`, SMTP (`_enviar_correo`), rutas `/api/correo` y
  `/api/enviar-correo`, modal + botón de correo en la UI.
- `prompts_ejecutados/56-…md` y `respuestas/56-…md` (este registro).

## Estado

- `https://coordinador.etmk.cl` operativo: HTTPS forzado (http→301→https), Basic Auth (usuario
  `coordinador`), ruteo a agentes locales (VPS) y remotos (túnel) funcionando.
- Correo del coordinador operativo y verificado end-to-end a `etmunoz@gmail.com`.

## Pendientes

- **Revocar sudo temporal**: `sudo rm /etc/sudoers.d/90-administrator-nopasswd` (housekeeping).
- Sumar a los compañeros a la allowlist de correo cuando se defina
  (`COORD_MAIL_ALLOW=etmunoz@gmail.com,otro@…` en el `EnvironmentFile`).
- El túnel del Mac (Ezequiel remoto) es efímero; para demo estable se usa el permanente
  `https://agente.etmk.cl`.
- Nota: `tools/aplicar_encabezados.py` sin argumentos recalcula la fecha de **todos** los archivos;
  al registrar un solo cambio, versionar solo los archivos tocados.
