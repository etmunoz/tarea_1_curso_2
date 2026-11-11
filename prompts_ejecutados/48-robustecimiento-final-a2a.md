<!--encabezado-grupo-->
> **Archivo:** `prompts_ejecutados/48-robustecimiento-final-a2a.md`  
> **Objetivo:** Prompt para Claude Code — Robustecimiento final del Taller A2A  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261111 1342 · **Última modificación:** 20261111 1738
<!--/encabezado-grupo-->

# Prompt para Claude Code — Robustecimiento final del Taller A2A

## 1. Contexto y objetivo

Estás trabajando en el repositorio `etmunoz/tarea_1_curso_2`, correspondiente a la Tarea 1 del Curso 2 del programa Certified Professional Agentic AI de la Universidad Adolfo Ibáñez.

El proyecto implementa una arquitectura multiagente con LangGraph y comunicación A2A nativa, utilizando agentes locales y remotos conectados mediante túneles HTTP de Cloudflare.

Existe un coordinador basado en el patrón Supervisor que descubre agentes mediante sus Agent Cards, selecciona el agente apropiado y le envía solicitudes mediante A2A.

El proyecto ya incorpora:
- Guardrails de entrada, salida y respuestas A2A.
- Manejo de agentes no disponibles.
- Catálogo de agentes con caché y TTL.
- Lista configurable de agentes permitidos.
- Pruebas automatizadas con pytest.
- Evidencias de funcionamiento entre Mac y Windows.
- Documento de entrega y diagramas de arquitectura.

**Tu objetivo es corregir cinco áreas de mejora identificadas en una revisión técnica, manteniendo la arquitectura actual y asegurando que las modificaciones sean verificables.**

No debes limitarte a proponer soluciones. Debes implementarlas, probarlas y documentarlas.

## 2. Instrucciones generales obligatorias

Antes de modificar cualquier archivo:

1. Lee `AGENTS.md` y respeta sus convenciones.
2. Inspecciona la estructura actual del repositorio.
3. Revisa especialmente:
   - `src/coordinador/graph.py`
   - `src/coordinador/catalogo.py`
   - `src/coordinador/a2a.py`
   - `src/coordinador/guardrails.py`
   - `src/coordinador/prompts.py`
   - Los tests existentes.
   - `evidencias/`
   - `entrega/documento-entrega.md`
   - Los scripts de generación de PDF y empaquetado.
4. Identifica qué problemas siguen presentes en el código actual.
5. No reimplementes funcionalidades que ya estén correctamente resueltas.
6. Mantén la compatibilidad con Python 3.13, `uv` y LangGraph.
7. Conserva la comunicación A2A nativa.
8. No introduzcas dependencias innecesarias.
9. No modifiques los agentes de Fabio y Gustavo ni inventes funcionalidades para ellos.
10. No incluyas credenciales, tokens o secretos en archivos versionados, logs ni evidencias.

Trabaja incrementalmente, verificando cada modificación antes de continuar.

---

# 3. Corrección 1 — Agente existente, pero temporalmente desconectado

## Problema identificado

Cuando el agente de Tomás está desconectado, el catálogo puede marcarlo como no disponible.

Sin embargo, ante una pregunta que corresponde a su especialidad, el supervisor puede responder mediante la ruta `sin_agente`, indicando que no existe un agente capaz de resolver la solicitud.

Esto confunde dos situaciones distintas:

- **Agente inexistente:** ningún agente registrado posee la capacidad solicitada.
- **Agente no disponible:** existe un agente especializado, pero no puede responder temporalmente.

Estas situaciones deben distinguirse tanto en la lógica como en las respuestas.

## Implementación requerida

### A. Separar capacidad de disponibilidad

Revisa el modelo del catálogo y asegúrate de representar separadamente:

- Identidad del agente.
- Capacidades declaradas.
- Estado de disponibilidad.
- Último momento de verificación.
- Motivo de indisponibilidad, cuando exista.

La pérdida temporal de conectividad no debe eliminar las capacidades conocidas de un agente.

Utiliza la última Agent Card válida cuando sea apropiado, identificándola como información almacenada en caché y evitando confundirla con una verificación de disponibilidad actual.

### B. Modificar el enrutamiento

El supervisor debe poder identificar al agente especializado aunque esté desconectado.

Cuando corresponda, debe seleccionar una ruta específica, por ejemplo:

`guardia_entrada → supervisor → agente_no_disponible → guardia_salida`

No debe utilizar `sin_agente` si existe evidencia suficiente de que el agente adecuado está registrado, pero temporalmente indisponible.

### C. Mantener una respuesta controlada

Ejemplo:

"El Agente de Tomás es el especialista para esta consulta, pero actualmente no está disponible. Puedes intentar nuevamente más tarde. Los demás agentes continúan operativos."

