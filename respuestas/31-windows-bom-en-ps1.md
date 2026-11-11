<!--encabezado-grupo-->
> **Archivo:** `respuestas/31-windows-bom-en-ps1.md`  
> **Objetivo:** 31 · Respuesta — Windows: arreglar la codificación de los `.ps1` (UTF-8 con BOM)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2226 · **Última modificación:** 20261111 1738
<!--/encabezado-grupo-->

# 31 · Respuesta — Windows: arreglar la codificación de los `.ps1` (UTF-8 con BOM)

> **Nota de numeración:** este registro se escribió como el 30 y se renumeró a 31 por el 29 que Ezequiel publicó desde el Mac; las citas del chat que decían «29 y 30» o «30» se ajustaron a «30 y 31» o «31».

Prompt: [`../prompts_ejecutados/31-windows-bom-en-ps1.md`](../prompts_ejecutados/31-windows-bom-en-ps1.md)

## El problema (detectado en el prompt 21)

Los `scripts/*.ps1` estaban en UTF-8 **sin BOM**. Windows PowerShell 5.1 interpreta esos
archivos como ANSI (cp1252), así que `¿Cuáles son…?` se leía como `Â¿CuÃ¡les son…?`. Además
de verse mal en consola, `win_coordinador.ps1` habría mandado las preguntas **mal escritas**
a los agentes y a las evidencias `05-ronda-windows.md`.

## Qué se hizo

1. **`tools/aplicar_encabezados.py`**: antes leía todo como UTF-8 sin considerar el BOM. Con
   BOM, su `--check` fallaba (el `# --8<--` ya no era lo primero) y al aplicar encabezados
   **habría quitado el BOM** otra vez. Se ajustó `procesar()`:
   ```python
   bom = "﻿" if (texto.startswith("﻿") or ext == ".ps1") else ""
   texto = texto.removeprefix("﻿")
   ...
   shebang = bom + shebang   # se repone al escribir (siempre en .ps1)
   ```
2. **Los 5 `.ps1`** (`setup_windows`, `win_app`, `win_coordinador`, `win_servir`, `win_tunel`)
   se reescribieron como **UTF-8 con BOM**, sin cambiar su contenido; solo se actualizó la
   fecha de *Última modificación* del encabezado.

## Verificación

```text
PowerShell 5.1.26100 lee (win_coordinador.ps1): ¿Cuáles son los cinco principios del Reiki?  -> correcto: True
Los 5 .ps1 parsean con el parser de PowerShell                                          -> errores=0 en todos
aplicar_encabezados.py sobre una copia .ps1 con BOM  -> BOM conservado: True | duplicado: False
aplicar_encabezados.py --check                        -> OK · 160 archivos con encabezado
git diff --stat scripts/                              -> 5 archivos, solo BOM + fecha del encabezado
```

## Lo malo / lo que no resultó a la primera

- Al editar la herramienta, el `"﻿"` quedó guardado como el **carácter BOM literal**
  (invisible) en vez del texto `﻿`. Funcionaba, pero era invisible y frágil.
- El primer intento de reemplazarlo con un `python -c` en línea **no hizo nada** (el
  escapado entre Bash y Python se cruzó). Se resolvió con un script aparte que usa
  `chr(0xFEFF)` y `chr(92)`, y ahora el código muestra `"﻿"` visible. Se volvió a probar
  la herramienta después del cambio.

## Lo que queda pendiente (no se tocó)

- `win_servir.ps1`: el job que guarda la ficha sigue sin `PYTHONIOENCODING=utf-8` (ver prompt 26).
  El BOM arregla cómo PowerShell **lee** el script; no cómo Python **imprime** en un job sin consola.
- Git avisa `LF will be replaced by CRLF`: normal en Windows.

## Estado

Los `.ps1` quedan listos para PowerShell 5.1, en particular `win_coordinador.ps1` para generar
las evidencias. Cambios **sin commit**. Siguiente: la URL del túnel del Mac.

---

## Respuesta completa del asistente (chat)

### Mensajes de avance (traducidos; en el chat salieron en inglés)

> La herramienta de encabezados lee los archivos como UTF-8 simple, así que un BOM rompería
> su revisión, y al aplicar encabezados también quitaría el BOM de nuevo. La ajusto para que
> conserve el BOM y después convierto los `.ps1`.

> Ahora verifico con el propio PowerShell 5.1 que lea bien las preguntas con tildes del coordinador.

> PowerShell 5.1 ahora lee bien `¿Cuáles son…?`. Pruebo además que la herramienta de
> encabezados conserve el BOM al reescribir un `.ps1`.

> El diff muestra un carácter invisible donde escribí `"﻿"`. Reviso si el archivo tiene
> la secuencia de escape o el carácter literal.

> Es el carácter literal: funciona, pero es invisible y frágil. Lo reemplazo por el escape visible `﻿`.

> El reemplazo automático no se aplicó. Lo hago con el editor.

> Listo, y la herramienta sigue funcionando. Ahora registro todo como el prompt 31.

### Respuesta final

> Arreglé la codificación: los 5 `.ps1` están ahora en UTF-8 con BOM, y PowerShell 5.1 lee
> bien las tildes. Lo comprobé con el propio parser de PowerShell: lee
> `¿Cuáles son los cinco principios del Reiki?` tal cual, y los 5 scripts parsean sin errores.
>
> También ajusté `tools/aplicar_encabezados.py`, porque sin ese cambio su revisión fallaba con
> el BOM y, al aplicar encabezados, lo habría quitado otra vez. Lo probé sobre una copia: el
> BOM se conserva, no se duplica, y la revisión pasa en los 160 archivos.
>
> En el camino hubo un tropiezo: el BOM quedó como un carácter invisible dentro del código de
> la herramienta y el primer intento de corregirlo no se aplicó. Lo arreglé con un script
> aparte y ahora se ve `"﻿"` en el código.
>
> Queda pendiente el otro problema de codificación, el del job de `win_servir.ps1` que no
> guarda la ficha; ese es de cómo imprime Python, no de cómo PowerShell lee el script.
>
> Todo quedó registrado como el prompt 31, sin commit todavía.
