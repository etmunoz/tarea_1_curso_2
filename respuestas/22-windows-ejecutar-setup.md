<!--encabezado-grupo-->
> **Archivo:** `respuestas/22-windows-ejecutar-setup.md`  
> **Objetivo:** 22 · Respuesta — Windows: ejecutar `setup_windows.ps1` (clave Gemini y AVG)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2208 · **Última modificación:** 20261110 2340
<!--/encabezado-grupo-->

# 22 · Respuesta — Windows: ejecutar `setup_windows.ps1` (clave Gemini y AVG)

Prompt: [`../prompts_ejecutados/22-windows-ejecutar-setup.md`](../prompts_ejecutados/22-windows-ejecutar-setup.md)

## Qué se hizo (cronología)

1. **1ª corrida** en una terminal interactiva:
   `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1`
   - Pasos 1/6 y 2/6 OK: Python 3.13 y 134 paquetes instalados con `uv sync`.
   - Paso 3/6: creó `.env` y quedó esperando `Pega tu GOOGLE_API_KEY`.
2. El usuario pegó la clave **directamente en `.env`**. Se comprobó (sin mostrarla) que estaba.
   - ⚠ **Riesgo encontrado:** si se presionaba Enter vacío en el prompt, el script reemplaza
     `GOOGLE_API_KEY=...` por `GOOGLE_API_KEY=` y **borra la clave recién puesta**
     (`setup_windows.ps1`, línea del `-replace`). Por eso se canceló esa corrida con Ctrl+C,
     se verificó que la clave seguía intacta y se volvió a correr (con clave presente, el
     script se salta la pregunta).
3. **2ª corrida:** en el paso 4/6 la prueba de Gemini se quedó **reintentando** (tenacity) y el
   usuario la cortó con Ctrl+C (`KeyboardInterrupt`).
4. **Diagnóstico:** una llamada REST directa a Gemini (urllib, sin reintentos) respondió
   **HTTP 200 "OK"** → la clave es válida. La 3ª corrida mostró el error real:
   `[SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer certificate`.
5. **Causa raíz:** el certificado que recibe Python para `generativelanguage.googleapis.com`
   lo emite **"AVG Web/Mail Shield Root"** (AVG Antivirus inspecciona HTTPS). Windows confía
   en esa raíz (por eso urllib funcionó), pero la librería `google-genai` usa el paquete
   **certifi**, que no la incluye.
6. **Prueba temporal** (sin tocar nada del proyecto): bundle certifi + `C:\ProgramData\AVG\Antivirus\wscert.pem`
   en `SSL_CERT_FILE` → Gemini respondió. Queda como alternativa si no se quiere tocar AVG.
7. **Arreglo definitivo (hecho por el usuario en AVG):** Menú → Configuración → General →
   Excepciones → agregar `https://generativelanguage.googleapis.com/*` y
   `https://*.trycloudflare.com/*` (esta segunda para cuando el coordinador llame al túnel del Mac).
8. Con la excepción, `uv run python tools/probar_gemini.py` → `✓ Gemini respondió: 'OK'`.
9. El paso 5/6 (Redis) **falló**: `Bind for 0.0.0.0:6379 failed: port is already allocated` → ver prompt 23.

## Lo bueno

- uv, Python 3.13 y dependencias quedaron instalados en una sola pasada.
- La clave de Gemini es válida y, con la excepción de AVG, funciona sin parches.

## Lo malo / lo que no resultó

- La prueba de Gemini con error SSL **reintenta largo rato** antes de fallar; parece colgada.
- `probar_gemini.py` falla al imprimir `✓`/`✗` cuando la salida va a un pipe con cp1252
  (`UnicodeEncodeError`); se evita con `PYTHONIOENCODING=utf-8`. En la consola normal se ve bien.
- Avisos `SyntaxWarning: invalid escape sequence '\/'` de `google/genai/types.py`: son de la
  librería, inofensivos.
- El script sigue al paso 5 aunque el 4 falle (los comandos nativos no detienen el script en PS 5.1).

## Lo que se arregló

| Problema | Arreglo |
|---|---|
| Enter vacío borraría la clave | Se canceló el prompt y se re-corrió con la clave ya en `.env` |
| SSL por AVG | Excepción de URL en AVG (alternativa probada: `SSL_CERT_FILE` con bundle) |

## Pendiente sugerido

- Que `setup_windows.ps1` no sobrescriba la clave si la respuesta viene vacía.
- Agregar a la guía (sección *Problemas típicos*) el caso de antivirus con inspección HTTPS.

---

## Respuestas completas del asistente (chat)

### A «luego debes ejecutar .\scripts\setup_windows.ps1»

**Mensaje de avance:**

> Ejecuto el setup en una pestaña de terminal, para que puedas pegar tu clave ahí cuando la pida.

**Respuesta final:**

