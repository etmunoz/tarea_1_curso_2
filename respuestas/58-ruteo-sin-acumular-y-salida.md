<!--encabezado-grupo-->
> **Archivo:** `respuestas/58-ruteo-sin-acumular-y-salida.md`  
> **Objetivo:** 58 · Respuesta — Ruteo sin acumular (solo la pregunta actual) + botones Nueva conversación/Salir  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261112 1558 · **Última modificación:** 20261112 1558
<!--/encabezado-grupo-->

# 58 · Respuesta — Ruteo sin acumular + salida/reset

Prompt: [`../prompts_ejecutados/58-ruteo-sin-acumular-y-salida.md`](../prompts_ejecutados/58-ruteo-sin-acumular-y-salida.md)

## 1 · Por qué el panel "daba tantas vueltas"

El grafo coordinador (`src/coordinador/graph.py`) define:

```python
ruta: Annotated[list[str], operator.add]        # reductor: concatena
# ...
graph = builder.compile(checkpointer=InMemorySaver())
```

Como el `thread_id` se mantiene fijo por sesión (sessionStorage), el checkpointer conserva el
estado entre preguntas y `operator.add` **concatena** la ruta de cada nueva pregunta a la anterior.
Resultado: con 3 preguntas, el panel mostraba ~12 pasos (3 rondas encadenadas).

## 2 · Fix (solo los pasos de la pregunta actual)

En `tools/coordinador_web.py`, `_preguntar` mide la longitud previa de `ruta` en el estado del
thread y se queda con los pasos nuevos:

```python
cfg = {"configurable": {"thread_id": thread or str(uuid.uuid4())}}
try:
    previos = len((g.get_state(cfg).values or {}).get("ruta", []))
except Exception:
    previos = 0
r = g.invoke({"messages": [HumanMessage(content=texto)]}, cfg)
ruta_total = r.get("ruta", [])
ruta = ruta_total[previos:] if 0 <= previos <= len(ruta_total) else ruta_total
```

### Verificación real (API local del coordinador, MISMO thread)

```
1a pregunta: ruta = ['guardia_entrada','supervisor','agente_local','guardia_salida']
2a pregunta: ruta = ['guardia_entrada','supervisor','agente_remoto','guardia_salida']  (elegido: Agente de Ezequiel)
```
→ Cada pregunta muestra **4 pasos**, no se acumulan (antes la 2ª habría mostrado 8).

## 3 · Salida / reset

Botones nuevos en la barra superior:

- 🔄 **Nueva conversación** (`nuevaConversacion`): genera un `thread` nuevo, lo guarda y limpia
  chat + ruteo a su estado vacío. Útil además para empezar un hilo limpio.
- 🚪 **Salir**: limpia la sesión (`sessionStorage`) e intenta olvidar el Basic Auth pidiendo con
  credenciales inválidas; muestra una pantalla "Sesión cerrada" con botón "Entrar de nuevo".
  **Caveat:** el logout de Basic Auth no es 100% confiable entre navegadores (cachean la
  credencial); si no re-pregunta la clave, basta cerrar la pestaña.

## Archivos tocados

- `tools/coordinador_web.py` — recorte de `ruta` en `_preguntar`; `let thread` + `nuevaConversacion`;
  botones 🔄/🚪 y sus handlers.
- `prompts_ejecutados/58-…md` y `respuestas/58-…md` (este registro).

## Estado

- Desplegado y verificado en `https://coordinador.etmk.cl` (commit `06c9d44`). El panel muestra la
  ruta de la consulta actual; existen Nueva conversación y Salir.

## Pendientes

- Regenerar el zip de entrega para incluir estos cambios (y el registro 57/58) cuando se pida.
- Housekeeping: revocar el sudo temporal (`sudo rm /etc/sudoers.d/90-administrator-nopasswd`).
