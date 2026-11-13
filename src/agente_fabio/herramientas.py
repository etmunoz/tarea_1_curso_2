from langchain_core.tools import tool

APUNTES = {
    "conceptos": (
        "1) Alineamiento de secuencias: comparar dos o más secuencias para encontrar regiones similares; "
        "BLAST busca alineamientos locales contra una base de datos y su e-value indica cuántos aciertos "
        "con ese puntaje se esperarían por azar (más cercano a 0, más confiable). "
        "2) Formatos FASTA y FASTQ: FASTA guarda la secuencia con una línea de encabezado '>'; FASTQ "
        "agrega la calidad de cada base (Phred) y es lo que entregan los secuenciadores. "
        "3) Accession de UniProt: identificador estable de una proteína (por ejemplo P04637 para TP53 "
        "humana); Swiss-Prot es la parte revisada por curadores y TrEMBL la anotada automáticamente."
    ),
    "criterios": (
        "Una buena solución bioinformática: (a) es reproducible: versiones de herramientas y de bases "
        "de datos registradas, mismos datos de entrada dan el mismo resultado; (b) parte con control de "
        "calidad de los datos (por ejemplo FastQC antes de alinear); (c) cita la fuente de cada dato "
        "(accession, URL, versión de la base); (d) elige la herramienta según el problema: sensibilidad "
        "cuando importa no perder homólogos lejanos, velocidad cuando el volumen es grande; (e) separa "
        "lo que dicen los datos de la interpretación."
    ),
    "caso": (
        "En el Curso 1 construí BioAgente, un agente ReAct con LangGraph y Gemini que responde sobre genes "
        "y proteínas consultando UniProt en vivo y sobre protocolos del laboratorio docente con RAG en Redis. "
        "Ante '¿Qué función tiene la proteína TP53 humana?' la respuesta correcta exige el accession P04637 "
        "y la URL de UniProt. Aprendí que los identificadores, longitudes y funciones deben venir de la "
        "herramienta y no de la memoria del modelo, que puede inventarlos o estar desactualizada, y que "
        "verificar con pruebas automáticas (asserts sobre el accession) da confianza en el agente."
    ),
}

@tool
def consultar_mis_apuntes(tema: str = "") -> str:
    """Consulta mis apuntes: conceptos, criterios o caso. Vacío devuelve todos."""
    clave = tema.lower().strip()
    if not clave:
        return "\n".join(f"{nombre}: {texto}" for nombre, texto in APUNTES.items())
    return APUNTES.get(clave, "No tengo ese tema registrado. Consulta conceptos, criterios o caso.")

HERRAMIENTAS = [consultar_mis_apuntes]
