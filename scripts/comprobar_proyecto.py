"""Verifica artefactos requeridos sin cargar modelos no confiables."""
import json
from pathlib import Path
from model_version import get_version
ROOT=Path(__file__).resolve().parents[1]
required=["app/main.py","app/schemas.py","models/champion.joblib", "models/model_info.json", "templates/index.html", "data/albumes_ejemplo.json", ".github/workflows/cicd.yml","Dockerfile", "requirements-ci.txt"]
missing=[f for f in required if not (ROOT/f).is_file()]
if missing: raise SystemExit("Faltan archivos: " + ", ".join(missing))
print(f"Archivos necesarios presentes. sklearn requerido: {get_version()}")
print("Datos musicales de ejemplo:", len(json.loads((ROOT/'data/albumes_ejemplo.json').read_text(encoding='utf-8'))))
