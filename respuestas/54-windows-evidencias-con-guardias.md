<!--encabezado-grupo-->
> **Archivo:** `respuestas/54-windows-evidencias-con-guardias.md`  
> **Objetivo:** 54 · Respuesta — Windows: actualizar las evidencias contra el Mac con el código final (guardias)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 2027 · **Última modificación:** 20261111 2027
<!--/encabezado-grupo-->

# 54 · Respuesta — Windows: actualizar las evidencias contra el Mac con el código final (guardias)

Prompt: [`../prompts_ejecutados/54-windows-evidencias-con-guardias.md`](../prompts_ejecutados/54-windows-evidencias-con-guardias.md)

## Qué se hizo

1. **Integrar lo último del Mac** (`git pull --ff-only`, avance rápido, en dos tandas):
   - `f19a57d` 52 · Confirmar interop contra el repo de Gustavo + caché de método
   - `12bf9c5` Evidencia 14: ronda end-to-end Mac↔Windows↔Gustavo
   - `8d4eafc` 53 · Fichas automáticas: modo `--vigilar` + `scripts/mac_fichas_auto.sh`
   - `438bdde` Entrega regenerada: fichas automáticas (53) + evidencia ronda (14)
2. **Fichas:** cada pull cambió `.py` y recargó `langgraph dev`, así que la ficha de Tomás se
   perdía. El primer intento de generar se **pausó**, porque el Mac también había perdido las
   suyas. Ezequiel las reaplicó.
3. **Vigilante de fichas en Windows:** no hay un `win_fichas_auto.ps1`, pero el modo `--vigilar`
   del prompt 53 funciona igual. Se dejó corriendo en una pestaña:
   `uv run python tools/configurar_fichas.py --grafos agente_tomas --vigilar`. Detectó la recarga y
   reaplicó «Agente de Tomás» solo.
   - Detalle: la herramienta de terminal reportó que el comando "no se ejecutó", pero sí se
     ejecutó. Se comprobó leyendo la pestaña.
4. **Evidencias:** `win_coordinador.ps1 "https://coffee-products-pharmaceutical-guitar.trycloudflare.com/"`.
5. **Entrega:** `construir_carpeta_entrega()` → `avisos: ninguno`. Las copias quedaron idénticas a
   las de `evidencias/`.

## Resultado

| Pregunta | Ruta | Respondió |
|---|---|---|
| ¿Cuáles son los cinco principios del Reiki? | guardia_entrada → supervisor → **agente_local** → guardia_salida | Agente de Tomás ✓ |
| ¿Qué métricas uso en un problema de regresión? | guardia_entrada → supervisor → **agente_remoto** → guardia_salida | Agente de Ezequiel (Mac) ✓ |
| ¿Cuánto cuesta una cazuela de vacuno para 6 personas? | guardia_entrada → supervisor → **agente_remoto** → guardia_salida | Agente de cocina chilena (Mac) ✓ |
| ¿Quién descubrió América? | guardia_entrada → supervisor → **sin_agente** → guardia_salida | ✓ |

**4 de 4.** Las guardias de entrada y salida (prompts 44–47 del Mac) no bloquearon respuestas
legítimas.

```text
aplicar_encabezados.py --check -> OK · 258 archivos con encabezado
cambios: evidencias/04-catalogo-windows.txt, 05-ronda-windows.md y sus copias en la entrega
```

## ¿Se hizo algo especial para Gustavo del lado Windows?

**No.** Se revisaron los registros 48b, 49, 51 y 52. Todo lo de Gustavo está en el **Mac**:

| Sentido | Qué hay | Dónde |
|---|---|---|
| Gustavo → nosotros | Puente A2A clásico (`src/puente_a2a/servidor.py`, `scripts/mac_puente.sh`) | Mac; expone **solo `agente_ezequiel`** (`PUENTE_GRAFO`) |
| Nosotros → Gustavo | Cliente con el dialecto `SendMessage` del SDK oficial + caché de método | Mac (prompts 51–52) |

- No existe un `win_puente.ps1`: **Gustavo no puede llegar a Tomás** por el puente.
- `win_coordinador.ps1` no incluye a Gustavo en su catálogo: solo Tomás, Ezequiel y cocina.
- Lo único del Windows que usa ese trabajo son los arreglos del prompt 35 (cliente A2A sin
  duplicados, `agente_local`/`agente_remoto`, caché de fichas), sobre los que el Mac construyó.

## Estado

Evidencias del Windows actualizadas con el código final. Commit local hecho; push a decisión
del usuario.

---

## Respuesta completa del asistente (chat)

### Mensajes de avance

> El Mac subió 2 commits más. Los reviso e integro antes de generar las evidencias, para que
> salgan sobre el código más reciente.

> Integré el código, ahora en `12bf9c5`, y reapliqué la ficha de Tomás. Pero **el servidor del
> Mac volvió a perder sus fichas** (`agente_ezequiel`, `agente_cocina`), seguramente al
> recargarse con esos commits. No genero las evidencias así, porque quedarían mal.
>
> Mientras Ezequiel las reaplica, adelanto lo de Gustavo: reviso los prompts 49, 51 y 52 para ver
> si piden algo del lado Windows.

> Las tres fichas están bien, pero el Mac subió 2 commits más. Los reviso: si los integro antes
> de generar, las evidencias salen sobre el código final.

> El prompt 53 del Mac agrega **fichas automáticas**: un modo `--vigilar` que las reaplica solo
> cuando el servidor se recarga. Justo lo que nos pasaba. Integro, veo si sirve también en Windows
> y genero las evidencias.

> No hay versión para Windows del script de fichas automáticas, pero el modo `--vigilar`
> funciona igual aquí. Lo dejo corriendo en una pestaña para Tomás, así la ficha se reaplica sola
> cada vez que el servidor se recargue.

> Sí quedó corriendo: el vigilante ya detectó la recarga de tu servidor y reaplicó «Agente de
> Tomás». Reviso las fichas del Mac y genero las evidencias.

> Las evidencias salieron 4 de 4, con las guardias en la ruta. Ahora las copio a la carpeta de
> entrega con la función del empaquetador y reviso qué cambió.

> Documento el prompt como el **54**, que por ahora es el siguiente número libre. Lo confirmo
> con el remoto antes del commit.

### Respuesta final

*(La respuesta final del turno resume este registro: el resultado 4 de 4 con las guardias,
dónde quedaron las evidencias, el vigilante de fichas y que del lado Windows no se hizo nada
especial para Gustavo.)*
