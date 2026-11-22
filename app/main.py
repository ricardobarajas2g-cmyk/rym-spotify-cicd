"""FastAPI para inferencia de favoritos RYM. Entrenamiento separado de inferencia."""
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from app.schemas import AlbumInput, PredictionOutput
from src.config import FEATURE_COLUMNS, GENRE_COL

ROOT = Path(__file__).resolve().parents[1]
MODEL_FILE = Path(os.environ.get("MODEL_PATH", str(ROOT / "models" / "champion.joblib")))
LOG_FILE = Path(os.environ.get("PREDICTION_LOG", str(ROOT / "logs" / "predicciones.jsonl")))
EXAMPLES_FILE = ROOT / "data" / "albumes_ejemplo.json"
_lock = Lock()

# Precargar y comprobar el modelo al arrancar; si falta artefacto, mostrar error útil.
if not MODEL_FILE.is_file():
    raise RuntimeError(f"No se encuentra el modelo: {MODEL_FILE}. Ver README.md")
model = joblib.load(MODEL_FILE)  # Cargar solo modelos locales/de origen confiable
info_file = ROOT / "models" / "model_info.json"
model_info = json.loads(info_file.read_text(encoding="utf-8")) if info_file.exists() else {}

app = FastAPI(title="RYM + Spotify · Predicción de álbumes favoritos", version="1.0.0",
              description="Clasificación favorita (rating RYM 9–10) desde características Spotify")

@app.get("/health", tags=["Estado"])
def health():
    return {"status": "ok", "modelo_cargado": True}

@app.get("/model-info", tags=["Estado"])
def get_model_info():
    return model_info

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    return (ROOT / "templates" / "index.html").read_text(encoding="utf-8")

@app.get("/albums", tags=["Ejemplos"])
def albums(q: str = Query(default="", max_length=120), limit: int = Query(default=30, ge=1, le=40)):
    """Ejemplos precomputados para rellenar el formulario; no son recomendaciones."""
    examples = json.loads(EXAMPLES_FILE.read_text(encoding="utf-8"))
    term = q.casefold().strip()
    if term:
        examples = [row for row in examples if term in (row['artista']+' '+row['album']).casefold()]
    return {"total": len(examples), "items": examples[:limit]}

@app.post("/predict", response_model=PredictionOutput, tags=["Predicción"])
def predict(album: AlbumInput):
    entry = album.model_dump()
    entry[GENRE_COL] = "|".join(s.strip().lower() for s in entry[GENRE_COL].split("|") if s.strip())
    if not entry[GENRE_COL]:
        raise HTTPException(status_code=422, detail="Indicar al menos un género")
    X = pd.DataFrame([{k: entry[k] for k in FEATURE_COLUMNS}], columns=FEATURE_COLUMNS)
    prediction = int(model.predict(X)[0])
    proba = float(model.predict_proba(X)[0, 1])
    result = PredictionOutput(
        artista=entry['artista'], album=entry['album'], prediction=prediction,
        probabilidad_favorito=round(proba, 5),
        interpretacion='Favorito probable (9–10)' if prediction == 1 else 'No favorito probable (1–8)',
        modelo=model_info.get('nombre_modelo', 'logistic'),
    )
    # Registros únicamente para práctica local de monitoreo (sin autenticar ni publicar).
    event = {"id": str(uuid.uuid4()), "timestamp_utc": datetime.now(timezone.utc).isoformat(),
             "request": entry, "response": result.model_dump(), "modelo_archivo": MODEL_FILE.name}
    try:
        with _lock:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with LOG_FILE.open('a', encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
    except OSError:
        # En esta práctica un fallo del registro local no impide devolver una predicción.
        pass
    return result
