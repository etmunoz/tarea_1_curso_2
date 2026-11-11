<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/50-backoffice-monitor-accesos-puente.md`  
> **Objetivo:** Prompt 50 · Backoffice de accesos al puente A2A (log + app Tkinter)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1723 · **Última modificación:** 20261111 1857
<!--/encabezado-grupo-->

# Prompt 50 · Backoffice de accesos al puente A2A (log + app Tkinter)

**Pedido del usuario (textual, consolidado):**

> Para el código de main, ¿cómo puedo registrar o saber que se está accediendo, para tener un
> registro? … Como tener una app que mire como el backoffice, y vaya registrando quién accede y
> qué accede, sería interesante. … Puede ser una app Tkinter que muestre en una ventana lo que
> sucede. Déjalo como prompt 50. Detállalo bien, y toma evidencias.

**Contexto:** el puente A2A (`src/puente_a2a/servidor.py`) silenciaba el log por request, así que
no quedaba registro de quién consume nuestro `agente_ezequiel` por el túnel (p. ej. Gustavo).

**Tareas:**
1. **Log de accesos opcional** en el puente: si `PUENTE_LOG` apunta a un archivo, escribir una
   línea por request (fecha UTC, IP real del cliente —reenviada por Cloudflare—, método, ruta,
   código). Sin contenido del mensaje ni secretos.
2. **App de escritorio (Tkinter, stdlib)** `tools/monitor_puente.py` que SOLO lee ese log y
   muestra en vivo una tabla (hora, IP, qué hizo, ruta, código) + resumen (total, IPs, consultas
   vs fichas, último acceso). Read-only: no toca el puente ni el túnel (seguro con Gustavo probando).
3. Evidencia de la app funcionando con accesos reales.

**Restricción:** NO reiniciar/regenerar el puente ni el túnel mientras Gustavo prueba.
