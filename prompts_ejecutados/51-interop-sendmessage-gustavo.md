<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/51-interop-sendmessage-gustavo.md`  
> **Objetivo:** Prompt 51 · Interop nosotros→Gustavo (dialecto SendMessage)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1738 · **Última modificación:** 20261111 2049
<!--/encabezado-grupo-->

# Prompt 51 · Interop nosotros→Gustavo (dialecto SendMessage)

**Pedido del usuario:** «Ojo que accedí a lo de Gustavo con este curl» (mostró que su servidor
usa `method: "SendMessage"`, `role: "ROLE_USER"`, parts sin `kind`, header `A2A-Version: 1.0`).
«Dale, como prompt 51 en la rama con su evidencia.»

**Contexto:** el `-32601` que nos daba el agente de Gustavo no era un bug suyo: su servidor
(SDK a2a-protocol.org) usa un **tercer dialecto** A2A con el método `SendMessage` y una forma de
mensaje distinta, y envuelve la respuesta en un repr de lista. Esto desbloquea el sentido
nosotros→Gustavo (que quedaba pendiente del prompt 48b/49).

**Tareas (rama `prompt-48-robustez`):**
1. `src/coordinador/a2a.py`: fallback a `SendMessage` cuando `message/send` da -32601 en dialecto
   clásico; desanidar la respuesta; extractor de `text` que reconozca `kind`/`type`/`text`.
2. Pruebas deterministas del fallback y el desanidado.
3. Evidencia REAL de nuestro cliente llamando al agente de Gustavo.
