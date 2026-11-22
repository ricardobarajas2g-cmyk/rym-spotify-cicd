"""Carga, valida y prepara el CSV sin filtrar información del test."""
import hashlib
import json
import pandas as pd
from src.config import DATA_PATH, OUT_DIR, FEATURE_COLUMNS, GENRE_COL, NUMERIC_COLUMNS, TARGET


def dataset_hash(path=DATA_PATH):
    """Identificador SHA-256 reproducible del CSV original."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_data(path=DATA_PATH):
    """Devuelve X, y, metadatos. El escalado y géneros se ajustan en el pipeline."""
    path = path if hasattr(path, "read_bytes") else __import__("pathlib").Path(path)
    df = pd.read_csv(path)
    required = set(FEATURE_COLUMNS + [TARGET, "rating_rym", "artista_rym", "album_rym"])
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"Faltan columnas en el CSV: {missing}")
    df = df.copy()
    # Excluir álbumes no puntuados (7 en este CSV).
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
    df["rating_rym"] = pd.to_numeric(df["rating_rym"], errors="coerce")
    df = df[df[TARGET].isin([0, 1]) & df["rating_rym"].between(1, 10)].copy()
    inferred_target = (df["rating_rym"] >= 9).astype(int)
    if not (df[TARGET].astype(int).to_numpy() == inferred_target.to_numpy()).all():
        raise ValueError("La variable favorito_9_10 no coincide con rating_rym>=9")
    for c in NUMERIC_COLUMNS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # Preparación textual fija; CountVectorizer aprenderá sus géneros SOLO con training.
    df[GENRE_COL] = (df[GENRE_COL].fillna("").astype(str)
                     .str.lower().str.strip()
                     .str.replace(r"\s*\|\s*", "|", regex=True)
                     .str.replace(r"\s+", " ", regex=True))
    df[GENRE_COL] = df[GENRE_COL].replace("", "desconocido")
    X = df[FEATURE_COLUMNS].copy()
    y = inferred_target.astype(int)
    meta = df[["artista_rym", "album_rym", "rating_rym"]].copy()
    if y.nunique() < 2:
        raise ValueError("Se necesitan ambas clases de la variable objetivo")
    return X, y, meta


def main():
    X, y, meta = load_data()
    OUT_DIR.mkdir(exist_ok=True)
    result = pd.concat([meta.reset_index(drop=True), X.reset_index(drop=True), y.rename(TARGET).reset_index(drop=True)], axis=1)
    result.to_csv(OUT_DIR / "albumes_etiquetados.csv", index=False, encoding="utf-8-sig")
    stats = {"filas_csv_original": len(pd.read_csv(DATA_PATH)), "filas_etiquetadas": len(y),
             "favoritos": int(y.sum()), "no_favoritos": int((y == 0).sum()),
             "columnas_entrada": FEATURE_COLUMNS, "sha256_csv": dataset_hash()}
    (OUT_DIR / "resumen_datos.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print("Archivo generado:", OUT_DIR / "albumes_etiquetados.csv")


if __name__ == "__main__":
    main()
