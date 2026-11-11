<!--encabezado-grupo-->
> **Archivo:** `respuestas/17-redis-distribuido-cloudflare.md`  
> **Objetivo:** 17 · Respuesta — Redis distribuido por Cloudflare (Ezequiel hospeda, Tomás usa)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2123 · **Última modificación:** 20261110 2259
<!--/encabezado-grupo-->

# 17 · Respuesta — Redis distribuido por Cloudflare (Ezequiel hospeda, Tomás usa)

Prompt: [`../prompts_ejecutados/17-redis-distribuido-cloudflare.md`](../prompts_ejecutados/17-redis-distribuido-cloudflare.md)

## Arquitectura (reparto, todo por Cloudflare)

- **Mac (Ezequiel)**: agente Ezequiel + **anfitrión del Redis** (Docker) expuesto por un
  **túnel TCP de Cloudflare** + coordinador.
- **Windows (Tomás)**: agente Tomás + **RAG**, que usa el Redis del Mac a través de un
  **forwarder local** (`cloudflared access tcp`).
- Entre equipos, nada por LAN: agentes por túnel HTTP (`trycloudflare.com`), Redis por túnel TCP (named tunnel).

## Archivos creados / modificados

- `scripts/mac_redis_cloudflare.sh` — Mac: `login` + crea el túnel con nombre `reiki-redis`,
  config con `ingress: tcp://localhost:6379`, ruta DNS del host, y lo corre.
- `scripts/win_redis_cloudflare.ps1` — Windows: `cloudflared access tcp --hostname <host> --url localhost:6379`
  (forwarder local → Redis del Mac).
- `scripts/mac_redis.sh` — Mac: levanta el Redis local (anfitrión).
- `scripts/setup_windows.ps1` — `-RedisUrl` escribe `REDIS_URL` en `.env` (apunta al forwarder);
  sin Docker en Windows.
- `.env.example` — `REDIS_URL` documentado para el reparto por Cloudflare.
- `guia_ezequiel_tomas.md` — **reescrita plug-and-play**: reparto, requisitos (incluye el dominio
  Cloudflare), pasos A (Mac) / B (Windows) / C (coordinador), evidencias, troubleshooting y teardown.

## Verificación

```text
$ bash -n scripts/mac_redis.sh scripts/mac_redis_cloudflare.sh   -> sintaxis OK
$ uv run python tools/aplicar_encabezados.py --check             -> OK
$ uv run pytest -q                                               -> 36 passed, 1 skipped
```

## Prerrequisito especial (lo único que no es automatizable)

Un **dominio gestionado en Cloudflare** (nameservers → Cloudflare), para el túnel TCP del
Redis. Elegir un host, p. ej. `redis-tomas.TU-DOMINIO.com`. Los agentes (HTTP) usan túneles
gratis sin dominio.

## Estado

Todo scripteado y en la guía (plug-and-play). Pendiente: la corrida real cuando el Windows
esté configurado y haya un dominio Cloudflare para el túnel TCP del Redis.
