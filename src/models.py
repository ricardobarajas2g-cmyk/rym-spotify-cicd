"""Pipelines completamente ajustables en cross-validation sin data leakage."""
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from src.config import GENRE_COL, NUMERIC_COLUMNS, SEED


def make_pipeline(model_name):
    """CountVectorizer trata cada género (separado por |) como etiqueta completa."""
    num = Pipeline([
        ("imputar", SimpleImputer(strategy="median")),
        ("escalar", StandardScaler()),
    ])
    prep = ColumnTransformer([
        ("numericas", num, NUMERIC_COLUMNS),
        ("generos", CountVectorizer(token_pattern=r"[^|]+", binary=True, lowercase=True, min_df=2), GENRE_COL),
    ], sparse_threshold=0.0)
    classifiers = {
        "logistic": LogisticRegression(C=1.0, max_iter=1500, random_state=SEED),
        "forest": RandomForestClassifier(n_estimators=160, max_depth=8, min_samples_leaf=2, random_state=SEED, n_jobs=-1),
        "svm": SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, random_state=SEED),
    }
    if model_name not in classifiers:
        raise ValueError(f"Modelo desconocido: {model_name}")
    return Pipeline([("preprocesamiento", prep), ("clasificador", classifiers[model_name])])


def model_params(name):
    model = make_pipeline(name).named_steps["clasificador"]
    if name == "logistic":
        return {"C": model.C, "max_iter": model.max_iter}
    if name == "forest":
        return {"n_estimators": model.n_estimators, "max_depth": model.max_depth,
                "min_samples_leaf": model.min_samples_leaf}
    return {"C": model.C, "gamma": model.gamma, "kernel": model.kernel,
            "probability": model.probability}
