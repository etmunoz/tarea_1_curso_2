<!--encabezado-grupo-->
> **Archivo:** `respuestas/53-fichas-automaticas-vigilante.md`  
> **Objetivo:** Respuesta 53 · Fichas automáticas (vigilante)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 2016 · **Última modificación:** 20261111 2049
<!--/encabezado-grupo-->

# Respuesta 53 · Fichas automáticas (vigilante)

Prompt: [`../prompts_ejecutados/53-fichas-automaticas-vigilante.md`](../prompts_ejecutados/53-fichas-automaticas-vigilante.md)

## Qué se hizo

- **`tools/configurar_fichas.py --vigilar`**: queda corriendo y, cada `--intervalo` segundos
  (def. 5, o `FICHAS_INTERVALO`), comprueba la Agent Card de cada grafo; si detecta que el `name`
  volvió al genérico (porque `langgraph dev` recargó), **re-aplica la ficha solo** (PATCH). No hace
  nada si ya están bien (no genera ruido). Tolera que el servidor esté recargando/caído (reintenta
  al próximo tick) y pide el `assistant_id` fresco por si el reload lo cambió.
- **`scripts/mac_fichas_auto.sh`**: arranca el vigilante en una terminal aparte
  (`./scripts/mac_fichas_auto.sh "agente_ezequiel,agente_cocina"`).

## Revisión / prueba funcional (sin recargar langgraph)

```
1) Arranco el vigilante (--vigilar, intervalo 3s).
2) "Rompo" la ficha a mano:  PATCH name="agente_ezequiel" (genérico)  -> HTTP 200
   nombre inmediatamente tras romper:  agente_ezequiel
3) Espero ~5s (el vigilante detecta el drift y re-aplica):
   nombre ahora:  Agente de Ezequiel        ← restaurada automáticamente
```

Con esto, tras cualquier recarga (p. ej. `aplicar_encabezados.py` o un cambio en `src/`), las
fichas se restauran solas en pocos segundos — ya no hay que correr el comando a mano.

## Uso recomendado

En una terminal aparte, junto a `langgraph dev`:
```bash
./scripts/mac_fichas_auto.sh
```

## Nota sobre URLs

El vigilante NO toca el puente ni los túneles, así que las URLs de Gustavo y Tomás **no cambian**
por esto. (Si en algún cambio hay que regenerarlas, se informan.)
