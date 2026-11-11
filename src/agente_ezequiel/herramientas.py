# --8<-- encabezado-grupo
# Archivo: src/agente_ezequiel/herramientas.py
# Objetivo: Herramientas del agente de Ezequiel · IA Engineer & Data Scientist.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 1603
# Última modificación: 20261110 2349
# --8<-- fin-encabezado-grupo

"""Herramientas del agente de Ezequiel · IA Engineer & Data Scientist.

Datos simulados pero creíbles dentro del archivo (como en el molde de viajes): en
producción saldrían de un catálogo interno, un tracking de experimentos (MLflow,
Weights & Biases) o una tabla de benchmarks. Si preguntan algo que no está en los
datos, la herramienta lo dice en UNA línea; nunca lanza un error.
"""
from __future__ import annotations

import unicodedata

from langchain_core.tools import tool

from src.agente_ezequiel import bd_modelos


def _norm(texto: str) -> str:
    """minúsculas, sin acentos: para casar la entrada del usuario con las claves."""
    t = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


# ── catálogos simulados ──────────────────────────────────────────────────────
# problema de ML/DS  →  técnica recomendada + por qué (una línea cada uno)
TECNICAS: dict[str, dict] = {
    "pocos datos": {"tecnica": "transfer learning / fine-tuning de un modelo preentrenado, o few-shot con un LLM",
                    "por_que": "con pocos ejemplos, reutilizar representaciones ya aprendidas rinde más que entrenar desde cero"},
    "overfitting": {"tecnica": "regularización (L2/dropout), early stopping y validación cruzada",
                    "por_que": "limitan la capacidad efectiva del modelo y detectan cuándo deja de generalizar"},
    "desbalance de clases": {"tecnica": "class weights, resampleo (SMOTE/undersampling) y métricas tipo F1/PR-AUC",
                             "por_que": "la accuracy engaña con clases raras; hay que reponderar y medir sobre la minoritaria"},
    "datos faltantes": {"tecnica": "imputación (mediana/KNN/iterative) o modelos que manejan NaN (gradient boosting)",
                        "por_que": "evita descartar filas y preserva señal; GBMs toleran faltantes nativamente"},
    "texto": {"tecnica": "embeddings + clasificador lineal para tareas simples; LLM con RAG para preguntas abiertas",
              "por_que": "los embeddings capturan semántica barata; RAG aporta contexto sin reentrenar"},
    "series de tiempo": {"tecnica": "features de lag/rolling + gradient boosting, o modelos temporales (Prophet, N-BEATS)",
                        "por_que": "la dependencia temporal exige validación por ventanas y features que miren el pasado"},
    "deteccion de anomalias": {"tecnica": "Isolation Forest o autoencoders, con umbral sobre el error de reconstrucción",
                              "por_que": "aprenden lo 'normal' sin etiquetas y marcan lo que se aleja"},
    "alta dimensionalidad": {"tecnica": "reducción (PCA/UMAP) o selección de features por importancia",
                           "por_que": "menos ruido y cómputo, y modelos que generalizan mejor"},
}

# tipo de problema  →  métricas a mirar
METRICAS: dict[str, list[str]] = {
    "clasificacion": ["accuracy", "F1 (macro y por clase)", "matriz de confusión", "ROC-AUC"],
    "clasificacion desbalanceada": ["F1 de la clase minoritaria", "PR-AUC", "recall@precision fija"],
    "regresion": ["MAE", "RMSE", "R²", "MAPE (si no hay ceros)"],
    "ranking": ["NDCG@k", "MRR", "MAP"],
    "clustering": ["silhouette", "Davies-Bouldin", "inspección cualitativa de clusters"],
    "generacion de texto": ["evaluación humana", "LLM-as-judge con rúbrica", "groundedness/fidelidad en RAG"],
    "deteccion de anomalias": ["precision@k", "recall sobre anomalías conocidas", "alertas por falso positivo"],
}

