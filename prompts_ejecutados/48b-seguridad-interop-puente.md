<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/48b-seguridad-interop-puente.md`  
> **Objetivo:** Prompt 48b · Refuerzos de seguridad sobre la interoperabilidad (prompt 49 + Gustavo)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1437 · **Última modificación:** 20261111 1857
<!--/encabezado-grupo-->

# Prompt 48b · Refuerzos de seguridad sobre la interoperabilidad (prompt 49 + Gustavo)

**Pedido del usuario:** «Ajustar seguridad/refuerzos considerando el prompt 49 (interop/puente)
y lo de Gustavo (dialecto clásico, su -32601, contextId). Informe equivalente al del 48a.»

**Enfoque:** el prompt 49 abrió superficie de ataque nueva (un **puente público** que expone
nuestro agente en A2A clásico, y un **cliente generalizado** que habla con servidores de
terceros como el de Gustavo). Este prompt revisa esa superficie desde seguridad.

## Hallazgos a comprobar y corregir

1. **Puente sin guardrails ni auth (alta):** `src/puente_a2a/servidor.py` expone `agente_ezequiel`
   a internet (por el túnel) y acepta `message/send` de cualquiera, SIN guardrail de entrada
   (vacías/largas/inyección), SIN redacción de salida y sin requerir token. Hay que aplicar los
   mismos guardrails del coordinador y un token opcional.
2. **Token enviado a endpoints arbitrarios (alta):** `a2a._pedir` adjunta `A2A_TOKEN` a TODA
   petición, incluidos servidores de terceros (Gustavo). Hay que seleccionar el token **por
   destino** (solo a hosts confiables), para no filtrar la credencial.
3. **El puente puede filtrar trazas internas (media):** excepciones no controladas en el
   `http.server` podrían devolver un 500 con traceback. Hay que un catch-all seguro.
4. **Respuestas de agentes clásicos como dato no confiable (media):** verificar que el coordinador
   sanea también las respuestas de agentes de terceros (dialecto clásico) con la política A2A.

**Pruebas deterministas** para cada hallazgo. Documentar límites. No tocar `main`. No fabricar
evidencia remota (nosotros→Gustavo sigue pendiente por su `-32601`).
