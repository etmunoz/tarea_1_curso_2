<!--encabezado-grupo-->
> **Archivo:** `evidencias/15-backoffice-tomas-mac.md`  
> **Objetivo:** Backoffice en vivo: el monitor de Tomás (Windows) registra el tráfico entrante desde el Mac · evidencia (mac)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 2120 · **Última modificación:** 20261111 2120
<!--/encabezado-grupo-->

# Backoffice en vivo · el monitor de Tomás ve quién consume su agente

Demostración cruzada del **backoffice** (prompt 50): Tomás levantó en su **Windows** el
puente A2A clásico **delante de `agente_tomas`** y su **monitor Tkinter**
(`tools/monitor_puente.py`), que lee el log de accesos del puente. Desde el **Mac** (Ezequiel)
consumimos su agente por su túnel de Cloudflare y el monitor de Tomás registró, en vivo, cada
acceso (IP del edge de Cloudflare, método, path, código).

## Montaje

- **Windows (Tomás)** — scripts nuevos `scripts/win_puente.ps1` + `scripts/win_fichas_auto.ps1`:
  - `agente_tomas` en `langgraph dev` (:2024), fichas auto-mantenidas (`win_fichas_auto.ps1`).
  - Puente A2A clásico en `:8791` escribiendo `logs\puente-tomas.log` (`win_puente.ps1`).
  - Túnel `cloudflared tunnel --url http://127.0.0.1:8791` → URL pública del puente.
  - Monitor `uv run python tools\monitor_puente.py --log logs\puente-tomas.log`.
- **Mac (Ezequiel)** — cliente A2A generalizado (`src/coordinador/a2a.py`) apuntando a esa URL.

> El puente es necesario porque `langgraph dev` **nativo no escribe** el log de accesos que
> lee el monitor; consumiendo a través del puente clásico, cada petición queda registrada.

## Tráfico generado desde el Mac (en vivo)

Cuatro consultas de Reiki a `agente_tomas`, todas respondidas por el puente (code 200):

| ctx | consulta | respuesta (resumen) |
|---|---|---|
| demo-mac-1 | ¿Qué es el Reiki y cuáles son sus principios? | Rei+Ki; **5 Gokai** (solo por hoy: no te enojes / no te preocupes / sé agradecido / trabaja con honestidad / sé amable) + disclaimer |
| demo-mac-2 | ¿En qué consiste una sesión y cuánto dura? | imposición de manos, presencial o a distancia (símbolos) |
| demo-mac-3 | ¿Diferencia entre Shoden, Okuden y Shinpiden? | N1 físico/autotratamiento · N2 símbolos a distancia/mental-emocional · N3 maestría |
| demo-mac-4 | ¿Reiki reemplaza al tratamiento médico? | **no reemplaza**; acudir a un profesional de la salud |

Antes de estas, el monitor ya mostraba **dos lecturas de la ficha** (GET de la Agent Card) y una
**consulta de prueba** del propio Tomás («¿Qué es Shoden?»).

## Detalle técnico

- **Dialecto:** entró directo por `message/send` (dialecto clásico estándar del puente); el
  cliente **no** necesitó el fallback a `SendMessage` (eso es solo para el SDK de Gustavo).
  Verificable: `a2a._cache_metodo[url]` quedó en `None` (no se aprendió `SendMessage`).
- **Registro sin fugas:** el log guarda metadatos de acceso (timestamp UTC, IP vía
  `Cf-Connecting-Ip`/`X-Forwarded-For`, `"METHOD path"`, código) — **no** el contenido de los
  mensajes ni secretos.

## Lo que demuestra

- **Backoffice operativo cross-machine:** el monitor de Tomás (Windows) ve en tiempo real quién
  consume su agente, incluido el tráfico originado en el Mac.
- **Interoperabilidad A2A clásica** Mac → puente de Windows → `agente_tomas`, con respuestas
  correctas de dominio (Reiki) y disclaimers de seguridad presentes.
- **Automatización:** fichas auto-mantenidas en Windows (`win_fichas_auto.ps1`), sin re-aplicar
  a mano tras cada recarga de `langgraph dev`.

## Captura

Tomás confirmó que su monitor Tkinter está abierto y registra el tráfico. Si envía un screenshot
de la ventana, se incrusta aquí como `evidencias/15-backoffice-tomas.png`.
