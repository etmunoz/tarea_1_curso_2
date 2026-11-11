<!--encabezado-grupo-->
> **Archivo:** `respuestas/45-forzar-estado-controlado-end-to-end.md`  
> **Objetivo:** Respuesta 45 · Forzar el estado controlado end-to-end (remoto caído)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 0735 · **Última modificación:** 20261111 0743
<!--/encabezado-grupo-->

# Respuesta 45 · Forzar el estado controlado end-to-end (remoto caído)

## Qué se hizo

Se agregó `_seccion_forzado(...)` a `tools/evidencia_robustez.py`. Siembra la ficha del
remoto (`agente_tomas`) en la caché de fichas (`catalogo._cards`, TTL `A2A_CARD_TTL`),
de modo que el supervisor la vea **disponible** y la ELIJA; el túnel sigue caído, así
que el fallo ocurre recién en `consultar`, que devuelve el **estado controlado**.

Esto reproduce un caso real: el agente estaba arriba (su ficha quedó cacheada hasta
`CARD_TTL` segundos) y se cae entre el enrutado y la consulta.

## Evidencia (end-to-end, por el coordinador, Windows caído)

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

La evidencia completa (resiliencia + este camino forzado + guardrails) quedó en
`evidencias/06-robustez-mac.md`.

## Reproducir
```bash
uv run python tools/evidencia_robustez.py --remoto https://<tunel-caido> --etiqueta mac
```
