# --8<-- encabezado-grupo
# Archivo: src/agente_ezequiel/bd_modelos.py
# Objetivo: Base de conocimiento (SQLite) de modelos de ciencia de datos.
# Grupo del curso: Fabio Durán - Gustavo Reyes - Ezequiel Muñoz
# Creación: 20261110 2009
# Última modificación: 20261110 2340
# --8<-- fin-encabezado-grupo

"""Base de conocimiento (SQLite) de modelos de ciencia de datos.

Tabla `modelos` con columnas: nombre, tipo (supervisado / no supervisado / refuerzo),
para_que, como_se_utiliza, librerias, ejemplo_python. La BD se crea y puebla sola la
primera vez (desde la lista MODELOS de este archivo); así el agente funciona sin pasos
extra. Ruta por defecto: `data/modelos_ds.sqlite` (configurable con `BD_MODELOS`).
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
BD_PATH = Path(os.environ.get("BD_MODELOS", RAIZ / "data" / "modelos_ds.sqlite"))

# (nombre, tipo, para_que, como_se_utiliza, librerias, ejemplo_python)
MODELOS: list[tuple[str, str, str, str, str, str]] = [
    # ── Supervisados ──────────────────────────────────────────────────────────
    ("Regresión lineal", "supervisado",
     "Predecir un valor numérico a partir de variables explicativas.",
     "Ajustas una recta/plano por mínimos cuadrados; sirve de baseline en regresión.",
     "scikit-learn, numpy",
     "from sklearn.linear_model import LinearRegression\nm = LinearRegression().fit(X, y)\nm.predict(X_new)"),
    ("Regresión logística", "supervisado",
     "Clasificación binaria/multiclase con probabilidades.",
     "Modela la probabilidad con la función logística; baseline de clasificación.",
     "scikit-learn",
     "from sklearn.linear_model import LogisticRegression\nm = LogisticRegression(max_iter=1000).fit(X, y)\nm.predict_proba(X_new)"),
    ("Árbol de decisión", "supervisado",
     "Clasificar o regredir con reglas if-then interpretables.",
     "Divide el espacio por umbrales; fácil de leer, tiende a sobreajustar solo.",
     "scikit-learn",
     "from sklearn.tree import DecisionTreeClassifier\nm = DecisionTreeClassifier(max_depth=4).fit(X, y)"),
    ("Random Forest", "supervisado",
     "Clasificación/regresión robusta con bagging de árboles.",
     "Promedia muchos árboles sobre muestras bootstrap; baja varianza, poco tuning.",
     "scikit-learn",
     "from sklearn.ensemble import RandomForestClassifier\nm = RandomForestClassifier(n_estimators=300).fit(X, y)"),
    ("Gradient Boosting (XGBoost)", "supervisado",
     "Baseline fuerte en datos tabulares.",
     "Árboles secuenciales que corrigen el error del anterior; cuida el overfitting.",
     "xgboost, scikit-learn",
     "from xgboost import XGBClassifier\nm = XGBClassifier(n_estimators=400, learning_rate=0.05).fit(X, y)"),
    ("SVM", "supervisado",
     "Clasificación con márgenes; útil en alta dimensión.",
     "Busca el hiperplano de máximo margen; con kernels captura no linealidad.",
     "scikit-learn",
     "from sklearn.svm import SVC\nm = SVC(kernel='rbf', C=1.0).fit(X, y)"),
    ("KNN", "supervisado",
     "Clasificar/regredir por cercanía a los k vecinos.",
     "Guarda los datos y vota por los k más cercanos; sensible a la escala.",
     "scikit-learn",
     "from sklearn.neighbors import KNeighborsClassifier\nm = KNeighborsClassifier(n_neighbors=5).fit(X, y)"),
    ("Naive Bayes", "supervisado",
     "Clasificación rápida, típica en texto.",
     "Aplica Bayes asumiendo independencia entre features; muy buen baseline en NLP.",
     "scikit-learn",
     "from sklearn.naive_bayes import MultinomialNB\nm = MultinomialNB().fit(X, y)"),
    ("Red neuronal (MLP)", "supervisado",
     "Aprender relaciones no lineales complejas.",
     "Capas densas con activaciones; necesita más datos y tuning que los tabulares.",
     "pytorch, tensorflow, scikit-learn",
     "from sklearn.neural_network import MLPClassifier\nm = MLPClassifier(hidden_layer_sizes=(64,32)).fit(X, y)"),
    # ── No supervisados ───────────────────────────────────────────────────────
    ("K-Means", "no supervisado",
     "Agrupar datos en k clusters.",
     "Minimiza la distancia a los centroides; elige k con el codo o silhouette.",
     "scikit-learn",
     "from sklearn.cluster import KMeans\nlabels = KMeans(n_clusters=3, n_init='auto').fit_predict(X)"),
    ("DBSCAN", "no supervisado",
     "Clusters de forma arbitraria y detección de ruido.",
     "Agrupa por densidad (eps, min_samples); no necesita fijar k.",
     "scikit-learn",
     "from sklearn.cluster import DBSCAN\nlabels = DBSCAN(eps=0.5, min_samples=5).fit_predict(X)"),
    ("PCA", "no supervisado",
     "Reducir dimensionalidad conservando varianza.",
     "Proyecta a componentes ortogonales; útil antes de modelar o para visualizar.",
     "scikit-learn",
     "from sklearn.decomposition import PCA\nXr = PCA(n_components=2).fit_transform(X)"),
    ("t-SNE / UMAP", "no supervisado",
     "Visualizar datos de alta dimensión en 2D.",
     "Preservan vecindades locales; para explorar, no para features de producción.",
     "umap-learn, scikit-learn",
     "import umap\nXr = umap.UMAP(n_components=2).fit_transform(X)"),
    ("Clustering jerárquico", "no supervisado",
     "Agrupar con un dendrograma (sin fijar k a priori).",
     "Une/parte clusters por distancia; cortas el dendrograma al nivel deseado.",
     "scipy, scikit-learn",
     "from sklearn.cluster import AgglomerativeClustering\nlabels = AgglomerativeClustering(n_clusters=3).fit_predict(X)"),
    ("Isolation Forest", "no supervisado",
     "Detección de anomalías sin etiquetas.",
     "Aísla puntos raros con árboles aleatorios; marca outliers por score.",
     "scikit-learn",
     "from sklearn.ensemble import IsolationForest\nout = IsolationForest(contamination=0.05).fit_predict(X)"),
    ("Autoencoder", "no supervisado",
     "Comprimir/representar datos y detectar anomalías.",
     "Red que reconstruye su entrada; el error de reconstrucción señala lo anómalo.",
     "pytorch, tensorflow",
     "# encoder/decoder densos; entrena a reconstruir X y mide el error"),
    # ── Reinforcement Learning ────────────────────────────────────────────────
    ("Q-Learning", "refuerzo",
     "Aprender una política óptima en entornos discretos.",
     "Actualiza una tabla Q(s,a) con la ecuación de Bellman; off-policy.",
     "numpy, gymnasium",
     "Q[s,a] += alpha * (r + gamma * Q[s2].max() - Q[s,a])"),
    ("SARSA", "refuerzo",
     "Control on-policy en entornos discretos.",
     "Como Q-Learning pero actualiza con la acción realmente tomada (on-policy).",
     "numpy, gymnasium",
     "Q[s,a] += alpha * (r + gamma * Q[s2,a2] - Q[s,a])"),
    ("DQN", "refuerzo",
     "RL con estados de alta dimensión (p. ej. imágenes).",
     "Aproxima Q con una red + replay buffer y target network.",
     "stable-baselines3, gymnasium, pytorch",
     "from stable_baselines3 import DQN\nm = DQN('MlpPolicy', env).learn(100000)"),
    ("PPO", "refuerzo",
     "Policy gradient estable para control continuo/discreto.",
     "Optimiza la política con un clip que evita pasos demasiado grandes.",
     "stable-baselines3, gymnasium",
     "from stable_baselines3 import PPO\nm = PPO('MlpPolicy', env).learn(100000)"),
    ("A2C", "refuerzo",
     "Actor-Critic sincrónico, baseline de policy gradient.",
     "Un actor propone acciones y un crítico estima el valor para reducir varianza.",
     "stable-baselines3, gymnasium",
     "from stable_baselines3 import A2C\nm = A2C('MlpPolicy', env).learn(100000)"),
]

COLUMNAS = ["nombre", "tipo", "para_que", "como_se_utiliza", "librerias", "ejemplo_python"]


def _conectar() -> sqlite3.Connection:
    """Objetivo: abrir la conexión SQLite con filas tipo dict.
    Entradas: ninguna. Salida: sqlite3.Connection."""
    con = sqlite3.connect(BD_PATH)
    con.row_factory = sqlite3.Row
    return con


def asegurar_bd(forzar: bool = False) -> Path:
    """Crea y puebla la BD si no existe (o si `forzar`). Devuelve la ruta."""
    BD_PATH.parent.mkdir(parents=True, exist_ok=True)
    existe = BD_PATH.exists()
    con = _conectar()
    try:
        if forzar:
            con.execute("DROP TABLE IF EXISTS modelos")
        con.execute(
            "CREATE TABLE IF NOT EXISTS modelos ("
            "nombre TEXT, tipo TEXT, para_que TEXT, como_se_utiliza TEXT, librerias TEXT, ejemplo_python TEXT)"
        )
        hay = con.execute("SELECT COUNT(*) FROM modelos").fetchone()[0]
        if forzar or hay == 0:
            con.execute("DELETE FROM modelos")
            con.executemany(
                "INSERT INTO modelos (nombre, tipo, para_que, como_se_utiliza, librerias, ejemplo_python) "
                "VALUES (?,?,?,?,?,?)",
                MODELOS,
            )
            con.commit()
    finally:
        con.close()
    _ = existe
    return BD_PATH


def consultar(consulta: str = "", tipo: str = "", limite: int = 5) -> list[dict]:
    """Busca modelos por texto (nombre/para_qué/librerías) y/o tipo. Devuelve filas."""
    asegurar_bd()
    where, params = [], []
    if consulta.strip():
        like = f"%{consulta.strip()}%"
        where.append("(nombre LIKE ? OR para_que LIKE ? OR como_se_utiliza LIKE ? OR librerias LIKE ?)")
        params += [like, like, like, like]
    if tipo.strip():
        where.append("tipo LIKE ?")
        params.append(f"%{tipo.strip()}%")
    sql = "SELECT " + ", ".join(COLUMNAS) + " FROM modelos"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " LIMIT ?"
    params.append(int(limite))
    con = _conectar()
    try:
        return [dict(r) for r in con.execute(sql, params).fetchall()]
    finally:
        con.close()
