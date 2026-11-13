<!--encabezado-grupo-->
> **Archivo:** `entrega/documento-entrega.md`  
> **Objetivo:** Documento de entrega · Taller A2A (Curso 2 · Sesión 1)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1941 · **Última modificación:** 20261112 2218
<!--/encabezado-grupo-->

# Documento de entrega · Taller A2A (Curso 2 · Sesión 1)

> **Cómo leer este documento.** Sigue los pasos del taller (1 a 8) y agrega dos
> secciones de cierre: cómo correr el proyecto (9) y las mejoras de robustez que
> implementamos sobre el coordinador (10). El PDF se genera con
> `uv run tools/exportar_pdf.py`. Las capturas `01-saltos.png` / `03-tunel.png` se
> generaron desde la corrida real (son reemplazables por capturas de pantalla
> manuales). Fabio y Gustavo ya entregaron sus blueprints (ver §2). La prueba final del
> coordinador en producción con los agentes de todos está en §11.1 y en
> `evidencias/evidencias_coordinador.md`.

## 0. Resumen ejecutivo

Construimos una red de **agentes que hablan por A2A** (Agent-to-Agent) usando
**LangGraph nativo**: cada agente se publica con `langgraph dev` y se descubre y se
invoca por su **Agent Card**, sin pegamento propietario. Sobre esa base levantamos un
**coordinador/supervisor** que, dada una pregunta del usuario, decide a qué agente
mandarla leyendo las fichas del catálogo, y reenvía por A2A.

La gracia del trabajo es que funciona **entre dos computadores en redes distintas**
(un Mac y un Windows) **solo por túneles HTTP de Cloudflare** —sin LAN, sin abrir
puertos, sin nada por TCP— y que el coordinador trata las respuestas remotas como
**datos no confiables**. Además endurecimos el sistema con **guardrails** de entrada,
salida y comunicación A2A, **resiliencia** ante agentes caídos y un **allow-list** de
agentes permitidos.

Como cierre, llevamos el agente más allá de la demo: lo dejamos **desplegado de forma
permanente en un VPS propio** con **HTTPS y URL fija** (`https://agente.etmk.cl`), con
auto-arranque por `systemd`, un **backoffice web** del log (`https://monitor.etmk.cl`) y un
**coordinador web** (`https://coordinador.etmk.cl`) con el que probamos, desde un mismo lugar en
producción, el ruteo a los agentes de los tres integrantes (Ezequiel, Tomás, Fabio, ProteinMAN y
Gustavo). Ver la sección **11.1**.

- **Stack:** uv + Python 3.13 · LangGraph (A2A nativo, `langgraph dev` en `:2024`) ·
  Gemini vía `langchain-google-genai` (embeddings `models/gemini-embedding-001`) ·
  Redis (redis-stack dockerizado) + `langchain-redis` para el RAG.
- **Repositorio (público):** https://github.com/etmunoz/tarea_1_curso_2
- **Pruebas:** `uv run pytest` → **148 passed, 1 skipped**.

## 1. Identificación

- **Curso 2 · Sesión 1** — Taller "tu skill es un agente y habla por A2A".
- **Grupo:** NN
- **Integrantes:**
  - Fabio Durán
  - Gustavo Reyes
  - Ezequiel Muñoz
- **Repositorio (público):** https://github.com/etmunoz/tarea_1_curso_2

> Nota sobre el stack: el enunciado del taller (`taller-a2a/`) describe un molde más
> viejo (un `server.py` en `:8003`, coordinador en `:8002`). Lo tradujimos al stack
> **real y vigente**: A2A **nativo** de LangGraph, donde los agentes son grafos
> declarados en `langgraph.json` y publicados por `langgraph dev`. Las ideas del taller
> (ficha, túnel, coordinador, ronda) se mantienen; cambia la plomería.

## 2. Blueprints (uno por integrante)

El *blueprint* es la ficha de diseño del agente (qué es, qué hace, qué no hace, qué
herramientas usa, a quién deriva, dónde se ejecuta).

