# Compartir los agentes con Cloudflare (quick tunnel) · Debian

Sirve para que tus compañeros, desde su computador, consulten tus agentes por A2A. Es el extra opcional del enunciado.
Un *quick tunnel* no necesita cuenta. La URL `https://….trycloudflare.com` **cambia cada vez** que lo levantas y
**muere** cuando cierras la terminal.

## 0 · Antes de abrir el túnel
- Cualquiera que tenga la URL puede usar **toda** la API de LangGraph de tu servidor: mandar mensajes (eso
  **consume tu cuota de Gemini**), leer los hilos y hasta cambiar la tarjeta. Usa datos de prueba, comparte la URL
  solo durante la clase y ciérrala con `Ctrl+C` al terminar.
- No hace falta abrir puertos ni tocar el firewall: `cloudflared` sale hacia Cloudflare, no recibe conexiones.

## 1 · Instalar `cloudflared` (una sola vez)
Repositorio oficial de Cloudflare. La distribución `any` funciona en Debian 13 (trixie) y también en testing/sid:
```bash
sudo mkdir -p --mode=0755 /usr/share/keyrings
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' \
  | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt-get update && sudo apt-get install -y cloudflared
cloudflared --version
```
Sin repositorio: descarga `cloudflared-linux-amd64.deb` desde
https://github.com/cloudflare/cloudflared/releases/latest e instálalo con `sudo apt install ./cloudflared-linux-amd64.deb`.

## 2 · Levantar los agentes (una terminal cada uno)
```bash
cd ~/Nextcloud/estudio/cursos/agente-IA/curso2/taller1/entrega/mi-agente
source .venv/bin/activate && langgraph dev --port 2025 --no-browser
```
```bash
cd ~/Nextcloud/estudio/cursos/agente-IA/curso2/taller1/entrega/segundo-agente
source .venv/bin/activate && langgraph dev --port 2026 --no-browser
```
Comprueba: `curl http://127.0.0.1:2025/ok` y `curl http://127.0.0.1:2026/ok` → `{"ok":true}`.

## 3 · Abrir los túneles (otra terminal por agente)
Usa **`127.0.0.1`** y no `localhost`. `langgraph dev` escucha solo en IPv4 (127.0.0.1), y en Debian `localhost`
también resuelve a `::1` (IPv6), lo que puede hacer fallar el túnel.
```bash
cloudflared tunnel --url http://127.0.0.1:2025     # Agente Fabio
```
```bash
cloudflared tunnel --url http://127.0.0.1:2026     # ProteinMAN (solo si también quieres compartirlo)
```
Cada una imprime una línea del tipo `https://palabras-al-azar.trycloudflare.com`. Esa es la URL que compartes.

## 4 · Probar desde fuera, antes de pasar la URL
```bash
URL=https://palabras-al-azar.trycloudflare.com
curl -s $URL/ok
AID=$(curl -s -X POST $URL/assistants/search -H 'Content-Type: application/json' -d '{"graph_id":"agente_fabio"}' \
      | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['assistant_id'])")
curl -s "$URL/.well-known/agent-card.json?assistant_id=$AID" | python3 -m json.tool | head -20
```
Si la tarjeta muestra `"name": "Agente Fabio"`, el túnel funciona. Si muestra `agente_fabio`, ejecuta antes la celda
de la tarjeta del notebook.

## 5 · Qué hace tu compañero
En su notebook, en el bloque 1 de «Ejemplo real», agrega tu URL a `SERVIDORES` y vuelve a ejecutar el bloque:
```python
SERVIDORES = [
    "http://127.0.0.1:2025",                          # su propio agente
    "https://palabras-al-azar.trycloudflare.com",     # el Agente Fabio (tu túnel)
]
```
El bloque reescribe la URL de la tarjeta (`interfaz.url = f"{base}/a2a/{aid}"`). Esto es necesario porque tu
servidor anuncia `http://127.0.0.1:2025/...`, que en su máquina no existe. Si tu compañero usa otro cliente que no
reescribe esa URL, tiene que mandar los mensajes a `https://…trycloudflare.com/a2a/<assistant_id>`.

Condiciones: los grafos y las tarjetas deben tener nombres distintos a los suyos (por ejemplo, si él también se
llama «Agente Fabio», el bloque falla con «Nombre repetido»).

## 6 · Al terminar
`Ctrl+C` en cada terminal de `cloudflared` y de `langgraph dev`. La URL deja de funcionar en ese momento.

## Atajo
`bash lanzar.sh` (en la raíz del taller) hace los pasos 2 a 4 solo: levanta los dos agentes, aplica sus
tarjetas, abre los túneles, verifica la tarjeta desde fuera e imprime el bloque `SERVIDORES` listo para copiar.
Con `--puente`, cada túnel pasa por `herramientas/puente.py` y cualquier cliente A2A estándar puede usar la URL
directamente: la tarjeta se sirve sin `assistant_id` y los mensajes se reciben en `POST /`.
