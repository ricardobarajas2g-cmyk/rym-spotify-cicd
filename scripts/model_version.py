"""Versión de sklearn declarada en los metadatos del modelo."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def get_version():
    info = json.loads((ROOT / "models" / "model_info.json").read_text(encoding="utf-8"))
    version = str(info.get("sklearn_version", "")).strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:rc\d+)?", version):
        raise SystemExit("Falta sklearn_version válida en models/model_info.json")
    if not (ROOT / "models" / "champion.joblib").is_file():
        raise SystemExit("Falta models/champion.joblib")
    return version

if __name__ == "__main__":
    print(get_version())