- **Ezequiel · IA Engineer & Data Scientist** → [`blueprint-ezequiel.md`](../blueprint-ezequiel.md)
- **Fabio** → [`blueprint-fabio.md`](../blueprint-fabio.md) (agentes **Agente Fabio** + **ProteinMAN**) · diseño del sistema en [`blueprint-agentes.md`](../blueprint-agentes.md)
- **Gustavo** → [`blueprint-gustavo.md`](../blueprint-gustavo.md) (agente meteorólogo)

En este repositorio el grupo levantó **tres agentes** propios (Ezequiel, Tomás y
cocina). Tomás es el segundo agente del integrante Ezequiel, y existe para poder
**probar A2A entre los dos computadores** del grupo: en el Mac corre Ezequiel y en el
Windows corre Tomás.

## 3. Mi agente (Paso 3)

**Agente de Ezequiel** (`src/agente_ezequiel/`) — Ingeniero de IA y Data Scientist.
Recomienda qué técnica de machine learning usar, qué métricas mirar y qué modelo
elegir según el tipo de dato. Es un agente `create_agent` (LangGraph) con su **prompt
separado** del grafo y sus herramientas en `herramientas.py`:

- `recomendar_tecnica(problema)` — mapea un problema (p. ej. desbalance de clases) a
  una técnica y el porqué.
- `metricas_recomendadas(tipo_problema)` — qué métricas priorizar.
- `elegir_modelo(tipo_de_dato)` — modelo de arranque según el dato.
- `consultar_modelos(...)` — consulta un **catálogo de modelos en SQLite**
  (`bd_modelos.py`), de modo que el agente tiene conocimiento "conectado" a una base,
  no solo texto.

El grafo queda registrado en `langgraph.json` como `agente_ezequiel`. **Qué cambiamos
tras verlo funcionar:** separamos el prompt del código, y cuando una herramienta recibe
algo fuera de su catálogo responde en una línea con lo que sí cubre (nunca lanza error).

Los otros dos agentes del grupo:

- **Agente de cocina chilena** (`src/agente_cocina/`): 20 recetas chilenas con
  **costeo** desde SQLite. Herramientas: `listar_recetas`, `ver_receta`,
  `costear_receta` (costo por ingrediente, total y por persona, en CLP).
- **Agente de Tomás** (`src/agente_tomas/`): Maestro Reiki con **RAG sobre Redis**.
  Herramientas: `principios_reiki`, `posiciones_manos`, `info_simbolo` y `buscar_reiki`
  (búsqueda semántica sobre `data/reiki/*` indexado con embeddings de Gemini).

- **Prompt usado** para crearlo: `prompts_ejecutados/04-crear-agente-ezequiel.md`.

## 4. Probarlo solo (Paso 4)

Antes de sumarlo a la red, el agente se prueba aislado: responde a una pregunta **de su
tema** usando su herramienta y **rechaza** una de otro tema (no alucina fuera de dominio).

- Comandos y salida: `respuestas/04-crear-agente-ezequiel.md`; notebook paso a paso:
  `notebooks/ezequiel_paso_a_paso.ipynb`.
- **Evidencia:** `evidencias/01-saltos.png` — ronda real por el coordinador mostrando los
  "saltos" (pregunta → ruta del supervisor → respuesta `[Agente de …]`), incluido el
  rechazo (`sin_agente`) de una pregunta fuera de dominio.

## 5. La ficha / Agent Card (Paso 5)

La **Agent Card** es cómo un agente se presenta al mundo A2A: un JSON en
`/.well-known/agent-card.json` con `name`, `description` (qué sé / qué no hago) y
`skills`. El supervisor **decide a quién enrutar leyendo estas fichas**, así que una
buena descripción es clave.

Mecánica concreta en A2A nativo de LangGraph:

1. Cada grafo tiene un `assistant_id` (UUID) que se obtiene con
   `POST /assistants/search {"graph_id": "<grafo>"}`.
2. La ficha se **aplica** con `PATCH /assistants/<id>` poniendo `name` + `description`
   desde `src/fichas.py`. Lo hace `tools/configurar_fichas.py`.
3. Se **lee** en `GET /.well-known/agent-card.json?assistant_id=<id>`.

