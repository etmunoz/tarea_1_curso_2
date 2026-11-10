<!-- --8<-- encabezado-grupo
Archivo: taller-a2a/03-mi-agente-con-mi-skill.md
Objetivo: Mi agente, con mi skill
Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
Creación: 20261110 1450
Última modificación: 20261110 1934
--8<-- fin-encabezado-grupo -->

<!-- clase: Taller · tu skill es un agente y habla por A2A · 61408ca1 | sección: sf8f5c9 | slide 3/10 · Parte 1 · Tu agente -->

Parte 1 · Tu agente · Paso 3 · prompt 1

# Mi agente, con mi skill

El molde es el agente de viajes: cuatro archivos y nada más. Cambias los datos, el rol y el nombre. Antes de pegar el prompt, reemplaza **NOMBRE** y ** ESPECIALIDAD** por los de tu blueprint.

**prompt 1 · copiar y pegar en OpenCode (cambia NOMBRE y ESPECIALIDAD)**

```
Quiero crear un agente nuevo que represente lo que yo sé hacer. Mi nombre es NOMBRE y mi especialidad es ESPECIALIDAD (por ejemplo: TI, redes y soporte técnico). Hazlo copiando el molde del agente de viajes, en src/agente_NOMBRE/ con los mismos cuatro archivos y siguiendo AGENTS.md:

1) tools.py. Una o dos herramientas con @tool de mi especialidad, con datos inventados pero creíbles dentro del archivo. Por ejemplo, para TI: estado_servicio(servicio) que dice si el wifi, la VPN, el correo o las impresoras están funcionando. Si piden algo que no está en los datos, la herramienta lo dice en una línea, nunca lanza un error.

2) prompts.py. Un SYSTEM_PROMPT que diga: eres NOMBRE, especialista en ESPECIALIDAD. Responde solo sobre eso, en español y corto, usando las herramientas antes de contestar y sin inventar datos. Si te preguntan algo que no es de tu tema, dilo en una frase y no intentes responderlo. Si te preguntan quién eres, di tu nombre y tu especialidad.

3) graph.py. Igual que el de viajes: create_agent con el modelo de Gemini, mis herramientas, el SYSTEM_PROMPT y MemorySaver, con las tres funciones responder, saltos y diagrama. Conéctalo a main.py para que funcionen python main.py NOMBRE "pregunta", --saltos y --diagrama.

4) server.py. La ficha con crear_tarjeta: nombre "Agente de NOMBRE", una descripción de dos frases (qué sé y qué no hago) y una skill por herramienta con una pregunta de ejemplo. Lee URL_NOMBRE del .env (agrégala al .env y al .env.example apuntando a http://127.0.0.1:8003) y arma app = crear_app(tarjeta, responder).

No lo levantes tú. Dime cómo probarlo sin servidor y después el comando: uvicorn src.agente_NOMBRE.server:app --port 8003 --reload.
```

Qué puedes cambiar

1. **La especialidad:** cualquier cosa que sepas de verdad. Ideas: contabilidad (IVA, boletas), cocina (recetas, reemplazos), fútbol (tabla, fixture), derecho laboral (finiquitos, vacaciones), música (acordes, escalas).
2. **Las herramientas:** con una basta. Si pones dos, que sean del mismo tema: el supervisor te elige por tema, no por cantidad.
3. **El framework:** si prefieres CrewAI, copia el molde de restaurantes (crew.py en vez de graph.py, en .venv-crew). Para A2A da igual: la ficha y el servidor son los mismos.
4. **El puerto:** 8003 para el primer integrante, 8004 para el segundo, 8005 para el tercero. Cada agente con su URL_NOMBRE en el .env.

Entregables de este paso

- La carpeta `src/agente_NOMBRE/` con sus cuatro archivos, dentro del proyecto completo.
- `main.py` con tu agente registrado y `.env.example` con tu `URL_NOMBRE`.
- En el documento: el prompt que usaste y, en dos líneas, qué cambiaste después de verlo funcionar.

**Lo logré ✓** Existe src/agente_NOMBRE/ y python main.py NOMBRE “pregunta” responde con mi herramienta.