La respuesta no debe revelar URLs internas, excepciones técnicas, tokens ni detalles innecesarios de infraestructura.

### D. Casos especiales

Considera:

- Agente desconectado antes de construir el catálogo.
- Agente que se desconecta después de ser seleccionado.
- Agent Card almacenada en caché.
- Agente que vuelve a conectarse.
- Agente nunca descubierto, sin capacidades conocidas.
- Varios agentes con capacidades equivalentes, uno disponible y otro desconectado.

Cuando exista otro agente autorizado y disponible con capacidad equivalente, evalúa un fallback controlado, evitando reintentos ilimitados o enrutamiento circular.

## Pruebas requeridas

Implementa tests para demostrar:

1. Agente existente y disponible.
2. Agente existente y desconectado.
3. Agente inexistente.
4. Desconexión durante la consulta.
5. Recuperación después de reconexión.
6. Otros agentes continúan funcionando.
7. El sistema no confunde indisponibilidad con ausencia de capacidad.

---

# 4. Corrección 2 — Fortalecer los guardrails

## Problema identificado

Los guardrails actuales se basan principalmente en patrones heurísticos y expresiones regulares.

Esto permite detectar algunos ataques conocidos, pero no constituye una protección completa frente a prompt injection, jailbreaks o manipulación mediante respuestas de agentes remotos.

## Objetivo

Implementar una defensa por capas, proporcional al alcance académico del proyecto.

No prometas seguridad absoluta.

## Implementación requerida

### A. Validación estructural de entrada

Mantén y mejora:

- Detección de solicitudes vacías.
- Límites de tamaño.
- Validación de tipos.
- Normalización prudente del texto.
- Identificación de patrones sospechosos.

Evita bloquear consultas legítimas únicamente porque contienen palabras asociadas a seguridad o ataques.

### B. Separación de instrucciones y datos

Asegura que las respuestas de agentes remotos:

- Nunca se incorporen como instrucciones privilegiadas.
- No puedan modificar el prompt del supervisor.
- No puedan alterar la lista de agentes permitidos.
- No puedan ordenar nuevas llamadas a herramientas.
- No puedan modificar el estado del coordinador fuera del contrato definido.

La separación debe implementarse mediante el flujo y los tipos de datos, no únicamente mediante advertencias textuales.

### C. Validación de salida

Conserva:

- Redacción de secretos.
- Control de longitud.
- Manejo de respuestas vacías.

Agrega, cuando corresponda:

- Validación de estructura.
- Comprobación de tipos.
- Identificación de contenido inesperado.
- Manejo seguro de respuestas malformadas.

### D. Tratamiento de instrucciones maliciosas

Actualmente una respuesta remota sospechosa puede mostrarse acompañada de una advertencia.

Evalúa una política configurable con tres resultados:

- `ALLOW`: respuesta aceptada.
- `SANITIZE`: respuesta saneada.
- `BLOCK`: respuesta bloqueada.

Define claramente los criterios.

No confíes únicamente en la presencia de determinadas palabras o frases.

### E. Observabilidad

Registra eventos de seguridad sin almacenar innecesariamente el contenido sensible de las solicitudes.

Incluye:

- Tipo de validación.
- Resultado.
- Agente involucrado.
- Identificador de correlación.
- Motivo técnico resumido.

## Pruebas requeridas

Crea casos para:

- Prompt injection directa.
- Prompt injection dentro de una respuesta A2A.
- Intentos de modificar instrucciones del supervisor.
- Intentos de solicitar credenciales.
- Respuestas malformadas.
- Respuestas legítimas que mencionan ataques de forma educativa.
- Contenido excesivamente largo.
- Secretos en respuestas.

Documenta los límites de cobertura y los falsos positivos o falsos negativos relevantes.

---

# 5. Corrección 3 — Autenticación y autorización A2A

## Problema identificado

La variable `A2A_AGENTES_PERMITIDOS` controla qué grafos pueden incorporarse al catálogo, pero no autentica la identidad del servidor remoto.

Un agente con un identificador permitido no necesariamente es un agente confiable.

## Objetivo

Incorporar controles mínimos de autenticación y autorización adecuados para un prototipo académico.

No es necesario construir una infraestructura empresarial completa de identidad.

## Implementación requerida

### A. Identidad del agente

Diseña un mecanismo para vincular:

- Identificador lógico del agente.
- Endpoint autorizado.
- Identidad o credencial verificable.
- Capacidades permitidas.

No consideres el nombre del agente o su Agent Card como prueba suficiente de identidad.

### B. Autenticación

Evalúa la compatibilidad con el servidor A2A utilizado.

Si es técnicamente viable, implementa autenticación mediante un mecanismo estándar compatible con el stack, por ejemplo un token Bearer validado en el punto de entrada del servidor.