> Detalle operativo importante: `langgraph dev` **recarga en caliente** al cambiar
> archivos, y esa recarga **borra las fichas aplicadas**. Por eso, tras cualquier
> cambio hay que volver a correr `configurar_fichas.py`.

- **Evidencia:** `evidencias/02-ficha-agente_ezequiel.json` (y también
  `02-ficha-agente_tomas.json`, `02-ficha-agente_cocina.json`, `02-ficha-agente_viajes.json`).

## 6. Salir a internet · Cloudflare (Paso 6)

Para que el agente de un computador sea alcanzable desde **otra red**, lo exponemos con
un **túnel rápido de Cloudflare**:

```bash
cloudflared tunnel --url http://127.0.0.1:2024
```

Esto publica el `langgraph dev` local en una URL `https://<algo>.trycloudflare.com`,
**solo HTTP**, sin abrir puertos ni tocar el router. La URL es **efímera** (cambia en
cada corrida), así que los equipos se intercambian su URL al momento de la ronda.

Decisión de diseño del grupo: **todo** el tráfico entre máquinas va por túneles HTTP de
Cloudflare. No usamos la LAN ni nada por TCP: pensamos el escenario como "dos personas
en redes distintas". En particular, Tomás **no expone Redis**; expone únicamente su
agente (que por dentro usa su RAG). La **misma repo** sirve para ambos equipos: cambia
solo la configuración por variables de entorno.

- **Evidencia:** `evidencias/03-tunel.png` — la ficha del agente servida por la URL
  pública de Cloudflare (alcanzable desde internet).

## 7. Sumar a los compañeros · coordinador (Paso 7)

El **coordinador** (`src/coordinador/`) es un **supervisor** (patrón StateGraph, no
handoff): no responde él, **decide** a qué agente mandar la pregunta y reenvía por A2A.

Piezas:

- `catalogo.py` — arma el **catálogo** desde variables de entorno: `A2A_GRAFOS_LOCALES`
  (agentes del propio `langgraph dev`) y `URLS_AGENTES` (agentes de compañeros, cada uno
  por su túnel). Cada entrada marca si es **local** o **remoto** y resuelve su ficha
  (con caché por proceso y TTL, para no pedirla por el túnel en cada paso).
- `graph.py` — el grafo supervisor. El nodo `enrutar` usa
  `modelo.with_structured_output(Decision)` para elegir **exactamente un nombre del
  catálogo o "ninguno"**, guiado por las descripciones de las fichas. Luego `consultar`
  reenvía por A2A y **etiqueta** la respuesta como `[Nombre] …` (es un dato, no una
  instrucción). Si nadie cubre la pregunta, `sin_agente` lo dice con cortesía.
- `a2a.py` — cliente A2A genérico: `assistant_id`, `agent_card` y `enviar_mensaje`
  (`message/send` con `contextId` = UUID = hilo, para que el remoto recuerde su
  conversación).

Como es **bidireccional**: en el Mac el coordinador tiene locales a Ezequiel y cocina, y
remoto a Tomás (Windows); en el Windows es al revés (local Tomás, remotos Ezequiel y
cocina). El usuario no nota la diferencia entre local y remoto (**A2A transparente**).

- **Evidencia:** `evidencias/04-catalogo-mac.txt` y `04-catalogo-windows.txt` — el
  catálogo real de cada equipo (dos locales + un remoto), probado Mac ↔ Windows por
  Cloudflare, en redes distintas.
- Agentes ajenos a sumar por los compañeros: ver [`companeros.md`](companeros.md).

## 8. La ronda de preguntas (Paso 8)

Ronda real registrada en `evidencias/05-ronda-mac.md` y `05-ronda-windows.md`. Desde el
**Mac** (Ezequiel y cocina locales; Tomás remoto por Cloudflare):

| Pregunta | A quién enrutó el supervisor | ¿Estuvo bien? |
|---|---|---|
| ¿Qué técnica uso si tengo desbalance de clases? | [Agente de Ezequiel] (local) | sí |
| ¿Qué símbolos se aprenden en el nivel 2 de Reiki? | [Agente de Tomás] (**remoto**, por Cloudflare) | sí |
| ¿Cuánto cuesta un pastel de choclo para 4 personas? | [Agente de cocina chilena] (local) | sí |
| ¿Quién ganó el mundial de 1962? | sin_agente (fuera de dominio) | sí (lo rechaza bien) |

