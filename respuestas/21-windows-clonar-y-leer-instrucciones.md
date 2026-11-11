<!--encabezado-grupo-->
> **Archivo:** `respuestas/21-windows-clonar-y-leer-instrucciones.md`  
> **Objetivo:** 21 · Respuesta — Windows: clonar el repo y leer las instrucciones  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2208 · **Última modificación:** 20261110 2208
<!--/encabezado-grupo-->

# 21 · Respuesta — Windows: clonar el repo y leer las instrucciones

Prompt: [`../prompts_ejecutados/21-windows-clonar-y-leer-instrucciones.md`](../prompts_ejecutados/21-windows-clonar-y-leer-instrucciones.md)

## Qué se hizo

- Se verificó que la carpeta `C:\Users\etmun\proyecto\tarea_1_curso_2` estaba vacía y se clonó
  ahí con `git clone https://github.com/etmunoz/tarea_1_curso_2.git` (git 2.56, gh 2.96).
- Se leyeron `guia_ezequiel_tomas.md` (sección **B · Windows**), `README.md`,
  `scripts/setup_windows.ps1`, `win_servir.ps1`, `win_tunel.ps1`, `win_app.ps1`,
  `win_coordinador.ps1` y `docker-compose.yml`.
- Se revisó el estado del PC **sin modificar nada** y se presentó el plan para aprobación.

## Resultado

```text
winget / uv 0.11.24 / cloudflared 2026.10.7 / Docker 29.8.2   -> ya instalados, Docker corriendo
.env                                                          -> no existe (esperado en un clon)
ExecutionPolicy (CurrentUser)                                 -> Undefined
scripts/*.ps1                                                 -> UTF-8 SIN BOM
```

## Lo bueno

- Todos los prerrequisitos ya estaban instalados: el setup no tenía que instalar nada.

## Lo malo / riesgos detectados (antes de ejecutar)

- **Codificación de los `.ps1`:** están en UTF-8 sin BOM. Windows PowerShell 5.1 los lee como
  ANSI y los acentos se ven como `Â·`, `Ã¡`. Además del problema visual, las preguntas de
  `win_coordinador.ps1` (`¿Cuáles son…?`) pueden llegar mal escritas a los agentes y a las
  evidencias. **Pendiente:** guardarlos con BOM o correrlos con `pwsh` (PowerShell 7).
- **Política de ejecución `Undefined`:** puede bloquear los `.ps1`. Para no cambiar un ajuste
  de seguridad del sistema, se decidió correrlos con `powershell -ExecutionPolicy Bypass -File …`
  (solo para esa ejecución).
- **La clave se pide por consola** (`Read-Host`): hay que pegarla en una terminal interactiva.

## Estado

Repo clonado y plan aprobado por el usuario → sigue en el prompt 22.
