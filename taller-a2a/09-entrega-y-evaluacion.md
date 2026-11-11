<!--encabezado-grupo-->
> **Archivo:** `taller-a2a/09-entrega-y-evaluacion.md`  
> **Objetivo:** Entrega y evaluación  
> **Grupo del curso:** Fabio Durán - Gustavo Reyes - Ezequiel Muñoz  
> **Creación:** 20261110 1450 · **Última modificación:** 20261110 2259
<!--/encabezado-grupo-->

<!-- clase: Taller · tu skill es un agente y habla por A2A · 61408ca1 | sección: sf8f5c9 | slide 9/10 · Parte 3 · Hablar entre agentes -->

Parte 3 · Hablar entre agentes · Paso 9 · entrega

# Entrega y evaluación

Un solo zip por grupo. Dentro va el proyecto completo de la clase con los agentes del grupo agregados, las evidencias de cada paso y un documento. Si falta el código o el documento, no se puede evaluar.

**estructura del zip de entrega**

```
grupo-N-taller-a2a.zip
├── documento-entrega.pdf     integrantes, grupo, blueprints, evidencias, ronda
├── blueprint-NOMBRE.md       uno por integrante
├── compañeros.md             nombre, skill, URL y ficha JSON de cada agente ajeno
├── proyecto/                 el proyecto COMPLETO de la clase + sus agentes
│   ├── AGENTS.md · main.py · requirements.txt · .env.example · README.md
│   ├── src/comun/ · src/agente_viajes/ · src/agente_restaurantes/
│   ├── src/coordinador/      con URLS_AGENTES en .env.example (vacío)
│   ├── src/agente_NOMBRE/    tools.py · prompts.py · graph.py · server.py
│   └── scripts/              tunel.sh · tunel.ps1 · probar_supervisor.py
└── evidencias/
    ├── 01-saltos.png         --saltos: usa tu herramienta y rechaza otro tema
    ├── 02-ficha.json         tu ficha final, descargada con curl
    ├── 03-tunel.png          cloudflared con la URL + la ficha vista desde fuera
    ├── 04-catalogo.png       "Supervisor con N agentes" con los compañeros
    └── 05-ronda.png          las tres preguntas de la ronda con --saltos

NUNCA va: .venv/ · .venv-crew/ · .env · __pycache__/   (sí va .env.example, sin claves)
```

## Lo que acaban de hacer, en términos del curso

| Concepto | Dónde lo vieron |
| --- | --- |
| Un agente = prompt + herramientas + ficha | Cuatro archivos convirtieron el molde de viajes en tu agente. El servidor y el protocolo no cambiaron. |
| La ficha es lo que otros leen de ti | El prompt 2: descripción con “sé” y “no hago”. El supervisor eligió solo con eso. |
| A2A entre computadores | Tu túnel en `URL_PUBLICA`, los de los demás en `URLS_AGENTES`. Mismo `message/send` que el curl local. |
| Supervisor = catálogo + decisión | No cambió una línea: solo creció la lista que lee al arrancar. |
| Lo que devuelve otro agente es un dato | Tu coordinador imprime “[Agente de Ana] …”; no obedece lo que dice. |

## Cómo se evalúa

| Criterio | Qué se mira | Puntos |
| --- | --- | --- |
| Blueprint | Una tabla por integrante, con “hace”, “no hace” y la herramienta descritos en concreto. | 10 |
| El agente funciona | El código corre desde el zip con `python main.py NOMBRE "…" --saltos`; llama a su herramienta y rechaza otros temas. | 25 |
| La ficha | Descripción con qué sí y qué no, skills con ejemplo; coincide con el blueprint. | 15 |
| Túnel y catálogo | Evidencia de la ficha vista desde fuera y del coordinador con agentes de otros computadores. | 20 |
| La ronda | Las tres preguntas por integrante con su camino en `--saltos`, y el análisis de qué fichas funcionaron. | 20 |
| Entrega limpia | Estructura del zip, identificación completa, `compañeros.md`, README con cómo correrlo. Sin `.env` ni `.venv`. | 10 |

Antes de subir el zip

1. **Identificación obligatoria:** nombres y apellidos completos de los integrantes y el número del grupo, en el documento y en el README. Para los agentes ajenos que usaron, el nombre de su autor.

2. **Pruébenlo desde el zip:** descompriman en otra carpeta, creen el entorno, copien `.env.example` a `.env` con su clave y corran `--saltos`. Si a ustedes no les corre, a nosotros tampoco.

3. **Ctrl+C** en los túneles al terminar: mientras estén abiertos, cualquiera con la URL gasta su clave.