Desde el **Windows** la ronda es el **espejo** (Tomás local; Ezequiel y cocina remotos):
una pregunta de Reiki la responde Tomás local, y una de métricas de regresión o de
costear una cazuela se enruta a los agentes del Mac por Cloudflare.

- **Comentario:** el supervisor eligió correctamente por ficha; derivó al agente remoto
  (Tomás) por Cloudflare **sin que el usuario note la diferencia**, y rechazó con
  cortesía lo que ningún agente cubre. Con esto queda demostrada la operatividad A2A en
  **los dos sentidos**.
- **Evidencia:** `evidencias/05-ronda-mac.md`, `evidencias/05-ronda-windows.md`.

## 9. Cómo correr el proyecto

Requisitos: `uv`, Python 3.13, Docker (para el Redis del RAG) y una `GOOGLE_API_KEY` de
Gemini.

```bash
uv sync                       # instala dependencias (entorno reproducible)
cp .env.example .env          # pega tu GOOGLE_API_KEY en el .env (NUNCA se versiona)
docker compose up -d          # levanta Redis para el RAG de Tomás
uv run langgraph dev          # publica los grafos en http://127.0.0.1:2024
uv run python tools/configurar_fichas.py   # aplica las fichas (Agent Cards)
uv run pytest                 # pruebas: 70 passed, 1 skipped
```

Para la prueba entre dos computadores (plug and play por equipo):

- **Mac:** `scripts/mac_coordinador.sh "<túnel-windows>"` · `scripts/mac_app.sh` ·
  `scripts/mac_tunel.sh`.
- **Windows:** `scripts/win_coordinador.ps1 "<túnel-mac>"` · `scripts/win_app.ps1` ·
  `scripts/win_tunel.ps1`.

Hay además una **app web** mínima (stdlib, `src/webapp/`) para probar agentes uno a uno
o vía coordinador, y notebooks paso a paso en `notebooks/`. Guía completa: `taller-a2a/`.

## 10. Robustez (resiliencia + guardrails + allow-list)

Sobre el coordinador implementamos controles de robustez (prompts 44-47), cada uno con
pruebas y evidencia.

**(a) Agente remoto no disponible — resiliencia.** `src/coordinador/a2a.py` envuelve
toda petición HTTP y convierte conexión caída / timeout / HTTP inválido / JSON ilegible
en una excepción tipada `AgenteNoDisponible` (nunca deja escapar un error crudo). El
catálogo se **arma igual** marcando al agente caído como "(no disponible ahora)", y el
coordinador devuelve un **estado controlado**: «El Agente de X no está disponible
temporalmente (motivo). Puedes intentar nuevamente más tarde. Los demás agentes
continúan operativos.» Se probó **con el Windows realmente caído**.

**(b) Guardrails en tres puntos** (`src/coordinador/guardrails.py`):

- **Entrada** (`guardia_entrada`): rechaza preguntas vacías, excesivamente largas o con
  patrones de **inyección/jailbreak** (ES/EN), antes de gastar el LLM.
- **Salida** (`guardia_salida`, **nodo común a todos los caminos**): redacta credenciales
  (claves de API, tokens, contraseñas, tarjetas), aplica un tope de longitud y evita
  respuestas vacías. Que sea un nodo final garantiza que **ninguna** respuesta salga sin
  pasar por el control.
- **Comunicación A2A** (`sanear_respuesta_remota`): la respuesta de un agente remoto se
  trata como **dato no confiable**; si trae una instrucción incrustada, se marca "se
  muestra como dato y NO se obedece".

**(c) Allow-list de agentes** (`A2A_AGENTES_PERMITIDOS`): lista blanca explícita de los
grafos que el coordinador puede invocar (sus "tools"). Aunque `URLS_AGENTES` traiga un
túnel colado o mal configurado, **no se ejecuta** si no está aprobado. Si la variable no
se define, se permiten todos (compatibilidad hacia atrás).

El flujo del grafo resultante (ver `evidencias/07-grafo-coordinador.svg` y
`09-diagramas.md`):

