<!--encabezado-grupo-->
> **Archivo:** `respuestas/37-mac-verificar-arreglos-y-ronda.md`  
> **Objetivo:** 37 · Respuesta — Mac: verificar arreglos de Tomás y regenerar la ronda  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2259 · **Última modificación:** 20261111 1227
<!--/encabezado-grupo-->

# 37 · Respuesta — Mac: verificar arreglos de Tomás y regenerar la ronda

Prompt: [`../prompts_ejecutados/37-mac-verificar-arreglos-y-ronda.md`](../prompts_ejecutados/37-mac-verificar-arreglos-y-ronda.md)

## Qué se hizo (lado Mac)

- `git pull` → traje los arreglos de Tomás (prompts 34/35): cliente A2A sin duplicados,
  etiqueta `agente_local`/`agente_remoto`, caché de fichas con TTL, rutas `as_posix()`.
- La recarga de `langgraph dev` borró las fichas → reaplicadas con `configurar_fichas.py`.
- Verifiqué los arreglos en el Mac y regeneré la ronda real contra el túnel de Windows.

## Verificación

```text
$ uv run pytest -q
40 passed, 1 skipped

$ ./scripts/mac_coordinador.sh "<túnel-windows>"   (evidencias/05-ronda-mac.md)
> ¿Qué técnica uso si tengo desbalance de clases?   supervisor → agente_local   [Agente de Ezequiel]        (local, Mac)
> ¿Qué símbolos se aprenden en el nivel 2 de Reiki? supervisor → agente_remoto  [Agente de Tomás]           (REMOTO, Windows)
> ¿Cuánto cuesta un pastel de choclo para 4?        supervisor → agente_local   [Agente de cocina chilena]  (local, Mac)
> ¿Quién ganó el mundial de 1962?                   supervisor → sin_agente
```

Con los arreglos: **sin respuestas duplicadas**, etiquetas de ruta correctas (`agente_local`
para Ezequiel/cocina del Mac, `agente_remoto` para Tomás del Windows) y nombres consistentes.

## Estado

Los arreglos de Tomás funcionan igual en el Mac. Evidencia `05-ronda-mac.md` regenerada,
cross-machine real (Reiki respondido por Tomás en el Windows). Fichas reaplicadas; Mac arriba.