No basta con agregar un encabezado `Authorization` en el cliente: debe existir validación efectiva en el receptor.

No implementes un mecanismo de seguridad aparente que pueda ser omitido fácilmente.

### C. Autorización

Separa autenticación de autorización.

Un agente autenticado solamente debe poder ejecutar las acciones expresamente permitidas.

Considera controles sobre:

- Agente de destino.
- Grafo solicitado.
- Operación A2A.
- Capacidades autorizadas.

Aplica el principio de mínimo privilegio.

### D. Configuración segura

- Credenciales mediante variables de entorno.
- Nunca credenciales hardcodeadas.
- No registrar tokens completos.
- No incorporar secretos a las evidencias.
- Validar configuraciones incompletas.
- Mantener un modo de demostración local claramente identificado.

Si se requiere un proxy o middleware para validar identidad, documenta su función y sus limitaciones.

### E. Alcance realista

Si la autenticación completa no puede implementarse de manera segura sin modificar infraestructura fuera del repositorio, no simules que está resuelta.

En ese caso:

1. Implementa los controles verificables que sí sean posibles.
2. Prepara una configuración segura de referencia.
3. Documenta los componentes externos necesarios.
4. Registra explícitamente la limitación.
5. Evita presentar una allow-list como autenticación.

## Pruebas requeridas

- Agente autorizado.
- Agente no autorizado.
- Token ausente.
- Token inválido.
- Intento de invocar un grafo no permitido.
- Identidad válida con permisos insuficientes.
- Protección frente a exposición accidental de credenciales.

---

# 6. Corrección 4 — Robustez del cliente A2A

Archivo principal:

`src/coordinador/a2a.py`

## Problema identificado

El cliente convierte adecuadamente errores de red en `AgenteNoDisponible`, pero todavía pueden existir excepciones no controladas cuando el servidor devuelve estructuras JSON inesperadas.

Además, el `assistant_id` almacenado en caché puede quedar obsoleto cuando se reinicia o recarga el servidor LangGraph.

## Implementación requerida

### A. Validación de respuestas JSON

No supongas que una respuesta JSON válida tiene necesariamente la estructura esperada.

Valida explícitamente:

- Tipo raíz.
- Presencia de campos obligatorios.
- Tipos de campos.
- Listas vacías.
- Identificadores ausentes.
- Identificadores malformados.
- Resultados A2A incompletos.
- Errores JSON-RPC.

Evita excepciones accidentales como:

- `KeyError`
- `IndexError`
- `TypeError`
- `AttributeError`

Convierte los errores de protocolo en excepciones controladas y diferenciables de los errores de transporte cuando corresponda.

### B. Recuperación de assistant_id obsoleto

Diseña una estrategia de invalidación de caché.

Cuando el servidor indique que un `assistant_id` ya no existe:

1. Detectar el error correspondiente.
2. Invalidar únicamente la entrada afectada.
3. Volver a consultar `/assistants/search`.
4. Obtener el identificador actualizado.
5. Reintentar la operación una sola vez, cuando sea seguro hacerlo.

Evita bucles infinitos.

No reintentes automáticamente operaciones con posibles efectos secundarios cuando no puedas determinar si el servidor ya las ejecutó.

### C. Timeouts

Distingue:

- Timeout de conexión.
- Timeout de lectura.
- Error HTTP.
- Error de protocolo.
- Respuesta inválida.

Utiliza valores configurables y razonables.

### D. Manejo de errores

Define una jerarquía clara de excepciones, por ejemplo:

- `AgenteNoDisponible`
- `ErrorProtocoloA2A`
- `RespuestaA2AInvalida`
- `IdentificadorAsistenteObsoleto`

Adapta los nombres al estilo del proyecto.

El coordinador debe convertir estas excepciones en estados controlados, sin mostrar trazas internas al usuario.

### E. Pruebas

Usa mocks o `httpx.MockTransport` para simular:

- HTTP 200 con JSON inválido.
- HTTP 200 con JSON estructuralmente incorrecto.
- Lista de asistentes vacía.
- Ausencia de `assistant_id`.
- JSON-RPC con error.
- HTTP 404 para identificador obsoleto.
- Renovación correcta del identificador.
- Reintento exitoso.
- Reintento fallido.
- Timeout.
- Conexión rechazada.
- Respuesta A2A sin contenido esperado.

Las pruebas deben ser deterministas y no depender de servicios externos.

---

# 7. Corrección 5 — Consistencia documental y evidencias

Revisa toda la documentación del repositorio.

## Verificaciones obligatorias

### A. Identificación

- Confirmar integrantes del grupo.
- Detectar marcadores pendientes como `Grupo: NN`.
- No inventar un número de grupo desconocido.
- Confirmar que los blueprints reflejen su estado real.

### B. Coherencia técnica

Verifica que los documentos describan exactamente lo que hace el código.

En particular:

