<!--encabezado-grupo-->
> **Archivo:** `respuestas/33-windows-corrida-real-2-pc.md`  
> **Objetivo:** 33 · Respuesta — Windows: corrida real entre 2 PC (lado Windows), con las fichas reaplicadas  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2244 · **Última modificación:** 20261111 0735
<!--/encabezado-grupo-->

# 33 · Respuesta — Windows: corrida real entre 2 PC (lado Windows), con las fichas reaplicadas

Prompt: [`../prompts_ejecutados/33-windows-corrida-real-2-pc.md`](../prompts_ejecutados/33-windows-corrida-real-2-pc.md)

## 1. Fichas verificadas en los dos servidores

```text
Windows agente_tomas    -> 'Agente de Tomás'          — 'Maestro Reiki: explica los cinco principios (Gokai)…'
Mac     agente_ezequiel -> 'Agente de Ezequiel'       — 'Ingeniero de IA y Data Scientist: recomienda qué técnica…'
Mac     agente_cocina   -> 'Agente de cocina chilena' — 'Conoce recetas chilenas clásicas y calcula cuánto cuesta…'
```

## 2. Corrida del coordinador (Windows → Mac)

`win_coordinador.ps1 "https://requirements-early-describes-socket.trycloudflare.com/"`

| Pregunta | Agente | Equipo | Resultado |
|---|---|---|---|
| ¿Cuáles son los cinco principios del Reiki? | Agente de Tomás | Windows (local) | ✓ los 5 principios Gokai |
| ¿Qué métricas uso en un problema de regresión? | Agente de Ezequiel | Mac (por túnel) | ✓ MAE, RMSE, R² y MAPE |
| ¿Cuánto cuesta una cazuela de vacuno para 6 personas? | Agente de cocina chilena | Mac (por túnel) | ✓ total $11.302 CLP · $1.884 por persona |
| ¿Quién descubrió América? | — (sin_agente) | — | ✓ «No tengo un agente para eso…» |

**4 de 4 correctas** (en el prompt 32, con fichas genéricas, fueron 2 de 4).

Evidencias generadas en el Windows (`ASUS-ETMK`, 2026-11-11T01:42 UTC):
- [`../evidencias/04-catalogo-windows.txt`](../evidencias/04-catalogo-windows.txt): catálogo con las 3 fichas reales.
- [`../evidencias/05-ronda-windows.md`](../evidencias/05-ronda-windows.md): las 4 preguntas con ruta y respuesta.

Con esto queda demostrado que el ruteo funciona **en los dos sentidos**: el Mac ya lo había
hecho (registro 29 de Ezequiel, `05-ronda-mac.md`) y ahora lo hace el Windows.

## Lo bueno

- La prueba entre los dos PC funciona completa, todo por túneles HTTP de Cloudflare, sin LAN.
- El RAG de Tomás (Redis local, puerto 6380), el SQLite de Ezequiel y el costeo de cocina
  responden con datos reales.
- Las tildes llegan bien a los agentes y a las evidencias (arreglo del BOM, prompt 31).

## Lo malo / observaciones (no se corrigieron)

- **Respuestas duplicadas en `05-ronda-windows.md`:** cada respuesta aparece dos veces seguidas.
  Parece un detalle de `tools/guardar_evidencias.py` (junta el texto del mensaje y el del
  artefacto A2A). No afecta el ruteo.
- **Etiqueta `agente_remoto` también para Tomás**, aunque es local: el nodo del coordinador se
  llama así para cualquier llamada A2A.
- **Mensaje de "sin agente" mezclado:** «Puedo ayudarte con: Agente de Tomás, agente_ezequiel,
  agente_cocina». Usa el nombre de la ficha para el local y el id del grafo para los remotos.
- Recordatorio (prompt 32): si los servidores se recargan, las fichas se pierden y hay que
  volver a correr `configurar_fichas.py`.

