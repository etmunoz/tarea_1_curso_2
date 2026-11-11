<!--encabezado-grupo-->
> **Archivo:** `taller-a2a/07-sumar-a-los-companeros.md`  
> **Objetivo:** Sumar a los compañeros  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1450 · **Última modificación:** 20261111 1224
<!--/encabezado-grupo-->

<!-- clase: Taller · tu skill es un agente y habla por A2A · 61408ca1 | sección: sf8f5c9 | slide 7/10 · Parte 3 · Hablar entre agentes -->

Parte 3 · Hablar entre agentes · Paso 7 · terminal

# Sumar a los compañeros

Copia dos o tres direcciones del chat a `URLS_AGENTES`, reinicia tu coordinador y mira el catálogo: ahora tiene a viajes, restaurantes y a tus compañeros. Pregunta algo que no es de tu tema y sigue el camino con `--saltos`.

**terminal · .env, coordinador y tres preguntas**

```markdown
# en tu .env: las direcciones de tus compañeros, separadas por comas (copia 2 o 3 del chat)
URLS_AGENTES=https://verde-luna-456.trycloudflare.com,https://rojo-sol-789.trycloudflare.com

# terminal 3 · tu coordinador (reinícialo para que vuelva a leer las fichas)
uvicorn src.coordinador.server:app --port 8002
# → Supervisor con 4 agentes     (viajes, restaurantes y los dos compañeros)

# terminal 4 · pregunta algo que NO es de tu tema y mira a quién se lo manda
python main.py coordinador "¿Cómo declaro el IVA este mes?" --saltos
# → supervisor     : agente="Agente de Ana" · motivo="pregunta de contabilidad"
# → agente_remoto  : "[Agente de Ana] El IVA se declara hasta el día 12 con el formulario 29..."
# Saltos: 2

python main.py coordinador "¿Cuánto cuesta un vuelo a Lima?" --saltos
# → supervisor     : agente="Agente de viajes"

python main.py coordinador "¿Quién ganó el mundial de 1962?" --saltos
# → supervisor     : agente="ninguno"
# → sin_agente     : "No tengo un agente para eso. Puedo ayudarte con: ..."
```

- **“Supervisor con N agentes”:** si N es menor que lo que esperabas, alguna dirección no respondió. El coordinador avisa en una línea cuál; pídele al compañero que revise su túnel.

- **El motivo del supervisor** te dice por qué eligió a ese agente. Si eligió mal, casi siempre es la ficha del compañero: es su currículum, no el tuyo, el que está flojo.

- **Nombres repetidos:** si dos compañeros se llaman “Agente de José”, el supervisor no los distingue. Cada ficha con nombre propio.

Entregables de este paso

- `evidencias/04-catalogo.png`: la terminal del coordinador con “Supervisor con N agentes”, donde N incluye al menos dos agentes de otros computadores.
- `compañeros.md`: nombre, skill, URL y la ficha JSON de cada agente ajeno que sumaron (así sabemos de quién era cada uno).

**Lo logré ✓** Mi coordinador tiene en su catálogo a agentes que corren en otros computadores.
