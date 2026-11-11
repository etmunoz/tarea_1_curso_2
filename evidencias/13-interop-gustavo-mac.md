<!--encabezado-grupo-->
> **Archivo:** `evidencias/13-interop-gustavo-mac.md`  
> **Objetivo:** Interoperabilidad NOSOTROS → agente de Gustavo · evidencia (mac)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1737 · **Última modificación:** 20261111 1957
<!--/encabezado-grupo-->

# Interoperabilidad NOSOTROS → agente de Gustavo · evidencia (mac)

Prompt 51. Cierra el sentido que faltaba: nuestro coordinador/cliente llamando al
`agente_meteorologo` de Gustavo.

## El hallazgo

El `-32601` NO era un bug de Gustavo: su servidor (SDK a2a-protocol.org) usa un **tercer
dialecto** A2A:

| | Método | Mensaje | Header | Respuesta |
|---|---|---|---|---|
| nosotros (langgraph) | `message/send` | role user, parts con `kind` | — | directa |
| a2a estándar | `message/send` | role user, `kind:message` | — | directa |
| **Gustavo** | **`SendMessage`** | **role `ROLE_USER`**, parts **sin `kind`** | **`A2A-Version: 1.0`** | texto en repr anidado |

## La solución (en `src/coordinador/a2a.py`)

- **Fallback**: si en dialecto clásico `message/send` responde `-32601`, se reintenta UNA vez con
  `SendMessage` + `role ROLE_USER` + parts sin `kind` + header `A2A-Version: 1.0`.
- **Desanidado**: su respuesta llega como `"[{'type':'text','text':'…','extras':{…}}]"`; se
  desanida con `ast.literal_eval` + el extractor de `text` (que ahora reconoce `kind`/`type`/`text`).

## Corrida real (nuestro cliente → agente de Gustavo, por Cloudflare)

```
dialecto: clasico
> ¿Qué clima hará mañana en Valdivia?
  Para mañana en Valdivia se esperan chubascos, con una temperatura máxima de 15 °C y una mínima de 6 °C.
> ¿Y en Concepción hoy?
  El pronóstico para hoy en Concepción indica cielos nublados al amanecer, lloviznas por la mañana y lluvia débil en la noche, con una temperatura mínima de 8 °C y una máxima de 18 °C.
```

## Pruebas

`tests/test_interop_sendmessage_51.py` (5): desanidado, extractor de `text`, fallback a
`SendMessage` con header (exactamente un reintento) y no-reintento cuando `message/send` sirve.
Suite completa: 146 passed, 1 skipped.

## Estado

Interoperabilidad A2A **en ambos sentidos**: Gustavo → nosotros (por el puente, prompt 49) y
**nosotros → Gustavo** (por este fallback). Implementado en la rama `prompt-48-robustez`.

## Ronda end-to-end (coordinador con Gustavo en el catálogo)

Catálogo: `agente_ezequiel` (local) + `agente_cocina` (local) + `agente_meteorologo` (remoto,
Gustavo, por Cloudflare). Corrida real:

```
> ¿Qué técnica uso si tengo desbalance de clases?
  ruta: guardia_entrada → supervisor → agente_local → guardia_salida
  [Agente de Ezequiel] … class weights, resampleo (SMOTE/undersampling), F1/PR-AUC …

> ¿Cuánto cuesta un pastel de choclo para 4 personas?
  ruta: guardia_entrada → supervisor → agente_local → guardia_salida
  [Agente de cocina chilena] … detalle por ingrediente … total CLP …

> ¿Qué clima hará mañana en Valdivia?
  ruta: guardia_entrada → supervisor → agente_remoto → guardia_salida
  [agente_meteorologo] Mañana en Valdivia se esperan chubascos con una máxima de 15 °C y una mínima de 6 °C.

> ¿Quién ganó el mundial de 1962?
  ruta: guardia_entrada → supervisor → sin_agente → guardia_salida
  No tengo un agente para eso. Puedo ayudarte con: Agente de Ezequiel, Agente de cocina chilena, agente_meteorologo.
```

El supervisor eligió al `agente_meteorologo` de Gustavo por su ficha y lo consultó por A2A
(dialecto `SendMessage`, desanidado). Pasa por los guardrails (`guardia_entrada`/`guardia_salida`)
como cualquier otro. Interoperabilidad A2A **en ambos sentidos**, end-to-end.

## Confirmación contra el repo de Gustavo (prompt 52)

Repo: https://github.com/guswolf-007/taller_A2A_uai · su servidor (`src/comun/servidor.py`) usa
**FastAPI + SDK a2a-protocol.org** (`create_jsonrpc_routes(manejador, rpc_url="/")`), con el método
**`SendMessage`** y respuesta en *content blocks* (`[{'type':'text','text':…}]`). Esto confirma que
nuestro fallback (prompt 51) y el desanidado coinciden con su implementación real.

**Mejora (prompt 52):** `a2a._cache_metodo` recuerda, por host, que un servidor necesita
`SendMessage`, para **no gastar el `message/send` fallido en cada llamada** (la 2ª consulta va
directa). Probado en `tests/test_interop_sendmessage_51.py::test_cache_metodo_evita_reintento`.
