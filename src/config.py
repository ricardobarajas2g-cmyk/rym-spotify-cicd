"""Configuración central para la práctica MLflow."""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "rym_spotify_con_generos.csv"
OUT_DIR = ROOT / "resultados"
EXPERIMENT = "RYM_Spotify_Favoritos"
REGISTRY_MODEL = "RYMSpotifyClasificadorFavoritos"
TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
TARGET = "favorito_9_10"
GENRE_COL = "generos_frecuentes"
NUMERIC_COLUMNS = [
    "promedio_danceability", "promedio_energy", "promedio_acousticness",
    "promedio_instrumentalness", "promedio_valence", "promedio_tempo",
    "promedio_popularity", "promedio_loudness", "anio_spotify",
]
FEATURE_COLUMNS = NUMERIC_COLUMNS + [GENRE_COL]
SEED = 42
