<!--encabezado-grupo-->
> **Archivo:** `respuestas/23-windows-puerto-redis.md`  
> **Objetivo:** 23 · Respuesta — Windows: cambiar el puerto de Redis (6379 ocupado)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2208 · **Última modificación:** 20261110 2208
<!--/encabezado-grupo-->

# 23 · Respuesta — Windows: cambiar el puerto de Redis (6379 ocupado)

Prompt: [`../prompts_ejecutados/23-windows-puerto-redis.md`](../prompts_ejecutados/23-windows-puerto-redis.md)

## Diagnóstico

```text
docker compose up -d   -> Bind for 0.0.0.0:6379 failed: port is already allocated
docker ps              -> redis-rag (redis/redis-stack-server, otro proyecto) en 0.0.0.0:6379, arriba hace 9 días
puerto 8001            -> ocupado por otro proceso python (RedisInsight también chocaría)
redis-rag FT._LIST     -> ya tiene un índice llamado 'reiki' (de otro proyecto)
```

**Por qué no reutilizar `redis-rag`:** `cargar_rag_reiki.py` hace `dropindex(delete_documents=True)`
del índice `reiki` antes de cargar. Si se apuntaba ahí, **habría borrado los datos de otro proyecto**.
Por eso se usa un Redis propio en otro puerto.

## Qué se hizo

- **`docker-compose.yml`:** puertos del host configurables, con los mismos valores por defecto
  (el Mac no cambia nada):
  ```yaml
  - "${REDIS_PORT:-6379}:6379"          # Redis
  - "${REDISINSIGHT_PORT:-8001}:8001"   # RedisInsight (UI web)
  ```
  `docker compose` lee esas variables del `.env` de la raíz automáticamente.
- **`.env.example`:** se documentaron `REDIS_PORT` y `REDISINSIGHT_PORT` (por defecto 6379/8001).
- **`.env` del Windows** (no versionado): `REDIS_PORT=6380`, `REDISINSIGHT_PORT=8002`,
  `REDIS_URL=redis://localhost:6380`.
- `docker compose up -d` → recreó `reiki-redis`; luego `uv run python tools/cargar_rag_reiki.py`.

## Resultado

```text
reiki-redis   Up   0.0.0.0:6380->6379/tcp, 0.0.0.0:8002->8001/tcp
redis-cli PING                       -> PONG
cargar_rag_reiki.py                  -> Cargando data\reiki → índice 'reiki' en redis://localhost:6380 …
                                        ✓ 9 fragmentos indexados.
rag.disponible()                     -> True
rag.buscar('cinco principios del Reiki', k=2)
                                     -> Nivel 1 (Shoden) "El principio" · Nivel 4 Maestría
redis-rag DBSIZE (antes y después)   -> 43 (intacto)
```

## Lo bueno

- RAG de Tomás operativo sobre su Redis local, sin tocar el Redis del otro proyecto.
- El cambio es retrocompatible: sin variables, todo queda en 6379/8001 como antes.

## Lo malo / observaciones

- La 1ª descarga de `redis/redis-stack` (373 MB) tomó ~5 minutos.
- En `.env.example` hay 3 líneas `REDIS_URL=` repetidas (heredadas de prompts anteriores);
  python-dotenv usa la última. Conviene dejar una sola.

## Estado

Setup del Windows completo (pasos 1–5 de la guía). Falta: `win_servir.ps1`, `win_tunel.ps1`
y `win_coordinador.ps1` con la URL del túnel del Mac.
