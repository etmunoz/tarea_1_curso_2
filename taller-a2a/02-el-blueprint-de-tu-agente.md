<!--encabezado-grupo-->
> **Archivo:** `taller-a2a/02-el-blueprint-de-tu-agente.md`  
> **Objetivo:** El blueprint de tu agente  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1450 · **Última modificación:** 20261110 2009
<!--/encabezado-grupo-->

<!-- clase: Taller · tu skill es un agente y habla por A2A · 61408ca1 | sección: sf8f5c9 | slide 2/10 · Parte 1 · Tu agente -->

Parte 1 · Tu agente · Paso 2 · blueprint

# El blueprint de tu agente

Antes de pedirle nada a OpenCode, cada integrante escribe en una tabla qué hace su agente, qué no hace y con qué herramienta. Es la misma tabla del Curso 1. Va en un archivo propio, `blueprint-NOMBRE.md`, y de ahí salen los prompts de los pasos siguientes.

**blueprint-NOMBRE.md · plantilla (completa cada fila con una frase)**

```markdown
## Blueprint · Agente de NOMBRE

| Qué definir        | Mi agente                                                                 |
|--------------------|---------------------------------------------------------------------------|
| Quién soy          | NOMBRE · ESPECIALIDAD (una frase)                                         |
| Hace               | …                                                                         |
| No hace            | …                                                                         |
| Herramientas       | nombre_de_la_herramienta(parámetros): qué devuelve y de dónde salen los datos |
| Decide solo        | …                                                                         |
| Nunca sin persona  | …                                                                         |
| Deriva a otro      | Cuando la pregunta es de … → lo dice en una frase y no responde           |
| Dónde se ejecuta   | http://127.0.0.1:8003 · src/agente_NOMBRE/ · python main.py NOMBRE        |
| Dirección pública  | (se completa en el paso 6 con la URL del túnel)                           |
```

Qué puedes cambiar

1. **Hace / No hace:** una frase cada una, concreta. “Responde sobre el estado del wifi, la VPN, el correo y las impresoras”, no “ayuda con TI”.
2. **La herramienta:** una basta. Escribe de dónde salen los datos (un diccionario inventado hoy; una API real si quieres seguir después).
3. **Deriva a otro:** esta fila es la que después hace que el supervisor no te mande preguntas que no son tuyas.

Entregables de este paso

- `blueprint-NOMBRE.md` completo, uno por integrante, en la raíz del zip.
- En el documento de entrega: los nombres y apellidos de los integrantes, el grupo y el blueprint de cada uno.

**Lo logré ✓** Puedo decir en una frase qué hace mi agente, qué no hace y qué herramienta usa.
