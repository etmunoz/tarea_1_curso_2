<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/56-coordinador-web-correo-y-cross-machine.md`  
> **Objetivo:** 56 · Coordinador web en la VPS — fix de import, ruteo cross-machine al Mac y envío de correo  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1521 · **Última modificación:** 20261112 1521
<!--/encabezado-grupo-->

# 56 · Coordinador web en la VPS — fix de import, ruteo cross-machine y correo

**Fecha:** 2026-11-12 · **Equipo:** Mac (nodo Ezequiel) + VPS `coordinador.etmk.cl`

Respuesta: [`../respuestas/56-coordinador-web-correo-y-cross-machine.md`](../respuestas/56-coordinador-web-correo-y-cross-machine.md)

## Instrucciones del usuario (textual, en orden)

1. (Pantalla) El coordinador web respondía `error del coordinador: No module named 'src'` y ruteaba a
   «ninguno». → arreglar.
2. «todo esto que estamos haciendo debe ser un nuevo prompt que permita registrar en la salida lo que
   vamos haciendo y obteniendo» → registrar esta tanda como prompt 56.
3. «ya lo guardé en la app coordinador de la vps» → el usuario puso la URL del **Ezequiel del Mac**
   (túnel Cloudflare) en la config ⚙️ del coordinador de la VPS.
4. «voy a crear este correo para que el agente coordinador de la vps también pueda enviar correos, te
   parece» + «o le ponemos otro nombre, como coordinador@etmk.cl, ese mejor no?» → crear buzón
   `coordinador@etmk.cl` y dar al coordinador la capacidad de **enviar correos**.
5. «es para ti … cómo te la paso» → la clave SMTP se inserta **solo** en el `EnvironmentFile` del
   servicio en el VPS; el asistente nunca la ve.
6. «destinatario mientras solo yo, etmunoz@gmail.com luego agregamos los de mis compañeros» →
   allowlist que hoy tiene solo su Gmail.
7. «listo, clave insertada» → desplegar y probar el envío real.

## Qué se hizo

- **Fix** `No module named 'src'`: el servicio corre fuera del raíz del repo → se agrega `RAIZ` a
  `sys.path` en `tools/coordinador_web.py`.
- **Prueba cross-machine**: el coordinador de la **VPS** rutea una pregunta de IA al **Ezequiel del
  Mac** (remoto, por túnel), vía `URLS_AGENTES=…#agente_ezequiel`.
- **Envío de correo**: endpoint `POST /api/enviar-correo` + `GET /api/correo`, botón «✉️ Enviar por
  correo» en cada respuesta, SMTP submission 587 + STARTTLS desde `coordinador@etmk.cl`.
  Guardrail: destinatario en allowlist y disparo **solo** por el usuario en la UI (nunca auto-envío
  desde respuestas de agentes, que son contenido no confiable). Credenciales solo en el
  `EnvironmentFile`, nunca en el repo.
