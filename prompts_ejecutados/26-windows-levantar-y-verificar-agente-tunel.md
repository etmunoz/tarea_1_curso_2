<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/26-windows-levantar-y-verificar-agente-tunel.md`  
> **Objetivo:** 26 · Windows: el usuario levanta agente y túnel; Claude verifica  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2215 · **Última modificación:** 20261110 2312
<!--/encabezado-grupo-->

# 26 · Windows: el usuario levanta agente y túnel; Claude verifica

**Fecha:** 2026-11-10 · **Equipo:** Windows (nodo Tomás)

## Prompts

> Lo hago yo

*(respuesta a "¿Levanto el agente Tomás y el túnel en dos pestañas?")*

> tu lo verificas

> Salió esto: *(pegó la salida de `.\scripts\win_servir.ps1`: langgraph dev arriba en :2024)*

> acuérdate que debes dejar todo escrito lo que va sucediendo, siempre en español.

## Verificación pedida

- El usuario corre `win_servir.ps1` y `win_tunel.ps1`; Claude verifica que el agente responda
  en `:2024`, que se regenere la ficha `evidencias/02-ficha-agente_tomas.json` y que el túnel
  entregue una URL `https://….trycloudflare.com` que responda.