> El setup está en marcha en la pestaña *setup windows* y se detuvo en el paso 3 de 6, que
> pide tu clave de Gemini.
>
> - **Pasos 1 y 2:** ya terminaron. Quedaron instalados Python 3.13 y las 134 dependencias.
> - **Paso 3:** se creó `.env` a partir de `.env.example`. Ahora el script espera la línea
>   `Pega tu GOOGLE_API_KEY (Gemini, la misma del Mac):`.
>
> **Lo que tienes que hacer:** abre esa pestaña, pega tu clave y presiona Enter. La clave
> queda guardada solo en `.env`, que git no sube al repositorio. Yo no la escribo por ti.
>
> Después el script sigue solo: prueba la clave de Gemini, levanta Redis con Docker y carga
> el RAG de Reiki. Cuando me avises, reviso la salida.
>
> Para que el script corriera usé `-ExecutionPolicy Bypass` solo en esta ejecución, sin
> cambiar ningún ajuste de tu sistema. Los acentos se ven mal en la consola ("Â·") porque el
> `.ps1` no tiene BOM, como te comenté antes. Por ahora es solo un problema de visualización.

### A «ya la agregué al .env directamente» y «lo paré yo»

**Mensajes de avance (traducidos; en el chat salieron en inglés):**

> La clave está en `.env`, pero el script sigue esperando en la pregunta. Si presionas Enter
> ahí sin escribir nada, el script va a sobrescribir tu clave con un valor vacío. Cancelo esa
> ejecución y la vuelvo a correr; esta vez ve la clave y se salta la pregunta.

> La prueba de Gemini se interrumpió mientras reintentaba una solicitud fallida. Reviso el
> formato de la clave (sin mostrarla) y el error real.

> Entendido, la paraste tú. Mientras reintentaba encontré algo útil: tu clave empieza
> distinto a las claves estándar de Google AI Studio. Hago una llamada directa, sin
> reintentos, para ver el error exacto.

> La clave funciona: Gemini respondió "OK" (HTTP 200). El reintento anterior probablemente
> fue un error temporal de Google. Vuelvo a correr el setup.

> Redis se está descargando. Mientras tanto reviso el error SSL: mi llamada directa
> funcionó, pero la llamada de la librería de Gemini falla.

> La causa es **AVG Antivirus**. Su "Web/Mail Shield" intercepta el tráfico HTTPS y vuelve a
> firmar los certificados con su propia raíz. Windows confía en esa raíz, pero la librería de
> Gemini usa su propia lista de certificados (certifi), que no la incluye. Pruebo un arreglo
> que no cambia nada de forma permanente: un paquete combinado (certifi + raíz de AVG) en una
> carpeta temporal.

### A «dime qué excepcion pongo en AVG»

**Respuesta final:**

> El error SSL lo causa AVG y no tu clave. AVG intercepta las conexiones HTTPS para
> revisarlas, y la librería de Gemini que usa Python no reconoce el certificado de AVG. Por
> eso hay que excluir las direcciones que usa el proyecto.
>
> **Qué excepción agregar en AVG**
> 1. Abre AVG y ve a **Menú ☰ → Configuración → General → Excepciones**.
> 2. Haz clic en **Agregar excepción** y escribe estas direcciones, una por una:
>    - `https://generativelanguage.googleapis.com/*`: Gemini, la usan los agentes y la prueba de la clave.
>    - `https://*.trycloudflare.com/*`: los túneles. Hace falta cuando tu coordinador o la app
>      llamen al túnel del Mac, porque fallaría por el mismo motivo.
> 3. Guarda los cambios.
>
> **Si el error sigue después de agregarlas:** en algunas versiones de AVG las excepciones de
> URL no desactivan la revisión de HTTPS. En ese caso, en **Protección básica → Escudo web**,
> desmarca **Habilitar análisis HTTPS**. Esto desactiva la revisión de HTTPS para todo el
> equipo, no solo para estas direcciones, así que decide tú si te parece bien.
>
> **Alternativa sin tocar AVG**
> Hice una prueba que no dejó ningún cambio permanente y funcionó: Gemini respondió. Junté
> los certificados normales de Python con el certificado de AVG en un solo archivo y le
> indiqué a Python que lo usara. Para dejarlo fijo, guardaría ese archivo dentro del proyecto,
> sin subirlo a git, y agregaría una línea `SSL_CERT_FILE=...` en tu `.env`.
>
> **En qué va el setup**
> En la pestaña *setup windows 2* se está descargando la imagen de Redis: 188 de 373 MB,
> paso 5 de 6. Después viene la carga del RAG de Reiki, que probablemente falle por el mismo
> problema SSL. Cuando esté resuelto, vuelvo a correr la prueba de Gemini y la carga del RAG.

### A «Ya la agregué»

**Mensajes de avance (traducidos):**

> La excepción de AVG funciona: Gemini responde sin ningún ajuste extra. Ahora espero a que
> Redis termine y se cargue el RAG.

> Redis no arrancó: el puerto 6379 ya está ocupado. Reviso qué lo está usando.

*(La respuesta final de este turno se registra en el prompt 23, porque el usuario pidió
cambiar el puerto mientras se trabajaba.)*
