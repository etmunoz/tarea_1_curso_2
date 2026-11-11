<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/41-empaquetar-entrega-carpeta-y-leeme.md`  
> **Objetivo:** Prompt 41 · Empaquetar la entrega como carpeta en la repo + LEEME  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2322 · **Última modificación:** 20261111 1413
<!--/encabezado-grupo-->

# Prompt 41 · Empaquetar la entrega como carpeta en la repo + LEEME

**Pedido del usuario (textual):**

> si, y deja el zip como estructura dentro de la repo con todo lo que se pide en
> una carpeta que tenga el nombre de la repo, y además un LEEME.txt para que diga
> lo que hay que hacer al deszipear.

**Contexto previo (el "si"):** aceptó completar `entrega/documento-entrega.md` con
los nombres del grupo (que están en los encabezados) y arreglar el empaquetador.

**Tareas:**
1. Completar `entrega/documento-entrega.md` (integrantes: Fabio Durán, Gustavo
   Reyes, Ezequiel Muñoz; ronda real; nombres de evidencias reales).
2. Crear `entrega/LEEME.txt` con qué hacer al deszipear.
3. `tools/empaquetar_entrega.py`: raíz del zip = `tarea_1_curso_2/` (nombre de la
   repo), incluir `LEEME.txt`, arreglar el checklist de evidencias, y materializar
   la estructura como carpeta versionada `entrega/tarea_1_curso_2/`.
4. Aplicar encabezados, regenerar el zip, registrar prompt/respuesta, commit+push.
