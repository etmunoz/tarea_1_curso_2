<!--encabezado-grupo-->
> **Archivo:** `respuestas/51-interop-sendmessage-gustavo.md`  
> **Objetivo:** Respuesta 51 · Interop nosotros→Gustavo (dialecto SendMessage)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1738 · **Última modificación:** 20261111 1957
<!--/encabezado-grupo-->

# Respuesta 51 · Interop nosotros→Gustavo (dialecto SendMessage)

Prompt: [`../prompts_ejecutados/51-interop-sendmessage-gustavo.md`](../prompts_ejecutados/51-interop-sendmessage-gustavo.md)

> Rama `prompt-48-robustez`. **`main` no modificado.**

## El hallazgo

El `-32601` no era un bug de Gustavo: su servidor usa un **tercer dialecto** A2A.

| | Método | Mensaje | Header |
|---|---|---|---|
| nosotros (langgraph) | `message/send` | role user, parts con `kind` | — |
| a2a estándar | `message/send` | role user, `kind:message` | — |
| **Gustavo** | **`SendMessage`** | **role `ROLE_USER`**, parts **sin `kind`** | **`A2A-Version: 1.0`** |

Además su respuesta llega "doble-envuelta": `parts[0].text` es un string con un repr de lista
(`"[{'type':'text','text':'…','extras':{…}}]"`).

## La solución (`src/coordinador/a2a.py`)

- **Fallback** en `enviar_mensaje`: si en dialecto clásico `message/send` responde `-32601`, se
  reintenta UNA vez con `SendMessage` (role `ROLE_USER`, parts sin `kind`, header `A2A-Version`).
- **Desanidado** (`_desanidar`): si el texto es un repr de lista/dict, se evalúa con
  `ast.literal_eval` y se extrae el/los `text` internos.
- **Extractor** (`_textos`): ahora una parte de texto es cualquier dict con `text` str (cubre
  `kind:text`, `type:text` y `{text}`).
- Helpers: `_cuerpo_message_send`, `_cuerpo_sendmessage`, `_codigo_error`.

## Corrida real (nuestro cliente → agente de Gustavo, por Cloudflare)

```
dialecto: clasico
> ¿Qué clima hará mañana en Valdivia?
  Para mañana en Valdivia se esperan chubascos, con una temperatura máxima de 15 °C y una mínima de 6 °C.
> ¿Y en Concepción hoy?
  El pronóstico para hoy en Concepción indica cielos nublados al amanecer, lloviznas por la
  mañana y lluvia débil en la noche, con una temperatura mínima de 8 °C y una máxima de 18 °C.
```

Evidencia completa: `evidencias/13-interop-gustavo-mac.md`.

## Pruebas

`tests/test_interop_sendmessage_51.py` (5): desanidado, extractor de `text`, fallback a
`SendMessage` con header (exactamente un reintento), y no-reintento cuando `message/send` sirve.
Suite completa: **146 passed, 1 skipped**.

## Estado

**Interoperabilidad A2A en AMBOS sentidos**: Gustavo→nosotros (puente, prompt 49) y
**nosotros→Gustavo** (este fallback). Con esto el coordinador ya puede enrutar al
`agente_meteorologo` de Gustavo. Implementado en la rama; `main` intacto.
