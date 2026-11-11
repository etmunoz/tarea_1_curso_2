<!--encabezado-grupo-->
> **Archivo:** `respuestas/45-forzar-estado-controlado-end-to-end.md`  
> **Objetivo:** Respuesta 45 · Forzar el estado controlado end-to-end (remoto caído)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 0735 · **Última modificación:** 20261111 2049
<!--/encabezado-grupo-->

# Respuesta 45 · Forzar el estado controlado end-to-end (remoto caído)

Prompt: [`../prompts_ejecutados/45-forzar-estado-controlado-end-to-end.md`](../prompts_ejecutados/45-forzar-estado-controlado-end-to-end.md)

## Problema que resuelve

En el prompt 44, con el Windows caído, el supervisor **evitaba** al agente marcado
`(no disponible ahora)` y enrutaba a `sin_agente`; el estado controlado solo se veía en la
llamada A2A directa. Faltaba capturar el camino **completo por el coordinador** terminando
en `agente_no_disponible`.

## Cómo se forzó (realista)

La caché de fichas (`catalogo._cards`, TTL `A2A_CARD_TTL`) hace que un agente que estaba
arriba siga figurando como disponible unos segundos aunque se caiga. Se siembra la ficha de
Tomás en esa caché: el supervisor la ve disponible y lo **elige**, y el fallo ocurre recién
al **consultar** el túnel caído → `consultar` devuelve el estado controlado. Esto reproduce
la carrera real "estaba arriba, se cayó entre el enrutado y la consulta".

Se agregó `_seccion_forzado(...)` a `tools/evidencia_robustez.py`:

```python
catalogo._cards[(remoto, "agente_tomas")] = (time.monotonic(), FICHAS["agente_tomas"])
```

## Salida real (end-to-end por el coordinador, Windows caído)

```
## 3. End-to-end forzado: el supervisor elige al remoto y se cae al consultar

- Ficha de Tomás sembrada en caché (CARD_TTL) para que el supervisor la vea
  disponible; el túnel https://delays-therapeutic-wait-yeast.trycloudflare.com sigue caído.

- > ¿Qué símbolos se aprenden en el nivel 2 de Reiki?
  - ruta: guardia_entrada → supervisor → agente_no_disponible
  - El Agente de Tomás no está disponible temporalmente (no se pudo conectar
    (¿túnel caído?)). Puedes intentar nuevamente más tarde. Los demás agentes
    continúan operativos.
```

La ruta `supervisor → agente_no_disponible` confirma que `consultar` captó el fallo y
entregó el mensaje controlado exacto, end-to-end.

## Reproducir

```bash
uv run python tools/evidencia_robustez.py --remoto https://<tunel-caido> --etiqueta mac
```

## Commit

`45ed53a` — «45 · Forzar end-to-end el estado controlado del agente remoto caído». La
sección quedó incorporada en `evidencias/06-robustez-mac.md` (§3).
