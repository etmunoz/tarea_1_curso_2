<!--encabezado-grupo-->
> **Archivo:** `respuestas/50-backoffice-monitor-accesos-puente.md`  
> **Objetivo:** Respuesta 50 · Backoffice de accesos al puente A2A  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1723 · **Última modificación:** 20261111 2016
<!--/encabezado-grupo-->

# Respuesta 50 · Backoffice de accesos al puente A2A

Prompt: [`../prompts_ejecutados/50-backoffice-monitor-accesos-puente.md`](../prompts_ejecutados/50-backoffice-monitor-accesos-puente.md)

## 1. Log de accesos en el puente (`src/puente_a2a/servidor.py`)

Se cambió `_Handler.log_message` (antes silenciaba) por un **log de accesos opcional**: si la
variable `PUENTE_LOG` apunta a un archivo, escribe una línea TSV por request:

```
<fecha UTC ISO-8601>	<IP del cliente>	"<MÉTODO> <ruta> HTTP/1.1" <código> -
```

- La IP es la **real del cliente** (toma `Cf-Connecting-Ip` / `X-Forwarded-For` que reenvía
  Cloudflare; si no, la de conexión). **No** se guarda el contenido del mensaje ni secretos.
- Sin `PUENTE_LOG`, el puente sigue silencioso (comportamiento previo).
- El puente corriendo se relanzó con `PUENTE_LOG=logs/puente-acceso.log` (y su URL pública).

## 2. App Tkinter `tools/monitor_puente.py`

Backoffice de escritorio (Tkinter, **stdlib, sin dependencias nuevas**) que **solo LEE** el log
(no toca el puente ni el túnel → seguro mientras un compañero prueba). Cada 1 s lee las líneas
nuevas (con offset, tolera rotación) y:

- Tabla: **Hora · IP del cliente · Qué hizo · Ruta · Código**. "Qué hizo" traduce método+ruta a
  lenguaje claro: `GET /.well-known/agent-card.json` → «📇 Leyó la ficha (descubrimiento)»,
  `POST /` → «💬 Envió una consulta (message/send)», `/ok` → «💚 Health check».
- Filas coloreadas (consulta/ficha) y auto-scroll al último acceso.
- Resumen: total de accesos, IPs distintas, nº de consultas vs fichas, y último acceso (hora + IP).

Uso:
```bash
uv run python tools/monitor_puente.py
uv run python tools/monitor_puente.py --log logs/puente-acceso.log
```
(Admite `--captura <png>` para auto-guardar una imagen de la ventana.)

## 3. Evidencia (accesos REALES, incluido Gustavo)

Log real al momento de la evidencia (`logs/puente-acceso.log`):

```
20:15:47Z  152.230.191.47  GET /.well-known/agent-card.json  200   (prueba propia)
20:15:51Z  152.230.191.47  POST /                            200   (prueba propia)
20:17:06Z  186.107.24.191  GET /.well-known/agent-card.json  200   ← Gustavo (leyó la ficha)
20:17:49Z  186.107.24.191  GET /.well-known/agent-card.json  200   ← Gustavo
20:22:31Z  186.107.24.191  POST /                            200   ← Gustavo (envió una consulta)
```

La ventana Tkinter mostró estos 5 accesos en vivo (2 IPs distintas; la de Gustavo,
`186.107.24.191`, aparece leyendo la ficha y **enviando una consulta** a `agente_ezequiel`).
Render del panel con los datos reales: `evidencias/12-backoffice-monitor-mac.svg` (coincide 1:1
con la ventana real que confirmó el usuario por captura).

## Notas

- Lo del log + la app son cambios en el **árbol de trabajo de `main`** (para la demo en curso);
  **no se commiteó ni pusheó a `main`** para no interferir con las pruebas de Gustavo.
- Pendiente (no se hizo ahora para no reiniciar el puente): log **estructurado** (JSONL con
  operación + vista previa saneada del texto) para un "qué accede" más rico.
