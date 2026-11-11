<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/44-resiliencia-remota-y-guardrails.md`  
> **Objetivo:** Prompt 44 · Dos implementaciones: resiliencia de agentes remotos y guardrails  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 0730 · **Última modificación:** 20261111 0835
<!--/encabezado-grupo-->

# Prompt 44 · Dos implementaciones: resiliencia de agentes remotos y guardrails

**Pedido del usuario (textual, consolidado):**

> Tenemos que hacer dos implementaciones técnicas especialmente importantes.
>
> **1. Cuando un agente remoto no está disponible.** En `src/coordinador/a2a.py`
> las llamadas HTTP tienen timeout pero no un manejo completo de excepciones. La
> mejora: capturar errores de conexión, timeout y respuestas HTTP inválidas, y
> devolver al supervisor un estado controlado, por ejemplo: "El agente de Fabio no
> está disponible temporalmente. Puedes intentar nuevamente más tarde. Los demás
> agentes continúan operativos." También evitar que un agente desconectado impida
> construir el catálogo de los agentes que sí funcionan.
>
> **2. Guardrails** en tres puntos:
> - Entrada: solicitudes vacías, excesivamente largas, fuera de dominio o
>   potencialmente maliciosas.
> - Salida: detección de credenciales, información sensible y respuestas que no
>   respeten las restricciones.
> - Comunicación A2A: tratar las respuestas de agentes remotos como datos no
>   confiables, nunca como instrucciones que el coordinador deba obedecer.
>
> Estos dos controles deberían tener pruebas automatizadas con pytest. Ahora que
> está abajo el Windows, puedes probarlo y dejar evidencia de ello.

**Tareas:**
1. `src/coordinador/a2a.py`: excepción `AgenteNoDisponible` + manejo de
   conexión/timeout/HTTP inválido/JSON inválido.
2. `src/coordinador/catalogo.py`: el catálogo se construye aunque un agente esté caído.
3. `src/coordinador/guardrails.py` (nuevo): controles de entrada, salida y A2A.
4. `src/coordinador/graph.py`: cablear guardrails (nodo de entrada + saneo de salida)
   y el estado controlado cuando el remoto no responde.
5. `tests/test_resiliencia_a2a.py` y `tests/test_guardrails.py` (pytest).
6. Probar con el Windows caído y dejar evidencia en `evidencias/`.
