<!--encabezado-grupo-->
> **Archivo:** `respuestas/32-windows-coordinador-contra-mac.md`  
> **Objetivo:** 32 · Respuesta — Windows: commit/push del BOM y coordinador contra el túnel del Mac  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2238 · **Última modificación:** 20261110 2340
<!--/encabezado-grupo-->

# 32 · Respuesta — Windows: commit/push del BOM y coordinador contra el túnel del Mac

Prompt: [`../prompts_ejecutados/32-windows-coordinador-contra-mac.md`](../prompts_ejecutados/32-windows-coordinador-contra-mac.md)

## 1. Commit y push: el push fue rechazado (y se resolvió)

```text
git commit  -> 4d5ecdb 29–30 · Windows: .ps1 en UTF-8 con BOM…
git push    -> RECHAZADO (non-fast-forward): origin/main tenía un commit nuevo
git fetch   -> 94cc4f6 Ezequiel Muñoz Krsulovic 22:27 «29 · Corrida real 2 PC (lado Mac)…»
```

El commit del Mac tocaba 167 archivos, casi todos **solo la fecha del encabezado** (corrió
`aplicar_encabezados.py`), y traía su corrida real: `evidencias/05-ronda-mac.md` y el registro
**29** (`29-corrida-real-2-pc.md`).

**Choques y cómo se resolvieron** (`git rebase origin/main`):

| Choque | Resolución |
|---|---|
| 5 `.ps1` + `tools/aplicar_encabezados.py`: ambos cambiamos la fecha del encabezado | Se conservó la versión del Windows (BOM y ajuste de la herramienta) y la fecha se dejó en 2230 |
| Fila 29 del índice en ambos lados | Se conservó el 29 del Mac y los nuestros quedaron como 30 y 31 |
| Número 29 usado por los dos | Los registros se renombraron con `git mv` (29→30, 30→31), se corrigieron las referencias internas y se agregó una **nota de numeración** en cada uno |

```text
git rebase --continue  -> Successfully rebased
git commit --amend     -> 96e6c30 30–31 · Windows: .ps1 en UTF-8 con BOM para PowerShell 5.1
git push               -> 94cc4f6..96e6c30  main -> main
aplicar_encabezados.py --check -> OK · 164 archivos
```

## 2. Coordinador del Windows contra el Mac

Conectividad previa:

```text
Windows local  /ok=200  grafos: cocina, ezequiel, tomas, viajes
túnel Windows  /ok=200  (delays-therapeutic-wait-yeast)
túnel Mac      /ok=200  (requirements-early-describes-socket)
```

Corrida (`win_coordinador.ps1 "https://requirements-early-describes-socket.trycloudflare.com/"`):

```text
Catalogo: local[agente_tomas] + remoto[<túnel-mac>#agente_ezequiel, <túnel-mac>#agente_cocina]
- agente_tomas: agente_tomas assistant (skills: agente_tomas Capabilities)
- agente_ezequiel: agente_ezequiel assistant (skills: agente_ezequiel Capabilities)
- agente_cocina: agente_cocina assistant (skills: agente_cocina Capabilities)
  > ¿Cuáles son los cinco principios del Reiki?            supervisor → sin_agente     ✗ (debía ir a Tomás)
  > ¿Qué métricas uso en un problema de regresión?          supervisor → sin_agente     ✗ (debía ir a Ezequiel)
  > ¿Cuánto cuesta una cazuela de vacuno para 6 personas?   supervisor → agente_remoto  ✓ (cocina)
  > ¿Quién descubrió América?                               supervisor → sin_agente     ✓
✓ evidencias/04-catalogo-windows.txt · ✓ evidencias/05-ronda-windows.md
```

Lo bueno: la conexión entre los dos PC por Cloudflare **funciona** (cocina, en el Mac, respondió
desde el Windows), y las tildes llegaron bien, gracias al BOM.

Lo malo: **2 de 4 ruteos fallaron**.

## 3. Diagnóstico del ruteo

El catálogo mostró **fichas genéricas** (`agente_tomas assistant`) en vez de las de `src/fichas.py`.
Sin la descripción («Maestro Reiki…», «Ingeniero de IA…»), el supervisor no sabe qué hace cada
agente; cocina acertó solo porque su nombre ya lo dice.

