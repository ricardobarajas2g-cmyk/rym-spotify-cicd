import json
import importlib.metadata
from pathlib import Path
from scripts.model_version import get_version

ROOT = Path(__file__).resolve().parents[1]

def test_version_del_champion_coincide_con_el_entorno():
    assert importlib.metadata.version("scikit-learn") == get_version(), (
        "Instalar la versión indicada por models/model_info.json antes de ejecutar pruebas"
    )

def test_artifactos_que_van_al_contenedor():
    assert (ROOT / "models" / "champion.joblib").stat().st_size > 1000
    rows=json.loads((ROOT / "data" / "albumes_ejemplo.json").read_text(encoding='utf-8'))
    assert rows
    assert "promedio_energy" in rows[0] and "generos_frecuentes" in rows[0]
