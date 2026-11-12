<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/57-antecedentes-de-acceso-en-el-ruteo.md`  
> **Objetivo:** 57 · Panel de ruteo muestra antecedentes del acceso (local/remoto, endpoint, host, IP)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1552 · **Última modificación:** 20261112 1552
<!--/encabezado-grupo-->

# 57 · Antecedentes del acceso en el panel de ruteo

**Fecha:** 2026-11-12 · **Equipo:** VPS `coordinador.etmk.cl` + Mac (Ezequiel remoto)

Respuesta: [`../respuestas/57-antecedentes-de-acceso-en-el-ruteo.md`](../respuestas/57-antecedentes-de-acceso-en-el-ruteo.md)

## Instrucción del usuario (textual)

> "está muy bien, pero al lado derecho podrías entregar más antecedentes de lo que se está
> accediendo, ip, qué server, no sé, pero para dar más antecedentes."

Contexto: el panel "Ruteo del coordinador" ya mostraba el agente elegido y los pasos del grafo. El
usuario pide enriquecerlo con **a qué se está accediendo realmente**: tipo (local/remoto),
servidor, endpoint, host e IP.

## Qué se hizo

- El backend del coordinador web (`tools/coordinador_web.py`) devuelve ahora, por consulta, un
  objeto `destino` con los antecedentes del agente al que se accedió.
- El panel derecho pinta una tarjeta **"Antecedentes del acceso"** debajo del agente elegido.
- Para los agentes **locales** (que corren en el propio VPS) se muestra además la identidad pública
  del servidor (`COORD_SERVIDOR`, `COORD_SERVIDOR_IP`), configurada en el `EnvironmentFile`.
