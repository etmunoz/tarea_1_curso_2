<!--encabezado-grupo-->
> **Archivo:** `respuestas/30-windows-commit-push-registros-25-28.md`  
> **Objetivo:** 30 · Respuesta — Windows: commit y push de los registros 25–28  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2224 · **Última modificación:** 20261111 1204
<!--/encabezado-grupo-->

# 30 · Respuesta — Windows: commit y push de los registros 25–28

> **Nota de numeración:** este registro se escribió como el 29, pero Ezequiel publicó antes su propio 29 desde el Mac («Corrida real entre 2 computadores»). Se renumeró a 30; las citas del chat que decían «29» se ajustaron a «30».

Prompt: [`../prompts_ejecutados/30-windows-commit-push-registros-25-28.md`](../prompts_ejecutados/30-windows-commit-push-registros-25-28.md)

## Qué se hizo

```text
git add prompts_ejecutados/ respuestas/      -> 13 archivos (8 nuevos: 25–28; 5 modificados: README + 21–24)
git commit   -> 91f870d 25–28 · Windows: agente Tomás y túnel verificados; respuestas completas en español
git push     -> a467e0c..91f870d  main -> main   (main == origin/main)
```

## Observaciones

- Git volvió a avisar `LF will be replaced by CRLF`: normal en Windows, no cambia el contenido.
- Este registro (30) se escribió **después** del commit para poder anotar su hash; queda sin
  commit y entra en el próximo.

## Estado

Repo remoto al día con todo lo hecho en el Windows hasta el túnel. Siguiente: intercambiar
URLs de túnel con el Mac y correr `win_coordinador.ps1` (antes, arreglar el BOM de los `.ps1`).

---

## Respuesta completa del asistente (chat)

### Mensaje de avance

> Hice el commit `91f870d` y el push a `origin/main`. Ahora registro este paso como el prompt 30.

### Respuesta final

> Listo: el commit `91f870d` («25–28 · Windows: agente Tomás y túnel verificados; respuestas
> completas en español») ya está en `origin/main`, con 13 archivos: los registros nuevos 25 a 28,
> el índice y las respuestas completas agregadas a 21–24.
>
> Este paso quedó registrado como el prompt 30. Lo escribí después del commit para poder
> anotar el hash, así que entra en el próximo commit.
>
> Para seguir con la prueba entre los dos PC necesito la URL del túnel del Mac. Antes de
> correr el coordinador arreglo la codificación de los `.ps1`, para que las preguntas con
> tildes lleguen bien escritas.