- Diferencia entre agente inexistente y desconectado.
- Alcance real de los guardrails.
- Autenticación versus allow-list.
- Recuperación de `assistant_id`.
- Comportamiento ante errores.
- Persistencia y limitaciones de memoria.

### C. Evidencias

Revisa:

- `evidencias/README.md`
- Evidencias de robustez.
- Evidencias de comunicación Mac/Windows.
- Diagramas.
- Rutas y nombres de archivos.
- Referencias cruzadas.

Corrige numeraciones y referencias inconsistentes.

No fabriques evidencias de ejecuciones que no ocurrieron.

Si alguna prueba necesita infraestructura remota que no está disponible, indícalo expresamente.

### D. Documento de entrega

Actualiza `entrega/documento-entrega.md`.

Conserva la estructura del taller y agrega las mejoras implementadas donde corresponda.

Explica brevemente:

- Problema original.
- Solución aplicada.
- Evidencia de funcionamiento.
- Limitaciones pendientes.

### E. Regeneración

Si el repositorio dispone de scripts para ello:

- Regenera el PDF.
- Actualiza la carpeta de entrega.
- Regenera el ZIP final.
- Comprueba que los artefactos correspondan al código y documentación actuales.

No incluyas `.env`, claves, cachés, archivos temporales ni datos sensibles en el paquete.

---

# 8. Criterios de aceptación

Considera el trabajo terminado solamente cuando:

1. El supervisor distinga correctamente entre un agente inexistente y uno desconectado.
2. Los agentes disponibles sigan funcionando si otro falla.
3. Los guardrails operen en entrada, salida y límites A2A.
4. Los controles no dependan exclusivamente de expresiones regulares.
5. La documentación no presente los guardrails como protección infalible.
6. La autenticación y autorización estén implementadas y probadas, o sus dependencias externas y limitaciones estén claramente identificadas.
7. Las respuestas JSON inesperadas no produzcan errores sin controlar.
8. El cliente pueda recuperarse de identificadores obsoletos en operaciones seguras.
9. Las pruebas anteriores sigan funcionando.
10. Las nuevas pruebas cubran los escenarios incorporados.
11. El documento de entrega y las evidencias estén sincronizados.
12. El paquete final no contenga secretos.

---

# 9. Validación final

Ejecuta:

```bash id="7s1byc"
uv run pytest -v
```

Adicionalmente:

- Ejecuta las verificaciones de estilo o calidad disponibles en el proyecto.
- Verifica que el grafo LangGraph compile.
- Comprueba que los imports funcionen.
- Inspecciona el diff.
- Revisa archivos nuevos y modificados.
- Comprueba que no se hayan incorporado credenciales.
- Ejecuta los scripts de documentación y empaquetado disponibles.

Si alguna validación falla, intenta corregirla y repite las pruebas.

No afirmes que algo fue probado si solamente fue inspeccionado.

---

# 10. Entregables esperados

Al terminar, presenta:

## A. Resumen ejecutivo

Explica qué problemas fueron corregidos y cuáles permanecen abiertos.

## B. Matriz de cambios

| Problema | Archivos modificados | Solución | Pruebas | Estado |
|---|---|---|---|---|

## C. Resultados de pruebas

Indica:

- Número de pruebas aprobadas.
- Número de pruebas fallidas.
- Número de pruebas omitidas.
- Comando ejecutado.
- Restricciones del entorno.

## D. Seguridad

Distingue expresamente:

- Controles implementados y verificados.
- Controles implementados pero no validados integralmente.
- Riesgos residuales.
- Mejoras futuras.

## E. Documentación

Indica qué documentos y evidencias fueron actualizados.

## F. Git

Muestra:

- Estado de la rama.
- Archivos modificados.
- Resumen del diff.

No hagas `push` ni modifiques el historial de Git sin autorización expresa.

---

# 11. Restricciones arquitectónicas

**No reemplaces la arquitectura actual.**

Mantén:

- LangGraph como motor de orquestación.
- Patrón Supervisor.
- A2A nativo.
- Descubrimiento mediante Agent Cards.
- Configuración por variables de entorno.
- Comunicación mediante Cloudflare para las demostraciones entre equipos.
- Compatibilidad con los agentes existentes.
- Trazabilidad de las rutas de ejecución.

No incorpores frameworks adicionales de orquestación.

Prioriza soluciones simples, comprobables y proporcionales al alcance académico.

**El propósito no es convertir el proyecto en un producto empresarial, sino demostrar una arquitectura multiagente correctamente diseñada, tolerante a fallos, con controles de seguridad explícitos y evidencia técnica reproducible.**

Comienza inspeccionando el repositorio y entrega un diagnóstico breve de los cinco problemas antes de modificar archivos. Luego implementa las correcciones, ejecuta las pruebas y prepara el resultado final.
