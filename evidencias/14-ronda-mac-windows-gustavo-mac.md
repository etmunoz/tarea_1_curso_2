<!--encabezado-grupo-->
> **Archivo:** `evidencias/14-ronda-mac-windows-gustavo-mac.md`  
> **Objetivo:** Ronda end-to-end Mac ↔ Windows ↔ Gustavo · evidencia (mac)  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 2004 · **Última modificación:** 20261111 2004
<!--/encabezado-grupo-->

# Ronda end-to-end Mac ↔ Windows ↔ Gustavo · evidencia (mac)

Coordinador del Mac con cuatro agentes: **locales** `agente_ezequiel`, `agente_cocina`;
**remotos** `agente_tomas` (Windows, A2A nativo langgraph) y `agente_meteorologo` (Gustavo,
A2A clásico `SendMessage`). Corrida real:

```
> ¿Qué técnica uso si tengo desbalance de clases?
  ruta: guardia_entrada → supervisor → agente_local → guardia_salida
  [Agente de Ezequiel] … class weights, SMOTE/undersampling, F1/PR-AUC …

> ¿Cuánto cuesta una cazuela de vacuno para 6 personas?
  ruta: guardia_entrada → supervisor → agente_local → guardia_salida
  [Agente de cocina chilena] … Posta $6.750, Papa $1.080 … (costo por ingrediente)

> ¿Cuáles son los cinco principios del Reiki?
  ruta: guardia_entrada → supervisor → agente_remoto → guardia_salida
  [Agente de Tomás] … Solo por hoy: no te enojes / no te preocupes / sé agradecido / trabaja
  con honestidad / sé amable …            ← REMOTO en el Windows, por Cloudflare (cross-machine)

> ¿Qué clima hará mañana en Valdivia?
  ruta: guardia_entrada → supervisor → agente_no_disponible → guardia_salida
  El agente_meteorologo es el especialista para esta consulta, pero actualmente no está
  disponible. Puedes intentar nuevamente más tarde. Los demás agentes continúan operativos.
            ← su card se leyó (el supervisor lo eligió como especialista) pero su túnel
              parpadeó al consultar → RESILIENCIA (prompt 48, Corrección 1): no es sin_agente.

> ¿Quién descubrió América?
  ruta: guardia_entrada → supervisor → sin_agente → guardia_salida
  No tengo un agente para eso. Puedo ayudarte con: Agente de Ezequiel, Agente de cocina
  chilena, Agente de Tomás, agente_meteorologo.
```

## Lo que demuestra

- **Cross-machine real (Mac ↔ Windows):** la pregunta de Reiki la respondió **Tomás** en el
  Windows, por su túnel de Cloudflare, enrutado por el coordinador del Mac. Todo por A2A nativo.
- **Multi-dialecto:** el catálogo incluye a Gustavo (A2A clásico `SendMessage`); el supervisor lo
  eligió por su ficha.
- **Resiliencia:** el túnel de Gustavo parpadea; al fallar su `message/send`, el coordinador
  distingue "especialista caído" (`agente_no_disponible`) de "no hay agente" (`sin_agente`).
- **Guardrails** en cada respuesta (`guardia_entrada`/`guardia_salida`).

## Pendiente

La consulta de clima **efectiva** a Gustavo (y la evidencia live del cache del prompt 52) queda
pendiente de que su quick tunnel esté estable. La interop nosotros→Gustavo ya se probó con éxito
en el prompt 51 (ver `evidencias/13-interop-gustavo-mac.md`).
