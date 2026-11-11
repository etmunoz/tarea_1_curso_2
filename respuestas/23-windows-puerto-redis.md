<!--encabezado-grupo-->
> **Archivo:** `respuestas/23-windows-puerto-redis.md`  
> **Objetivo:** 23 · Respuesta — Windows: cambiar el puerto de Redis (6379 ocupado)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2208 · **Última modificación:** 20261111 1406
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

---

## Respuesta completa del asistente (chat)

### Mensajes de avance (traducidos; en el chat salieron en inglés)

> Hago el puerto configurable, para que el Windows use 6380 (y 8002 para RedisInsight,
> porque el 8001 también está ocupado) mientras el Mac mantiene los valores por defecto.
> Algo que noté: el otro contenedor, `redis-rag`, ya tiene un índice `reiki` de otro
> proyecto. Con un puerto aparte no lo tocamos.

> Redis está arriba en 6380. Ahora cargo el RAG de Reiki.

### Respuesta final

> El setup de Windows quedó completo: Gemini responde, Redis está corriendo en el puerto que
> cambiamos y el RAG de Reiki ya tiene datos cargados.
>
> **Cambio de puerto**
> Los puertos 6379 y 8001 de tu PC ya estaban ocupados. El 6379 lo usa `redis-rag`, un
> contenedor de otro proyecto que lleva 9 días arriba y que tiene su propio índice `reiki`.
> No lo toqué y sus datos siguen iguales (43 claves).
>
> Hice el puerto configurable para que el Mac no tenga que cambiar nada:
> - **`docker-compose.yml`:** los puertos se leen de `${REDIS_PORT:-6379}` y
>   `${REDISINSIGHT_PORT:-8001}`. Si no se definen, quedan los de siempre.
> - **`.env.example`:** agregué esas dos variables con una nota de cuándo cambiarlas.
> - **Tu `.env` local**, que no se sube a git: `REDIS_PORT=6380`, `REDISINSIGHT_PORT=8002` y
>   `REDIS_URL=redis://localhost:6380`.
>
> **Estado**
> - **Gemini:** con la excepción de AVG responde "OK" directamente, sin ningún ajuste extra.
> - **Redis:** el contenedor `reiki-redis` está arriba en 6380 y RedisInsight se abre en http://localhost:8002.
> - **RAG:** cargó 9 fragmentos en el índice `reiki`. Una búsqueda de prueba devolvió los
>   textos de los niveles de Reiki.
>
> **Pendiente**
> - Los cambios en `docker-compose.yml` y `.env.example` no están en un commit.
> - Las pestañas *setup windows* y *setup windows 2* ya terminaron. La segunda muestra el
>   error de puerto de la ejecución anterior, que ya está resuelto.
> - Faltan los pasos 3 a 5 de la guía. `win_servir.ps1` levanta el agente Tomás y
>   `win_tunel.ps1` abre el túnel. `win_coordinador.ps1` necesita la URL del túnel del Mac.
> - Los `.ps1` siguen sin BOM, así que en PowerShell 5.1 las preguntas del coordinador
>   saldrán con los acentos mal escritos. Conviene arreglarlo antes de generar las evidencias.
