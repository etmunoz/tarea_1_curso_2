<!--encabezado-grupo-->
> **Archivo:** `deploy/README.md`  
> **Objetivo:** Despliegue del servidor (VPS etmk.cl) — servicios, subdominios y pasos para reproducirlo  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1530 · **Última modificación:** 20261112 1530
<!--/encabezado-grupo-->

# Despliegue del servidor (VPS `etmk.cl`)

Todo lo que corre en producción en la VPS. El **código** está en la repo; aquí están la **receta de
infraestructura** (units systemd, plantillas de entorno, config de Apache) para rearmarlo. Los
**secretos nunca se versionan**: van en `/etc/*.env` (ver los `*.env.example`).

## Arquitectura

```
Internet ──HTTPS──> Apache (Let's Encrypt)  ──reverse proxy──>  servicios locales (127.0.0.1)
```

| Subdominio | Servicio systemd | Puerto local | Qué es |
|---|---|---|---|
| `agente.etmk.cl` | `agente-puente` | 8790 | Puente A2A clásico de Ezequiel (para que lo consuman los compañeros) |
| `monitor.etmk.cl` | `agente-monitor` | 8793 | Backoffice web de accesos al puente (Basic Auth) |
| `coordinador.etmk.cl` | `agente-coordinador` | 8794 | Chat del coordinador A2A: rutea a cada agente (Basic Auth) |
| (interno) | `agente-langgraph` | 2024 | `langgraph dev`: grafos nativos (Ezequiel, cocina…). Lo consumen el puente y el coordinador |

Dependencias: `agente-puente` y `agente-coordinador` esperan a `agente-langgraph` (`:2024`) antes de
arrancar (`ExecStartPre` hace *poll* a `/ok`).

## Cómo el coordinador "llega a todos lados"

El coordinador arma su catálogo de agentes en cada consulta desde dos fuentes:

- **Locales del VPS** — vía `A2A_BASE=http://127.0.0.1:2024` (los grafos de `langgraph dev`).
- **Remotos** — vía las URLs que se guardan desde la UI (⚙️ *Configurar agentes*) en
  `logs/coordinador_urls.json`. Cada entrada es `url#grafo` (p. ej. el Ezequiel de un Mac por un
  túnel, o los agentes de Fabio/Gustavo). Editable sin reiniciar.

Así, un mismo coordinador enruta a Ezequiel, Tomás, Fabio y Gustavo estén donde estén, solo
cambiando su URL en la configuración.

## Requisitos en el VPS

- Usuario de sistema con shell (aquí `web1`, shell-user `etmkuseragente`) y su HOME.
- [`uv`](https://docs.astral.sh/uv/) instalado en `~/.local/bin` del usuario.
- La repo clonada en `WorkingDirectory` (aquí `…/etmkuseragente/tarea_1_curso_2`).
- Un `.env` del proyecto con `GOOGLE_API_KEY` (NO versionado).
- Apache + ISPConfig con Let's Encrypt para cada subdominio.

## Pasos

### 1. Variables de entorno (secretos)
```bash
sudo install -m 600 /dev/null /etc/agente-coordinador.env
sudo install -m 600 /dev/null /etc/agente-monitor.env
# editar cada uno según deploy/agente-*.env.example y poner los valores reales
```

### 2. Servicios systemd
```bash
sudo cp deploy/systemd/agente-*.service /etc/systemd/system/
# revisar User/Group/WorkingDirectory/HOME/PATH si el usuario del VPS es otro
sudo systemctl daemon-reload
sudo systemctl enable --now agente-langgraph agente-puente agente-monitor agente-coordinador
systemctl is-active agente-langgraph agente-puente agente-monitor agente-coordinador
```

### 3. Publicación HTTPS (por subdominio, en ISPConfig)
1. Crear el **Website** del subdominio y emitir **Let's Encrypt**.
2. En *Redirect* poner **proxy** al servicio local, p. ej. coordinador → `http://127.0.0.1:8794/`.
3. Forzar HTTPS. Si ISPConfig deja la regla del proxy **antes** del redirect en el vhost `:80`
   (el http no redirige), agregar en *Options → Apache Directives* este bloque, que va **antes**
   de la regla de proxy:
   ```apache
   RewriteEngine On
   RewriteCond %{HTTPS} off
   RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]
   ```
4. Verificar:
   ```bash
   curl -sI http://coordinador.etmk.cl        # -> 301 a https
   curl -sI https://coordinador.etmk.cl        # -> 401 (Basic Auth)
   ```

## Operación

```bash
# actualizar código y reiniciar
cd <repo> && git pull
sudo systemctl restart agente-coordinador      # (o el servicio que toque)

# logs
sudo journalctl -u agente-coordinador -n 50 --no-pager
```

## Seguridad

- **Secretos** solo en `/etc/*.env` (chmod 600, root) — nunca en la repo (`.env` y `logs/` están en
  `.gitignore`).
- **Basic Auth** en monitor y coordinador; HTTPS forzado en todos.
- **Correo del coordinador**: envía solo a destinatarios de la *allowlist* y solo por acción del
  usuario en la UI; nunca auto-envío desde respuestas de agentes (contenido no confiable).
- **Housekeeping pendiente:** revocar el sudo temporal cuando ya no haga falta:
  `sudo rm /etc/sudoers.d/90-administrator-nopasswd`.
