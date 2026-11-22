# Imagen Linux replicable de FastAPI + clasificador RYM/Spotify.
FROM python:3.11-slim

ARG SKLEARN_VERSION=1.8.0
ARG SOURCE_REPO=""
LABEL org.opencontainers.image.title="RYM Spotify Clasificador Favoritos" \
      org.opencontainers.image.description="API FastAPI para clasificar álbumes favoritos" \
      org.opencontainers.image.source="${SOURCE_REPO}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MODEL_PATH=/app/models/champion.joblib \
    PREDICTION_LOG=/app/logs/predicciones.jsonl

WORKDIR /app
COPY requirements-container.txt ./
RUN python -m pip install --no-cache-dir -r requirements-container.txt "scikit-learn==${SKLEARN_VERSION}"
COPY app/ ./app/
COPY src/__init__.py src/config.py ./src/
COPY templates/ ./templates/
COPY models/champion.joblib models/model_info.json ./models/
COPY data/albumes_ejemplo.json ./data/
RUN useradd --uid 10001 --create-home appuser \
    && mkdir -p /app/logs \
    && chown -R appuser:appuser /app/logs
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
