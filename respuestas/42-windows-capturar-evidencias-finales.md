<!--encabezado-grupo-->
> **Archivo:** `respuestas/42-windows-capturar-evidencias-finales.md`  
> **Objetivo:** 42 · Respuesta — Windows: capturar las evidencias finales y dejarlas en la entrega  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2346 · **Última modificación:** 20261111 1227
<!--/encabezado-grupo-->

# 42 · Respuesta — Windows: capturar las evidencias finales y dejarlas en la entrega

Prompt: [`../prompts_ejecutados/42-windows-capturar-evidencias-finales.md`](../prompts_ejecutados/42-windows-capturar-evidencias-finales.md)

## Qué se hizo

1. **Traer lo último del Mac** (`git pull --ff-only`, avance rápido, sin conflictos):
   - `f159978` «Entrega completa: grupo NN, blueprints de compañeros, capturas y PDF (prompt 41)»
   - `5a80f5d` «Entrega actualizada: ronda bidireccional fresca Mac+Tomás y reempaquetado»

   Con eso llegaron las capturas `01-saltos.png` y `03-tunel.png`, el PDF del documento y
   `tools/exportar_pdf.py`.
2. **Ficha de Tomás:** el pull cambió `.py`, `langgraph dev` se recargó y la ficha volvió a la
   genérica. Se reaplicó guardando su evidencia (`configurar_fichas.py --guardar-evidencia`).
   Las fichas del Mac estaban correctas.
3. **Evidencias del Windows:** `win_coordinador.ps1` contra el túnel del Mac.
4. **Dejarlas donde corresponde:** se regeneró `entrega/tarea_1_curso_2/` con la misma función del
   empaquetador (`construir_carpeta_entrega()`), sin armar el zip, porque `dist/` no se versiona y lo
   arma el Mac. Resultado: `avisos: ninguno`.

## Resultado

Catálogo (`04-catalogo-windows.txt`):

```text
- Agente de Tomás           (local, Windows)
- Agente de Ezequiel        (Mac, por túnel)
- Agente de cocina chilena  (Mac, por túnel)
```

Ronda (`05-ronda-windows.md`, generada el 2026-11-11T02:45 UTC desde `ASUS-ETMK`):

| Pregunta | Ruta | Respondió |
|---|---|---|
| ¿Cuáles son los cinco principios del Reiki? | supervisor → agente_local | Agente de Tomás ✓ |
| ¿Qué métricas uso en un problema de regresión? | supervisor → agente_remoto | Agente de Ezequiel ✓ |
| ¿Cuánto cuesta una cazuela de vacuno para 6 personas? | supervisor → agente_remoto | Agente de cocina chilena ✓ |
| ¿Quién descubrió América? | supervisor → sin_agente | «…Agente de Tomás, Agente de Ezequiel, Agente de cocina chilena.» ✓ |

**4 de 4**, cada respuesta una sola vez y con los nombres de las fichas.

Dónde quedaron:

| Archivo | `evidencias/` | `entrega/tarea_1_curso_2/evidencias/` |
|---|---|---|
| `04-catalogo-windows.txt` | actualizado | actualizado (idéntico) |
| `05-ronda-windows.md` | actualizado | actualizado (idéntico) |
| `02-ficha-agente_tomas.json` | sin cambios (misma ficha) | sin cambios |

```text
aplicar_encabezados.py --check -> OK · 200 archivos con encabezado
git status -> solo las 4 evidencias del Windows (+ este registro)
```

## Para Ezequiel (Mac)

- Haz `git pull`: vienen las evidencias finales del Windows, ya copiadas en la carpeta de entrega.
- Si vas a armar el zip de nuevo, `tools/empaquetar_entrega.py --grupo N` ya toma estas versiones.
- Después del pull, tu `langgraph dev` se recarga: reaplica las fichas si vas a seguir probando.

## Estado

Evidencias del Windows finales y en su lugar. Commit y push a continuación.

---

## Respuesta completa del asistente (chat)

### Mensajes de avance

> El remoto tiene 2 commits nuevos del Mac. Los reviso e integro primero, y después veo cómo arma
> el empaquetador la carpeta `entrega/`.

> Es un avance rápido, sin conflictos. Como trae 53 `.py`, tu servidor se va a recargar y hay que
> reaplicar la ficha de Tomás antes de correr el coordinador.

> El Mac ya subió las capturas `01-saltos.png` y `03-tunel.png`, y el zip no se versiona. Como
> esperaba, la ficha de Tomás se perdió con el pull. La reaplico guardando su evidencia, reviso las
> del Mac y corro el coordinador.

> Las evidencias del Windows quedaron generadas: 4 de 4, con los nombres reales. Ahora las paso a la
> carpeta de la entrega. Antes reviso cómo la arma el empaquetador, para regenerarla igual que el Mac.

> Solo regenero la carpeta `entrega/tarea_1_curso_2/`, con la misma función del empaquetador. El
> zip (`dist/`) no se versiona y lo arma el Mac. Después reviso que solo hayan cambiado las
> evidencias del Windows.

> Solo cambiaron las 4 evidencias del Windows: las dos de `evidencias/` y sus copias en la entrega.
> La ficha de Tomás quedó idéntica. Antes de documentar, confirmo que el Mac no haya usado el 42.

### Respuesta final

> Listo: las evidencias finales del Windows están generadas, copiadas en la carpeta de entrega y
> subidas al repo. Ezequiel solo tiene que hacer `git pull`.
>
> La ronda salió 4 de 4 con los nombres reales: Reiki → Tomás (local), métricas → Ezequiel (Mac),
> cazuela → cocina (Mac), y la pregunta fuera de tema sin agente.
>
> Este prompt quedó documentado como el 42.