## Encabezados de las evidencias (arreglado)

- `guardar_evidencias.py` reescribe `04-catalogo-windows.txt` y `05-ronda-windows.md` **sin el
  encabezado del grupo**, y `aplicar_encabezados.py --check` falló en esos dos archivos. En el
  Mac, Ezequiel los arregló corriendo la herramienta después.
- Se aplicó el encabezado **solo a esos dos archivos** (`procesar()`), para no cambiar la fecha de
  los otros 164.
- La herramienta, corrida en Windows, escribió la ruta con barra invertida
  (`evidencias\05-ronda-windows.md`), porque usa `str(Path)`. Se corrigió a `/` con un script
  aparte; `sed` falló dos veces con el escapado de `\`. **Pendiente:** usar `.as_posix()` en
  `aplicar_encabezados.py` para que en Windows no vuelva a pasar.
- `--check` → `OK · 168 archivos con encabezado`.

## Estado

Corrida real del lado Windows **completa y correcta**. Evidencias y registros **sin commit**.
Faltan las capturas manuales `01-saltos.png` y `03-tunel.png` de la guía.

---

## Respuesta completa del asistente (chat)

### Mensajes de avance

> Las tres fichas están bien, en los dos servidores. Repito la corrida del coordinador.

> Las 4 preguntas se rutearon bien. En la línea de cocina no se ve el texto de la respuesta, así
> que reviso la evidencia completa.

> Las evidencias están completas: Tomás (Windows), Ezequiel y cocina (Mac) contestaron, y la
> pregunta fuera de tema quedó sin agente. Encontré dos detalles menores y los dejo anotados.
> Ahora registro todo como el prompt 33.

> La revisión de encabezados marcó un archivo, `evidencias/05-ronda-windows.md`. Veo qué pasa.

> El script de evidencias reescribe los archivos sin el encabezado del grupo. En el Mac,
> Ezequiel lo agregó después con la herramienta. Lo aplico solo a estos dos archivos, para no
> cambiar la fecha de los otros 164.

> El encabezado quedó con la ruta escrita `evidencias\...` (barra de Windows), y el resto del
> repo usa `/`. Lo corrijo y lo anoto como detalle de la herramienta.

> El escapado de `sed` se me cruza con la barra invertida. Lo hago con un pequeño script de Python.

> Corregido. Anoto en el registro 33 los detalles de los encabezados.

### Respuesta final

> ¡Funcionó! El coordinador del Windows ruteó bien las 4 preguntas usando agentes de los dos
> computadores:
>
> | Pregunta | Agente | Equipo |
> |---|---|---|
> | Cinco principios del Reiki | Agente de Tomás | Windows (local) ✓ |
> | Métricas de regresión | Agente de Ezequiel | Mac ✓ |
> | Cazuela para 6 personas | Agente de cocina chilena | Mac ✓ ($11.302 total, $1.884 por persona) |
> | ¿Quién descubrió América? | ninguno | ✓ |
>
> Con la ronda del Mac que subió Ezequiel, queda demostrado el ruteo en los dos sentidos.
>
> Las evidencias quedaron en `evidencias/04-catalogo-windows.txt` y `evidencias/05-ronda-windows.md`.
>
> Detalles menores que anoté y no corregí: cada respuesta aparece duplicada en la evidencia;
> la ruta dice `agente_remoto` incluso para Tomás, que es local; y el mensaje de "sin agente"
> mezcla nombres de ficha con ids de grafo.
>
> Las dos evidencias habían quedado sin el encabezado del grupo. Se lo agregué solo a ellas y
> corregí la barra invertida que la herramienta puso en la ruta. Ahora la revisión pasa en los
> 168 archivos.
>
> Todo quedó registrado como el prompt 33. Las evidencias y los registros 32 y 33 todavía no
> tienen commit. Faltan las capturas manuales `01-saltos.png` y `03-tunel.png` que pide la guía.
