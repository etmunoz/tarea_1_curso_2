<!--encabezado-grupo-->
> **Archivo:** `taller-a2a/05-la-ficha-es-tu-curriculum.md`  
> **Objetivo:** La ficha es tu currículum  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1450 · **Última modificación:** 20261111 1438
<!--/encabezado-grupo-->

<!-- clase: Taller · tu skill es un agente y habla por A2A · 61408ca1 | sección: sf8f5c9 | slide 5/10 · Parte 1 · Tu agente -->

Parte 1 · Tu agente · Paso 5 · prompt 2

# La ficha es tu currículum

Cuando un compañero pregunte, su supervisor va a leer tu ficha junto a las de los demás y elegir una. No sabe nada de tu tema: solo tiene la descripción. Una ficha vaga hace que te manden preguntas que no son tuyas, o que nunca te elijan.

**Ficha floja** “Agente de José. Ayuda con cosas de TI.”El supervisor no sabe si “TI” incluye programar, comprar un computador o arreglar la VPN. Adivina.
**Ficha clara** “Responde sobre el estado del wifi, la VPN, el correo y las impresoras de la oficina, y da pasos de soporte básico. No programa, no cotiza equipos ni gestiona cuentas.”Dice qué sí y qué no. El supervisor elige sin dudar.

**prompt 2 · copiar y pegar en OpenCode (cambia NOMBRE)**

```python
Revisa la ficha de mi agente en src/agente_NOMBRE/server.py pensando en quién la va a leer: otro agente, el supervisor, que con cada pregunta decide si me la manda a mí o a otro. Él no sabe nada de mi tema; solo lee la ficha. Mejórala así:

1) description. Dos frases. La primera dice qué sé, con temas concretos (no "ayudo con TI", sino "estado del wifi, la VPN, el correo y las impresoras de la oficina"). La segunda dice qué no hago, para que no me manden preguntas que no puedo responder.

2) skills. Una por herramienta: un name corto, una description de una línea y un ejemplo con una pregunta real, escrita como la haría una persona.

3) Al terminar, muéstrame la ficha final con el curl de /.well-known/agent-card.json y explícame en dos líneas cómo la usaría el supervisor para elegirme frente a un agente de viajes.
```

Qué puedes cambiar

1. **Las skills:** son la lista de “lo que sé hacer” dentro de la ficha. Una por herramienta, cada una con una pregunta de ejemplo real.
2. **La frase de “no hago”:** es la más importante. Evita que te lleguen preguntas que tu herramienta no puede responder. Cópiala de la fila “No hace” del blueprint.
3. **Reinicia el servidor** después de cambiar la ficha: el supervisor de tus compañeros la lee cuando arranca, no cada vez.

Entregables de este paso

- `evidencias/02-ficha.json`: tu ficha final descargada con curl desde `/.well-known/agent-card.json`.
- En el documento: la descripción antes y después del prompt 2, y por qué la cambiaste.

**Lo logré ✓** Mi ficha dice qué sé y qué no hago, y cada skill tiene una pregunta de ejemplo.
