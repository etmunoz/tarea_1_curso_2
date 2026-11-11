<!--encabezado-grupo-->
> **Archivo:** `respuestas/35-windows-arreglar-detalles-coordinador.md`  
> **Objetivo:** 35 · Respuesta — Windows: arreglar los detalles del coordinador y de las herramientas  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2253 · **Última modificación:** 20261110 2325
<!--/encabezado-grupo-->

# 35 · Respuesta — Windows: arreglar los detalles del coordinador y de las herramientas

Prompt: [`../prompts_ejecutados/35-windows-arreglar-detalles-coordinador.md`](../prompts_ejecutados/35-windows-arreglar-detalles-coordinador.md)

## 1. Respuestas duplicadas → `src/coordinador/a2a.py`

**Causa (verificada con una respuesta real de Tomás):**

```text
.history[0].parts[0].text   = 'Di solo: hola'                     ← la PREGUNTA del usuario
.history[1].parts[0].text   = 'Hola, soy Tomás, Maestro Reiki.'   ← la respuesta
.artifacts[0].parts[0].text = 'Hola, soy Tomás, Maestro Reiki.'   ← la MISMA respuesta
```

`_texto_de_resultado` recorría todo el resultado y unía todos los textos. Por eso salían la
pregunta repetida y la respuesta dos veces.

**Arreglo:** se toma la respuesta en orden de preferencia: 1) `artifacts`; 2) el mensaje de
`status`; 3) el último mensaje con `role: agent` del `history`; 4) como último recurso, todos los
textos. Tests nuevos: `test_texto_de_resultado_no_duplica_ni_repite_la_pregunta` y
`test_texto_de_resultado_sin_artifacts_usa_ultimo_mensaje_del_agente`.

## 2. `agente_remoto` para Tomás → `catalogo.py` + `graph.py`

- `AgenteRemoto` tiene ahora el campo `local: bool`. `construir_catalogo()` pone `local=True`
  en los grafos de `A2A_GRAFOS_LOCALES` y `local=False` en los de `URLS_AGENTES`.
- El nodo `consultar` registra `agente_local` o `agente_remoto` según ese campo.
- Test nuevo: `test_catalogo_marca_locales_y_remotos`.

## 3. Nombres mezclados en "sin agente" → `catalogo.py`

**Causa:** el grafo vuelve a armar el catálogo en cada nodo (`enrutar`, `_rama`, `consultar`,
`sin_agente`), y cada vez pedía las fichas otra vez por el túnel. Si en alguna de esas
peticiones fallaba una ficha remota, el nombre caía al id del grafo (`agente_ezequiel`). Esto
también podía mandar una pregunta a `sin_agente` por error, porque `_rama` compara nombres.

**Arreglo:** caché de fichas **compartida en el proceso**, por (base, grafo), con un TTL de 120 s
(se configura con `A2A_CARD_TTL`). Solo se guardan las fichas que respondieron bien. Se quitó
la caché por objeto (`_card`), que se perdía en cada armado del catálogo. Test nuevo:
`test_ficha_se_pide_una_vez_y_nombre_consistente`, que con 3 armados pide la ficha 1 vez y
mantiene el nombre aunque el túnel falle después.

## 4. Rutas con `\` en Windows → `tools/aplicar_encabezados.py`

- `str(path.relative_to(RAIZ))` → `path.relative_to(RAIZ).as_posix()` en los 3 lugares.
  Probado sobre una copia: `> **Archivo:** \`evidencias/_prueba_ruta.md\``.
- **Extra:** se excluye `.pytest_cache` (pytest crea ahí un `README.md` sin encabezado y `--check`
  lo marcaba).

## 5. Extra: evidencias sin encabezado → `tools/guardar_evidencias.py`

Ahora `guardar_evidencias.py` llama a `aplicar_encabezados.procesar()` después de escribir
`04-catalogo-*.txt` y `05-ronda-*.md`. Ya no hace falta arreglarlas a mano, como en el prompt 33.

## Verificación

