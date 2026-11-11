<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/53-fichas-automaticas-vigilante.md`  
> **Objetivo:** Prompt 53 · Fichas automáticas (vigilante que las re-aplica solo)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 2016 · **Última modificación:** 20261111 2049
<!--/encabezado-grupo-->

# Prompt 53 · Fichas automáticas (vigilante que las re-aplica solo)

**Pedido del usuario:** «Programa para que lo de las fichas sea automático y no tener que estar
haciéndolo manualmente, ¿puedes? Si es así, nuevo prompt y revisión, commit, push, regenerar la
entrega commit y push e informar. Si cambias algo y se necesitan de nuevo las URL, me las das
(Gustavo y Tomás) para que prueben.»

**Problema:** `langgraph dev` recarga en caliente y **resetea** el name/description de cada agente
(las fichas se aplican por `PATCH /assistants/<id>`), obligando a correr `configurar_fichas.py` a
mano cada vez.

**Solución:** modo `--vigilar` en `tools/configurar_fichas.py` + `scripts/mac_fichas_auto.sh`.