```
__start__ → guardia_entrada → enrutar → {consultar | sin_agente} → guardia_salida → __end__
                   └──(bloqueado)──────────────────────────────────────┘
```

- **Pruebas:** `tests/test_resiliencia_a2a.py`, `tests/test_guardrails.py`,
  `tests/test_salida_y_allowlist.py`.
- **Evidencia:** `evidencias/06-robustez-mac.md` (resiliencia con túnel caído, batería de
  ataques de entrada detenidos, redacción de salida y allow-list excluyendo un intruso).

### Robustecimiento final (prompt 48, rama `prompt-48-robustez`)

- **Inexistente vs desconectado:** el catálogo conserva las capacidades de un agente desde su
  última ficha conocida, así el supervisor distingue "no hay agente para esto" (`sin_agente`) de
  "el especialista existe pero está temporalmente caído" (`agente_no_disponible`).
- **Guardrails por capas:** validación de tipos (entrada y salida), normalización, y una política
  configurable para respuestas remotas (`GUARDRAIL_POLITICA_A2A`: ALLOW / SANITIZE / BLOCK), con
  observabilidad (eventos sin guardar contenido sensible). *No se promete protección infalible:*
  la detección es heurística y puede tener falsos positivos/negativos.
- **Autenticación/autorización A2A (`src/coordinador/auth.py`):** autorización por mínimo
  privilegio (grafo + operación) y token Bearer en el cliente. **Honesto:** un allow-list **no es
  autenticación**; la validación efectiva del token requiere habilitarla en el receptor (se deja
  como referencia + modo demo). Límite registrado.
- **Robustez del cliente A2A:** jerarquía de excepciones (`ErrorA2A` → `AgenteNoDisponible`,
  `ErrorProtocoloA2A`, `RespuestaA2AInvalida`, `IdentificadorAsistenteObsoleto`), validación
  estructural del JSON y **recuperación de `assistant_id` obsoleto** (404 → recargar → reintentar
  una vez, sin bucles).
- **Pruebas:** `tests/test_robustez_a2a_48.py`, `tests/test_guardrails_auth_48.py`.
  **Evidencia:** `evidencias/11-robustez-48-mac.md`.
- **Ajustes finales (prompt 48a):** validación exhaustiva de respuestas A2A (sin excepciones de
  programación ante estructuras inesperadas), autenticación uniforme en el descubrimiento
  (`401/403` diferenciados; no se clasifica a ciegas), recuperación acotada del `assistant_id`,
  disponibilidad por **sondeo fresco** (la ficha cacheada no prueba conectividad) y
  ALLOW/SANITIZE/BLOCK por **acción efectiva**. Pruebas: `tests/test_ajustes_48a.py`.

## 11. Arquitectura y diagramas

- `evidencias/07-grafo-coordinador.svg` — el grafo del coordinador (con los guardrails).
- `evidencias/08-arquitectura.svg` — la arquitectura completa: Mac (Ezequiel, cocina,
  viajes) y Windows (Tomás + RAG en Redis), cada uno con su `langgraph dev`, coordinador
  y app web, unidos por túneles HTTP de Cloudflare (A2A bidireccional).
- `evidencias/09-diagramas.md` — índice con el **mermaid auténtico** del grafo (extraído
  del grafo compilado) + los dos SVG.

## 11.1 Despliegue permanente en un VPS (`agente.etmk.cl`)

Además de la demo por túneles efímeros (Mac ↔ Windows ↔ Gustavo), dejamos **nuestro
Agente de Ezequiel publicado de forma permanente** en un VPS propio (Ubuntu 24 + ISPConfig,
dominio `etmk.cl`), con **HTTPS y URL fija** — así los compañeros lo consumen sin depender
de que una máquina esté encendida ni de túneles que caducan.

**URLs permanentes:**

| Qué | URL |
|---|---|
| Agente (A2A, JSON-RPC `message/send`) | `https://agente.etmk.cl` |
| Agent Card (ficha) | `https://agente.etmk.cl/.well-known/agent-card.json` |
| Backoffice web (login) | `https://monitor.etmk.cl` (usuario `monitor` + clave) |
| Coordinador web (login) | `https://coordinador.etmk.cl` (usuario `coordinador` + clave) |

