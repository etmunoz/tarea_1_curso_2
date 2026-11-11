<!--encabezado-grupo-->
> **Archivo:** `taller-a2a/04-probarlo-solo-antes-de-conectarlo.md`  
> **Objetivo:** Probarlo solo, antes de conectarlo  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1450 · **Última modificación:** 20261111 0735
<!--/encabezado-grupo-->

<!-- clase: Taller · tu skill es un agente y habla por A2A · 61408ca1 | sección: sf8f5c9 | slide 4/10 · Parte 1 · Tu agente -->

Parte 1 · Tu agente · Paso 4 · terminal

# Probarlo solo, antes de conectarlo

Primero sin servidor, con `--saltos`, para ver que llama a tu herramienta y que rechaza lo que no es de tu tema. Después levantado en tu puerto, con la ficha y un mensaje, igual que en el paso 6 de la clase.

**terminal · --saltos y --diagrama**

```markdown
# sin servidor, desde la raíz y con el .venv activo (cambia "jose" por tu nombre)
python main.py jose "¿Está caída la VPN?" --saltos
# → model : llama a estado_servicio(servicio="vpn")
# → tools : "degradado: latencia alta desde las 09:00"
# → model : respuesta final
# Saltos: 3 · Herramientas: estado_servicio

python main.py jose "¿Qué vuelos hay a Lima?"
# → "Eso no es de mi especialidad: yo veo TI y soporte técnico."

python main.py jose --diagrama
# graph TD;  __start__ --> model;  model -. tools .-> tools;  tools --> model;  model -. end .-> __end__
```

## Mac / Linux

**terminal · servidor, ficha y mensaje**

```markdown
# terminal 1 · levantar tu agente en el 8003
uvicorn src.agente_jose.server:app --port 8003 --reload

# terminal 2 · la ficha
curl -s http://127.0.0.1:8003/.well-known/agent-card.json | python3 -m json.tool

# terminal 2 · un mensaje
CTX=$(python3 -c "import uuid; print(uuid.uuid4())")
curl -s -X POST http://127.0.0.1:8003/ -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":\"1\",\"method\":\"message/send\",\"params\":{\"message\":{\"role\":\"user\",\"messageId\":\"m1\",\"contextId\":\"$CTX\",\"parts\":[{\"kind\":\"text\",\"text\":\"¿Está caída la VPN?\"}]}}}" | python3 -m json.tool
```

## Windows · PowerShell

**powershell · servidor, ficha y mensaje**

```markdown
# terminal 1 · levantar tu agente en el 8003
uvicorn src.agente_jose.server:app --port 8003 --reload

# terminal 2 · la ficha
Invoke-RestMethod http://127.0.0.1:8003/.well-known/agent-card.json | ConvertTo-Json -Depth 10

# terminal 2 · un mensaje
$ctx = [guid]::NewGuid().ToString()
$cuerpo = @{ jsonrpc="2.0"; id="1"; method="message/send"; params=@{ message=@{ role="user"; messageId="m1"; contextId=$ctx; parts=@(@{ kind="text"; text="¿Está caída la VPN?" }) } } } | ConvertTo-Json -Depth 10
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8003/ -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($cuerpo)) | ConvertTo-Json -Depth 10
```

- **Qué mirar:** en `--saltos`, que aparezca tu herramienta por su nombre. En la ficha, tu nombre en `name`. En la respuesta, el texto dentro de `artifacts`.

- **Si responde cosas de otro tema,** el problema está en `prompts.py`: la regla “si no es de tu tema, dilo en una frase” tiene que estar clara.

- **Si la herramienta no se llama,** revisa el docstring de la función en `tools.py`: es lo que el modelo lee para decidir usarla.

Entregables de este paso

- `evidencias/01-saltos.png`: la captura de `--saltos` con una pregunta de tu tema (se ve tu herramienta) y una de otro tema (la rechaza).
- La salida de `--diagrama` pegada en el documento.
- La respuesta del mensaje por curl o PowerShell, con el texto dentro de `artifacts`.

**Lo logré ✓** Mi agente contesta por A2A en mi puerto y rechaza lo que no es de mi tema.
