<!--encabezado-grupo-->
> **Archivo:** `respuestas/28-windows-verificar-tunel.md`  
> **Objetivo:** 28 · Respuesta — Windows: verificar el túnel de Cloudflare del agente Tomás  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2220 · **Última modificación:** 20261110 2349
<!--/encabezado-grupo-->

# 28 · Respuesta — Windows: verificar el túnel de Cloudflare del agente Tomás

Prompt: [`../prompts_ejecutados/28-windows-verificar-tunel.md`](../prompts_ejecutados/28-windows-verificar-tunel.md)

## Qué se hizo

Se probó la URL pública desde Python (`httpx`), que además verifica la excepción de AVG para
`*.trycloudflare.com` (ver prompt 22):

```text
Túnel: https://delays-therapeutic-wait-yeast.trycloudflare.com   (temporal: cambia si se reinicia)

GET  /ok                                   -> 200 {"ok":true,...}
POST /assistants/search (agente_tomas)     -> acc5c687-67ca-54db-9228-766f2302e8b3
GET  /.well-known/agent-card.json          -> «Agente de Tomás»
POST /a2a/<id>  message/send               -> estado: completed, sin error
  "¿Qué significa Shoden en Reiki?"
  → "Shoden corresponde al primer nivel de Reiki, conocido como "El principio", y su foco se
     centra en el cuerpo físico y el autotratamiento. A través de las iniciaciones del
     maestro, este nivel abre el canal de energía del alumno para practicar la sanación."
```

La respuesta usa el contenido de `data/reiki/nivel-1-shoden.md` → el RAG sobre el Redis local
(puerto 6380) funciona también cuando se consulta desde afuera.

## Lo bueno

- Túnel en pie en el nodo Cloudflare de Santiago (`scl02`), protocolo QUIC.
- Agente, ficha y A2A responden por la URL pública; la excepción de AVG cubre `trycloudflare.com`.

## Lo malo / observaciones

- `ERR Failed to dial a quic connection … timeout`: el **primer** intento falló; cloudflared
  reintentó, los pre-chequeos salieron todos `PASS` y la conexión quedó registrada. No requiere acción.
- `cloudflared does not support loading the system root certificate pool on Windows`: aplica a
  orígenes HTTPS; nuestro origen es `http://127.0.0.1:2024`, así que no afecta.
- La ficha publicada anuncia `url: http://127.0.0.1:2024/a2a/…` (la dirección local, no la del
  túnel). El coordinador arma la URL con `URLS_AGENTES=<túnel>#agente_tomas`, así que no lo
  afecta; un cliente que use al pie de la letra el campo `url` de la ficha sí fallaría.
- La URL `trycloudflare.com` es temporal: si se cierra la terminal del túnel, cambia y hay que
  mandarle la nueva al Mac.

## Estado

Nodo Windows listo para la prueba entre los dos PC. Siguiente: mandar la URL del túnel a
Ezequiel (Mac), pedirle la suya y correr `win_coordinador.ps1 "https://<tunel-mac>"`
(antes, arreglar el BOM de los `.ps1`).

---

## Respuesta completa del asistente (chat)

### Mensajes de avance

> El túnel quedó registrado (conexión `scl02`, protocolo QUIC). El error de QUIC del principio
> fue un reintento que después se conectó bien. Verifico la URL pública con Python (httpx),
> que además prueba la excepción de AVG para `trycloudflare.com`.

> El túnel funciona desde internet, con respuesta A2A completa. Registro esto como el prompt 28.

### Respuesta final

> El túnel funciona: la URL pública `https://delays-therapeutic-wait-yeast.trycloudflare.com`
> llega a tu agente, y Tomás contestó por A2A desde internet («Shoden corresponde al primer
> nivel de Reiki…»), usando el RAG.
>
> El error de QUIC del inicio fue solo un primer intento fallido; cloudflared reintentó y se
> conectó. El aviso de certificados no aplica, porque el túnel apunta a `http` local.
>
> Siguiente: manda esa URL a Ezequiel para el Mac y pídele la suya. Mantén abierta la terminal
> del túnel, porque si la cierras la URL cambia. Antes de correr el coordinador arreglo la
> codificación de los `.ps1`.

### A «pero dime la URL que no la vi en la salida o no se como identificarla»

> Tu URL del túnel es:
>
> **`https://delays-therapeutic-wait-yeast.trycloudflare.com`**
>
> **Cómo reconocerla en la salida de `win_tunel.ps1`:** aparece casi al principio, dentro de
> un recuadro hecho con `+----+` y `|`, justo debajo de la línea *"Your quick Tunnel has been
> created! Visit it at…"*. Siempre empieza con `https://` y termina en `.trycloudflare.com`;
> lo del medio son cuatro palabras al azar separadas por guiones. Es la única línea de la
> salida con esa terminación.
>
> **Qué le mandas a Ezequiel:** solo esa URL, sin `/` al final. Él la usa en el Mac así:
> `./scripts/mac_coordinador.sh "https://delays-therapeutic-wait-yeast.trycloudflare.com"`.
>
> **Ojo:** si cierras esa terminal o se reinicia el túnel, sale una URL nueva con otras
> palabras, y hay que mandarla de nuevo.
