<!--encabezado-grupo-->
> **Archivo:** `respuestas/22-windows-ejecutar-setup.md`  
> **Objetivo:** 22 · Respuesta — Windows: ejecutar setup_windows.ps1 (clave Gemini y AVG)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 2208 · **Última modificación:** 20261110 2208
<!--/encabezado-grupo-->

# 22 · Respuesta — Windows: ejecutar `setup_windows.ps1` (clave Gemini y AVG)

Prompt: [`../prompts_ejecutados/22-windows-ejecutar-setup.md`](../prompts_ejecutados/22-windows-ejecutar-setup.md)

## Qué se hizo (cronología)

1. **1ª corrida** en una terminal interactiva:
   `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1`
   - Pasos 1/6 y 2/6 OK: Python 3.13 y 134 paquetes instalados con `uv sync`.
   - Paso 3/6: creó `.env` y quedó esperando `Pega tu GOOGLE_API_KEY`.
2. El usuario pegó la clave **directamente en `.env`**. Se comprobó (sin mostrarla) que estaba.
   - ⚠ **Riesgo encontrado:** si se presionaba Enter vacío en el prompt, el script reemplaza
     `GOOGLE_API_KEY=...` por `GOOGLE_API_KEY=` y **borra la clave recién puesta**
     (`setup_windows.ps1`, línea del `-replace`). Por eso se canceló esa corrida con Ctrl+C,
     se verificó que la clave seguía intacta y se volvió a correr (con clave presente, el
     script se salta la pregunta).
3. **2ª corrida:** en el paso 4/6 la prueba de Gemini se quedó **reintentando** (tenacity) y el
   usuario la cortó con Ctrl+C (`KeyboardInterrupt`).
4. **Diagnóstico:** una llamada REST directa a Gemini (urllib, sin reintentos) respondió
   **HTTP 200 "OK"** → la clave es válida. La 3ª corrida mostró el error real:
   `[SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer certificate`.
5. **Causa raíz:** el certificado que recibe Python para `generativelanguage.googleapis.com`
   lo emite **"AVG Web/Mail Shield Root"** (AVG Antivirus inspecciona HTTPS). Windows confía
   en esa raíz (por eso urllib funcionó), pero la librería `google-genai` usa el paquete
   **certifi**, que no la incluye.
6. **Prueba temporal** (sin tocar nada del proyecto): bundle certifi + `C:\ProgramData\AVG\Antivirus\wscert.pem`
   en `SSL_CERT_FILE` → Gemini respondió. Queda como alternativa si no se quiere tocar AVG.
7. **Arreglo definitivo (hecho por el usuario en AVG):** Menú → Configuración → General →
   Excepciones → agregar `https://generativelanguage.googleapis.com/*` y
   `https://*.trycloudflare.com/*` (esta segunda para cuando el coordinador llame al túnel del Mac).
8. Con la excepción, `uv run python tools/probar_gemini.py` → `✓ Gemini respondió: 'OK'`.
9. El paso 5/6 (Redis) **falló**: `Bind for 0.0.0.0:6379 failed: port is already allocated` → ver prompt 23.

## Lo bueno

- uv, Python 3.13 y dependencias quedaron instalados en una sola pasada.
- La clave de Gemini es válida y, con la excepción de AVG, funciona sin parches.

## Lo malo / lo que no resultó

- La prueba de Gemini con error SSL **reintenta largo rato** antes de fallar; parece colgada.
- `probar_gemini.py` falla al imprimir `✓`/`✗` cuando la salida va a un pipe con cp1252
  (`UnicodeEncodeError`); se evita con `PYTHONIOENCODING=utf-8`. En la consola normal se ve bien.
- Avisos `SyntaxWarning: invalid escape sequence '\/'` de `google/genai/types.py`: son de la
  librería, inofensivos.
- El script sigue al paso 5 aunque el 4 falle (los comandos nativos no detienen el script en PS 5.1).

## Lo que se arregló

| Problema | Arreglo |
|---|---|
| Enter vacío borraría la clave | Se canceló el prompt y se re-corrió con la clave ya en `.env` |
| SSL por AVG | Excepción de URL en AVG (alternativa probada: `SSL_CERT_FILE` con bundle) |

## Pendiente sugerido

- Que `setup_windows.ps1` no sobrescriba la clave si la respuesta viene vacía.
- Agregar a la guía (sección *Problemas típicos*) el caso de antivirus con inspección HTTPS.
