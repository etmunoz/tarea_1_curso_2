<!--encabezado-grupo-->
> **Archivo:** `respuestas/57-antecedentes-de-acceso-en-el-ruteo.md`  
> **Objetivo:** 57 · Respuesta — Antecedentes del acceso (local/remoto, endpoint, host, IP) en el panel  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1552 · **Última modificación:** 20261112 1552
<!--/encabezado-grupo-->

# 57 · Respuesta — Antecedentes del acceso en el panel de ruteo

Prompt: [`../prompts_ejecutados/57-antecedentes-de-acceso-en-el-ruteo.md`](../prompts_ejecutados/57-antecedentes-de-acceso-en-el-ruteo.md)

## Resumen

El panel "Ruteo del coordinador" ahora muestra, bajo el agente elegido, una tarjeta **"Antecedentes
del acceso"** con: **tipo** (local/remoto), **servidor**, **grafo**, **endpoint**, **host** e **IP**.
Así se ve a qué se accede realmente en cada consulta (el agente local del VPS o uno remoto por túnel).

## Cambios en `tools/coordinador_web.py`

- `_resolver_ip(host)`: resuelve la IP del host (best-effort, timeout 3 s, sin bloquear).
- `_detalle_destino(cat, elegido, ruta)`: ubica el agente elegido en el catálogo
  (`AgenteRemoto.base_url/graph/local`) y arma el `destino`:
  - `tipo`: `local` si corre en el `A2A_BASE` del propio servidor, `remoto` si es de un túnel/URL.
  - `grafo`, `endpoint` (base_url), `host` (de la URL) e `ip` (resuelta).
  - Si es **local**, agrega `servidor` y `ip_publica` desde el entorno (`COORD_SERVIDOR`,
    `COORD_SERVIDOR_IP`) para mostrar la identidad pública del VPS en vez de `127.0.0.1`.
  - Robustez: si no logra mapear el agente, al menos informa local/remoto según la ruta.
- `_preguntar(...)`: ahora retorna también `destino`.
- Frontend (`pintarRuteo`): tarjeta con las filas no vacías, entre el agente elegido y los pasos.

En el VPS se agregaron al `EnvironmentFile` (no secretos):
```
COORD_SERVIDOR=coordinador.etmk.cl
COORD_SERVIDOR_IP=69.197.134.192
```

Commit `43266dd`. Deploy: `git reset --hard origin/main` + `systemctl restart agente-coordinador`.

## Verificación real (API local del coordinador, VPS)

**Pregunta local (cocina):**
```json
elegido: agente_cocina
destino: {"tipo":"local","grafo":"agente_cocina","endpoint":"http://127.0.0.1:2024",
          "host":"127.0.0.1","ip":"127.0.0.1",
          "servidor":"coordinador.etmk.cl","ip_publica":"69.197.134.192"}
```

**Pregunta remota (IA → Ezequiel del Mac):**
```json
elegido: Agente de Ezequiel
destino: {"tipo":"remoto","grafo":"agente_ezequiel",
          "endpoint":"https://reservations-defining-taught-jul.trycloudflare.com",
          "host":"reservations-defining-taught-jul.trycloudflare.com","ip":"104.16.231.132"}
```

→ Local resuelve a la identidad pública del VPS (`coordinador.etmk.cl` / `69.197.134.192`); remoto
muestra el host del túnel y la IP de Cloudflare.

## Archivos tocados

- `tools/coordinador_web.py` — `_resolver_ip`, `_detalle_destino`, `destino` en `_preguntar`,
  tarjeta en `pintarRuteo`.
- `/etc/agente-coordinador.env` (en el VPS) — `COORD_SERVIDOR`, `COORD_SERVIDOR_IP`.
- `prompts_ejecutados/57-…md` y `respuestas/57-…md` (este registro).

## Estado

- Desplegado y verificado en `https://coordinador.etmk.cl`; el panel muestra los antecedentes en
  cada consulta (local y remota).

## Pendientes

- `deploy/agente-coordinador.env.example` conviene incluir `COORD_SERVIDOR` / `COORD_SERVIDOR_IP`
  como opcionales (se agregan en este mismo registro).
- Housekeeping: revocar el sudo temporal (`sudo rm /etc/sudoers.d/90-administrator-nopasswd`).