**Arquitectura del despliegue (cadena de 3 capas, todo en el VPS):**

```
Internet → Apache (reverse proxy + Let's Encrypt, :443)
        → Puente A2A clásico (Python http.server, 127.0.0.1:8790, guardrails + log de accesos)
        → langgraph dev (uvicorn/ASGI, 127.0.0.1:2024) → agente_ezequiel / agente_cocina → Gemini
```

- El agente escucha **solo en `127.0.0.1`**; se publica por Apache con **certificado Let's Encrypt**
  (ver `evidencias/17-despliegue-vps.svg`).
- **Persistencia real:** cinco servicios **`systemd`** (`agente-langgraph`, `agente-fichas`,
  `agente-puente`, `agente-monitor`, `agente-coordinador`), `enabled` (arrancan al bootear) y
  `Restart=always` (reviven si se caen). **Probado con un reinicio** del servidor: volvieron solos.
  `agente-fichas` corre `configurar_fichas.py --vigilar` y re-aplica las Agent Cards cuando
  `langgraph dev` las borra al hot-reload, reemplazando el paso manual del taller.
- **Coordinador web** (`tools/coordinador_web.py`, `https://coordinador.etmk.cl`): chat del
  coordinador A2A con panel de ruteo y configuración de las URLs de cada agente (Ezequiel, Tomás,
  Fabio, Gustavo y **ProteinMAN**). Muestra los **antecedentes del acceso** (local/remoto, grafo,
  endpoint, host, IP), guarda el ruteo por respuesta y puede enviar correo desde `coordinador@etmk.cl`
  (allowlist, solo por acción del usuario). Detrás de HTTPS + Basic Auth. Evidencias en
  `evidencias/evidencias_coordinador.md`.
- **Backoffice web** (`tools/monitor_web.py`): la misma traza del log de accesos que el monitor Tkinter,
  pero en el navegador, autorefrescante y protegida con **HTTP Basic Auth** (detrás de HTTPS).
- **Seguridad del despliegue:** MySQL atado a `127.0.0.1`, el token `A2A_TOKEN` nunca se envía a
  terceros, y los avisos de seguridad no verificados **no se ejecutan**. El `.env` (con la
  `GOOGLE_API_KEY`) vive fuera del docroot público, permisos `600`, nunca en git.
- **Receta reproducible:** toda la infraestructura del servidor (units `systemd`, plantillas de
  entorno sin secretos, proxy + force-HTTPS y pasos de despliegue) está versionada en
  [`deploy/`](../deploy/) — ver [`deploy/README.md`](../deploy/README.md). La historia detallada del
  montaje (acceso, persistencia, HTTPS, hardening, correo, coordinador web y pruebas cross-machine)
  está en [`deploy/BITACORA-SERVIDOR.md`](../deploy/BITACORA-SERVIDOR.md).

## 12. Limitaciones y trabajo futuro

Este trabajo es un prototipo funcional y honesto; dejamos registradas sus limitaciones
y cómo se extendería.

**Limitaciones actuales:**

- **Túneles efímeros (en la demo).** Para la ronda Mac ↔ Windows ↔ Gustavo usamos *quick
  tunnels* de Cloudflare (`trycloudflare.com`): la URL cambia en cada corrida y no tiene
  autenticación ni DNS fijo. **Ya resuelto para nuestro agente** con el despliegue permanente
  del **§11.1** (`https://agente.etmk.cl`, HTTPS y URL fija); los túneles quedan solo para la
  demo entre equipos.
- **Fichas volátiles.** `langgraph dev` recarga en caliente y **borra las Agent Cards**; en
  la demo se recuperan con `configurar_fichas.py` (modo `--vigilar`). En el VPS (§11.1) el
  servicio `systemd` las **reaplica solo** tras cada arranque.
- **Datos simulados.** Varios catálogos (técnicas/modelos de Ezequiel, precios de cocina)
  son datos de ejemplo, no fuentes de producción.
- **Guardrails heurísticos.** La detección de inyección/jailbreak y de secretos es por
  **expresiones regulares**: cubre los casos comunes, pero no es exhaustiva; un atacante
  decidido podría redactar algo fuera de los patrones. No hay clasificador semántico.