# caso de uso por tipo de dato  →  modelo/enfoque de arranque
MODELOS: dict[str, dict] = {
    "tabular": {"modelo": "gradient boosting (XGBoost/LightGBM/CatBoost)",
                "nota": "baseline fuerte en datos tabulares; rápido de iterar antes de probar deep learning"},
    "texto": {"modelo": "embeddings (sentence-transformers) + clasificador, o un LLM para tareas generativas/abiertas",
              "nota": "empieza por embeddings; sube a LLM solo si la tarea lo pide"},
    "imagen": {"modelo": "CNN preentrenada (ResNet/EfficientNet) o un ViT con fine-tuning",
               "nota": "transfer learning casi siempre gana a entrenar desde cero"},
    "series temporales": {"modelo": "gradient boosting con features de lag, o Prophet/N-BEATS si hay estacionalidad marcada",
                        "nota": "valida por ventanas temporales, nunca con shuffle aleatorio"},
    "generacion": {"modelo": "LLM (Gemini/GPT/Claude) con prompt + RAG; fine-tuning solo si el prompt no alcanza",
                  "nota": "prompt y RAG primero; fine-tuning es el último recurso por costo"},
    "recomendacion": {"modelo": "filtrado colaborativo (ALS) o two-tower con embeddings",
                     "nota": "arranca con popularidad/colaborativo como baseline"},
}


def _buscar(catalogo: dict, consulta: str) -> str | None:
    """Devuelve la clave del catálogo cuyo texto aparece en la consulta (o None)."""
    q = _norm(consulta)
    for clave in catalogo:
        if _norm(clave) in q or q in _norm(clave):
            return clave
    # match por palabra suelta exacta
    palabras = set(q.split())
    for clave in catalogo:
        if palabras & set(_norm(clave).split()):
            return clave
    # match por raíz: comparten prefijo de >=5 letras (p. ej. "clasificar" ↔ "clasificacion")
    for clave in catalogo:
        for kw in _norm(clave).split():
            for qw in palabras:
                if len(kw) >= 5 and len(qw) >= 5 and kw[:5] == qw[:5]:
                    return clave
    return None


@tool
def recomendar_tecnica(problema: str) -> dict:
    """Recomienda una técnica de ML/Data Science para un problema dado y explica por qué.
    Ejemplos de problema: 'pocos datos', 'overfitting', 'desbalance de clases', 'datos faltantes',
    'texto', 'series de tiempo', 'detección de anomalías', 'alta dimensionalidad'.
    Devuelve {problema, tecnica, por_que}. Si no reconoce el problema, lo dice en una línea."""
    clave = _buscar(TECNICAS, problema)
    if not clave:
        return {"nota": f"No tengo una técnica catalogada para «{problema}». Puedo ayudar con: {', '.join(TECNICAS)}."}
    return {"problema": clave, **TECNICAS[clave]}


@tool
def metricas_recomendadas(tipo_problema: str) -> dict:
    """Dice qué métricas usar según el tipo de problema de ML.
    Tipos: 'clasificacion', 'clasificacion desbalanceada', 'regresion', 'ranking', 'clustering',
    'generacion de texto', 'deteccion de anomalias'.
    Devuelve {tipo, metricas:[...]}. Si no reconoce el tipo, lo dice en una línea."""
    clave = _buscar(METRICAS, tipo_problema)
    if not clave:
        return {"nota": f"No tengo métricas catalogadas para «{tipo_problema}». Tipos que manejo: {', '.join(METRICAS)}."}
    return {"tipo": clave, "metricas": METRICAS[clave]}


@tool
def elegir_modelo(tipo_de_dato: str) -> dict:
    """Sugiere un modelo/enfoque de arranque según el tipo de dato o caso de uso.
    Tipos: 'tabular', 'texto', 'imagen', 'series temporales', 'generacion', 'recomendacion'.
    Devuelve {tipo, modelo, nota}. Si no reconoce el tipo, lo dice en una línea."""
    clave = _buscar(MODELOS, tipo_de_dato)
    if not clave:
        return {"nota": f"No tengo un modelo catalogado para «{tipo_de_dato}». Tipos que manejo: {', '.join(MODELOS)}."}
    return {"tipo": clave, **MODELOS[clave]}


@tool
def consultar_modelos(consulta: str = "", tipo: str = "") -> list[dict]:
    """Consulta el catálogo de modelos de ciencia de datos en la base SQLite.
    `tipo` opcional: 'supervisado', 'no supervisado' o 'refuerzo'. `consulta` busca por
    nombre, para qué sirve, cómo se usa o librerías (p. ej. 'clustering', 'xgboost', 'RL').
    Devuelve, por modelo: nombre, tipo, para_que, como_se_utiliza, librerias y ejemplo_python.
    Si no hay coincidencias, devuelve una lista vacía."""
    return bd_modelos.consultar(consulta=consulta, tipo=tipo)


HERRAMIENTAS = [recomendar_tecnica, metricas_recomendadas, elegir_modelo, consultar_modelos]