```text
uv run pytest -q                   -> 40 passed, 1 skipped
aplicar_encabezados.py --check     -> OK · 170 archivos con encabezado
configurar_fichas.py (Tomás)       -> reaplicada: langgraph dev se recargó por los cambios de código
fichas del Mac                     -> «Agente de Ezequiel», «Agente de cocina chilena» (intactas)
```

Nueva corrida (`win_coordinador.ps1` → túnel del Mac):

```text
¿Cuáles son los cinco principios del Reiki?   supervisor → agente_local   [Agente de Tomás] Los cinco principios… (UNA vez)
¿Qué métricas uso en un problema de regresión? supervisor → agente_remoto  [Agente de Ezequiel] …
¿Cuánto cuesta una cazuela de vacuno…?         supervisor → agente_remoto  [Agente de cocina chilena] …
¿Quién descubrió América?                      supervisor → sin_agente
   "No tengo un agente para eso. Puedo ayudarte con: Agente de Tomás, Agente de Ezequiel, Agente de cocina chilena."
05-ronda-windows.md  -> con encabezado del grupo y ruta `evidencias/05-ronda-windows.md`
```

## Lo que NO se hizo (y por qué)

- **Capturas `01-saltos.png` y `03-tunel.png`:** son manuales, una captura de pantalla de tu
  equipo. Quedan para el usuario.
- **"Registros 32 y 33 sin commit":** ya estaba resuelto; entraron en el commit `3b12365` (prompt 34).

## Para el Mac (Ezequiel)

Después de `git pull`, su `langgraph dev` se va a recargar y **perderá las fichas**. Tiene que
volver a correr:

```bash
uv run python tools/configurar_fichas.py --grafos agente_ezequiel,agente_cocina
```

Si vuelve a correr `mac_coordinador.sh`, su ronda va a salir con las mismas mejoras: sin
duplicados, con `agente_local`/`agente_remoto` y con encabezado.

---

## Respuesta completa del asistente (chat)

### Mensajes de avance

> Confirmé la causa de la duplicación. El resultado A2A trae el `history` (con la pregunta y la
> respuesta) y además los `artifacts` (otra vez la respuesta). El cliente recorre todo y junta
> los textos, así que la pregunta aparece repetida al inicio y la respuesta sale dos veces.
> Reviso los tests antes de corregirlo.

> Corrijo el cliente A2A para que tome la respuesta de los `artifacts`. Si no hay `artifacts`,
> usa el mensaje del `status`, y si tampoco hay, el último mensaje del agente en el `history`.
> Así nunca se repite la pregunta.

> Entendido: cuando termine, hago commit y push para que el Mac tenga los cambios. Sigo con la
> etiqueta de la ruta: marco en el catálogo qué agentes son locales, para que la ruta diga
> `agente_local` o `agente_remoto` según corresponda.

> Reviso que nadie más use el campo `_card` que eliminé, ni la etiqueta `agente_remoto`.

> Con la caché, el mensaje de "sin agente" usa los mismos nombres que el catálogo, sin pedir otra
> vez las fichas por el túnel. Agrego tests para la marca de local y para la caché, y corrijo las
> rutas con `/` en la herramienta de encabezados.

> Las líneas 213 y 258 son las que escriben la ruta en el encabezado. La 299 solo la muestra en
> pantalla, pero la cambio también por consistencia.

> También hago que `guardar_evidencias.py` ponga el encabezado del grupo al escribir las
> evidencias, para que no vuelva a pasar lo del prompt 33.

> Pasan los 40 tests, y 1 se salta porque es opcional. Como cambié archivos del repo, tu
> `langgraph dev` se recargó y perdió la ficha de Tomás. La reaplico, reviso las del Mac y repito
> la corrida.

> Los 3 detalles quedaron arreglados en la corrida real. Reviso la evidencia completa y su encabezado.

> La revisión de encabezados marca `.pytest_cache/README.md`. Ese archivo lo creó pytest al correr
> los tests y git lo ignora, pero la herramienta no excluye esa carpeta. La agrego a las carpetas
> excluidas.

> Actualizo la fecha de los encabezados solo en los archivos que cambié y escribo el registro 35.

*(La respuesta final está al final de este turno en el chat y queda resumida arriba: los cuatro
arreglos, la corrida nueva, lo que no se hizo y el aviso para el Mac.)*