- **Enrutado dependiente del LLM.** El supervisor usa Gemini para elegir agente; en
  preguntas ambiguas puede equivocarse, y no hay reintento ni confirmación.
- **Memoria no persistente.** El estado por hilo usa `InMemorySaver`: se pierde al
  reiniciar el servidor.
- **Allow-list grueso.** La lista blanca es por **agente/grafo**, no por herramienta fina
  dentro de un agente; y no hay autenticación ni firma entre agentes A2A.
- **Pendientes de entrega.** Número de grupo como marcador (`NN`), blueprints de Fabio y
  Gustavo por completar, y el email del commit `4c89013` quedó en el historial por
  decisión del grupo (ver `respuestas/40-…`).

**Trabajo futuro:**

- **Túnel con identidad:** *named tunnel* + dominio propio y **Cloudflare Access**
  (autenticación) en lugar del túnel efímero.
- **Autenticación A2A:** tokens/firmas entre agentes y allow-list **por skill/herramienta**,
  no solo por agente.
- **Guardrails reforzados:** clasificador LLM/ML para inyección y PII, políticas de salida
  más ricas, *rate limiting* y **auditoría** (log de bloqueos y redacciones).
- **Resiliencia extra:** reintentos con *circuit-breaker*, *health-check* periódico del
  catálogo y caché de respuestas.
- **Persistencia:** *checkpointer* en Redis/SQLite para que la memoria de los hilos
  sobreviva reinicios.
- **Observabilidad:** trazas (LangSmith) y métricas de enrutamiento (aciertos del supervisor).
- **Datos reales:** reemplazar los catálogos simulados por fuentes reales (p. ej. un
  *tracking* de experimentos para Ezequiel, una base de precios para cocina).
- **CI:** GitHub Actions corriendo `pytest` + `aplicar_encabezados.py --check` en cada push.

## 13. Evidencias incluidas

Lista y cómo producir cada una: `evidencias/README.md`.

- `01-saltos.png`, `03-tunel.png` — generadas desde la corrida real (coordinador y túnel).
- `02-ficha-agente_*.json` — Agent Cards aplicadas.
- `04-catalogo-mac.txt`, `04-catalogo-windows.txt` — catálogo del coordinador en cada equipo.
- `05-ronda-mac.md`, `05-ronda-windows.md` — ronda de preguntas en cada equipo (A2A bidireccional).
- `06-robustez-mac.md` — resiliencia + guardrails + allow-list (prompts 44-47).
- `07-grafo-coordinador.svg`, `08-arquitectura.svg`, `09-diagramas.md` — diagramas.
- `10-interop-puente-mac.md` — puente al dialecto A2A clásico (para que un cliente estándar
  nos consuma).
- `11-robustez-48-mac.md` — robustecimiento final (resiliencia, guardrails, auth/authz, allow-list).
- `12-backoffice-monitor-mac.svg` — monitor del puente (quién consume el agente).
- `13-interop-gustavo-mac.md` — interoperabilidad nosotros → agente de Gustavo (dialecto `SendMessage`).
- `14-ronda-mac-windows-gustavo-mac.md` — ronda end-to-end con los tres orígenes por A2A.
- `15-backoffice-tomas-mac.md` + `15-backoffice-tomas.png` — el monitor de Tomás (Windows)
  registrando, en vivo, el tráfico entrante desde el Mac.

## 14. Convenciones y trazabilidad del grupo

- **Encabezado de grupo** en todo archivo que admite comentarios (verificado con
  `tools/aplicar_encabezados.py --check`).
- **Cada prompt** queda registrado en `prompts_ejecutados/NN-slug.md` y **cada
  respuesta** (con la salida real, lo que funciona y lo que falla) en
  `respuestas/NN-slug.md`, indexados en `prompts_ejecutados/README.md`. A la fecha de
  esta entrega hay **47 prompts** registrados.
- **Seguridad:** el `.env` real (con la clave) **nunca** se versiona (`.gitignore`); la
  `GOOGLE_API_KEY` no aparece en el repositorio.
