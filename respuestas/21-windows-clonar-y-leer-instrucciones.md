<!--encabezado-grupo-->
> **Archivo:** `respuestas/21-windows-clonar-y-leer-instrucciones.md`  
> **Objetivo:** 21 · Respuesta — Windows: clonar el repo y leer las instrucciones  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2208 · **Última modificación:** 20261110 2306
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

---

## Respuesta completa del asistente (chat)

### Mensajes de avance

> La carpeta está vacía. Clono el repo ahí.

### Respuesta final

> Cloné el repo en `C:\Users\etmun\proyecto\tarea_1_curso_2` y leí las instrucciones para
> Windows. Me detengo aquí, como pediste: todavía no ejecuté nada.
>
> **Qué dicen las instrucciones (rol Windows = Tomás)**
> La guía está en `guia_ezequiel_tomas.md`, sección B. El Windows corre el agente Tomás
> (Maestro Reiki), que usa un RAG sobre un Redis local en Docker. Además abre un túnel de
> Cloudflare hacia el Mac de Ezequiel y corre un coordinador que trabaja en ambos sentidos.
>
> **Estado de tu PC:** ya están instalados winget, uv 0.11.24, cloudflared 2026.10.7 y
> Docker 29.8.2, y Docker está corriendo. Aún no existe el archivo `.env`.
>
> **Lo que propongo hacer**
>
> 1. **Ejecutar el setup (`scripts/setup_windows.ps1`).** Como ya tienes todo instalado, no
>    instalará nada nuevo. Hace esto:
>    - instala Python 3.13 con `uv` y corre `uv sync` para crear `.venv`;
>    - crea `.env` a partir de `.env.example`;
>    - prueba tu clave de Gemini;
>    - levanta Redis con `docker compose up -d` (imagen `redis/redis-stack`, puertos 6379 y 8001);
>    - carga el contenido de Reiki en el RAG.
> 2. **La `GOOGLE_API_KEY` la pones tú.** El script la pide de forma interactiva, y esta
>    sesión no puede responder esa pregunta. Además, no corresponde que yo escriba tu clave.
>    Mi propuesta: creo el `.env`, tú pegas la clave a mano y después yo sigo con el resto del setup.
> 3. **Dejar para después los pasos que necesitan terminales abiertas o al otro equipo:**
>    - `win_servir.ps1` (agente en el puerto 2024) y `win_tunel.ps1` (túnel) quedan
>      corriendo, así que conviene abrirlos en pestañas de terminal aparte;
>    - `win_coordinador.ps1 "https://<tunel-mac>"` necesita la URL del túnel del Mac de Ezequiel.
>
> **Dos problemas que encontré**
> - **Codificación de los `.ps1`:** están en UTF-8 sin BOM. Windows PowerShell 5.1 los lee
>   mal, y los acentos y la "¿" salen como "Â¿QuÃ©". Esto puede alterar las preguntas que
>   envía `win_coordinador.ps1` y quedar mal escrito en las evidencias. La solución es guardar
>   esos archivos con BOM; es un cambio pequeño. También se pueden correr con `pwsh`
>   (PowerShell 7) si lo tienes.
> - **Permisos de ejecución:** tu política de ejecución está en `Undefined`, y probablemente
>   Windows bloqueará los `.ps1`. La guía sugiere `Set-ExecutionPolicy -Scope CurrentUser
>   RemoteSigned`. Como es un ajuste de seguridad, prefiero que lo apliques tú. La otra opción
>   es que yo corra cada script con `-ExecutionPolicy Bypass` solo para esa ejecución, sin
>   cambiar nada de forma permanente.
>
> Dime si sigo así o si quieres cambiar algo, por ejemplo usar `-SinRag` para omitir Redis.