```text
ficha Windows agente_tomas  -> name='agente_tomas'    desc='agente_tomas assistant'   (en el prompt 26 era «Agente de Tomás»)
ficha Mac agente_ezequiel   -> name='agente_ezequiel' desc='agente_ezequiel assistant'
ficha Mac agente_cocina     -> name='agente_cocina'   desc='agente_cocina assistant'
```

**Causa:** `langgraph dev` corre **en memoria** y se recarga cuando cambian archivos del repo
(watchfiles). El rebase y el `git pull` modificaron muchos archivos, los servidores se recargaron
y **perdieron las fichas** aplicadas con PATCH. Pasó en los dos equipos.

**Arreglo en el Windows (hecho):**

```text
configurar_fichas.py --grafos agente_tomas --guardar-evidencia
  -> ✓ agente_tomas: «Agente de Tomás» — Maestro Reiki: explica los cinco principios (Gokai)…
```

**En el Mac (pendiente):** hay que volver a aplicar las fichas de `agente_ezequiel` y
`agente_cocina`, desde el Mac o vía su túnel. Después se repite la corrida del coordinador.

## Lección aprendida

Con `langgraph dev` en memoria, **cualquier cambio de archivos** (pull, rebase, edición) puede
borrar las fichas. Antes de correr un coordinador hay que verificar las fichas del catálogo, o
volver a correr `configurar_fichas.py` en cada equipo.

## Estado

`evidencias/04-catalogo-windows.txt` y `05-ronda-windows.md` contenían la corrida **con el ruteo
fallido**: sin commit, se sobrescriben al repetir la corrida. Esperando la decisión sobre las fichas del Mac.

---

## Respuesta completa del asistente (chat)

### Mensajes de avance

> Hago el commit y el push en español, como corresponde.

> El push fue rechazado: `origin/main` tiene commits nuevos, probablemente de Ezequiel desde el
> Mac. Antes de integrar nada, reviso qué trae.

> Ezequiel subió su propio commit «29 · Corrida real 2 PC (lado Mac)». Toca 167 archivos, casi
> todos solo en la fecha del encabezado. Hay un posible choque de numeración, porque él también
> usó el 29. Lo reviso.

> Esto es lo que encontré:
> - **Lo bueno:** Ezequiel ya corrió el coordinador del Mac contra nuestro túnel, y su commit trae `evidencias/05-ronda-mac.md` actualizado.
> - **Los choques:** en 7 archivos los dos cambiamos solo la línea de la fecha del encabezado; los dos agregamos una fila 29 al índice; su «29» ya está publicado, así que el número 29 lo ocupan dos registros distintos.
>
> Mi solución: integro su commit, dejo nuestros registros como **30** y **31**, y en los `.ps1` conservo nuestra versión con BOM.

> Tengo la URL del Mac: `https://requirements-early-describes-socket.trycloudflare.com`. Primero
> termino de integrar el commit de Ezequiel y después corro el coordinador contra esa URL.
> Resuelvo los conflictos: en los `.ps1` y en la herramienta conservo nuestra versión, la que
> tiene el BOM y el ajuste.

> Ahora renumero nuestros registros: el 30 pasa a 31 y el 29 a 30, y corrijo las referencias internas.

> Agrego una nota de la renumeración en los dos registros, porque las citas del chat decían 29 y 30.

> Push hecho (`96e6c30`). Ahora el coordinador: primero compruebo que tu agente siga arriba y
> que el túnel del Mac responda.

> Los tres responden. Corro el coordinador del Windows contra el túnel del Mac. Hace 4 preguntas
> con Gemini, así que puede tardar un par de minutos.

> El coordinador corrió y generó las evidencias, pero **el ruteo salió mal**: Reiki y métricas
> quedaron en "sin_agente". El catálogo muestra nombres genéricos ("agente_tomas assistant") en
> vez de las fichas, así que el supervisor no sabe qué hace cada agente. Reviso las fichas en los
> dos servidores.

> Encontré la causa. Antes, tu servidor tenía la ficha «Agente de Tomás»; ahora volvió a la
> genérica. `langgraph dev` se reinicia cuando cambian archivos del repo, y el rebase cambió
> varios. Como guarda todo en memoria, al reiniciarse se pierden las fichas. En el Mac pasa lo
> mismo con Ezequiel y cocina. Vuelvo a aplicar la ficha de Tomás en tu servidor, que es local.

> La ficha de Tomás ya está aplicada otra vez. Antes de preguntarte por las del Mac, dejo todo
> esto registrado como el prompt 32.
