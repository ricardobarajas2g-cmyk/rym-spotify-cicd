"""Reconstruye artefacto local del modelo logistic de la Práctica 4."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import joblib
import sklearn
from sklearn.model_selection import train_test_split
from src.prepare_data import load_data
from src.models import make_pipeline
from src.config import DATA_PATH, SEED

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--all-data',action='store_true',help='Opcional: entrenar con todas las filas etiquetadas; cambia modelo respecto a práctica 4')
    args=parser.parse_args()
    X,y,_=load_data()
    if args.all_data:
        X_train,y_train=X,y
        procedencia='entrenado con 611 datos etiquetados (demo; sin holdout)'
    else:
        X_train,_,y_train,_=train_test_split(X,y,test_size=.2,random_state=SEED,stratify=y)
        procedencia='replica local entrenamiento 80% de Práctica 4, seed 42'
    model=make_pipeline('logistic')
    model.fit(X_train,y_train)
    output=ROOT/'models'/'champion.joblib'
    output.parent.mkdir(parents=True,exist_ok=True)
    joblib.dump(model,output)
    info={"nombre_modelo":"logistic", "tipo":"réplica local", "fuente":"rym_spotify_con_generos.csv",
          "procedencia":procedencia,"filas_entrenamiento":len(X_train), "sha256_dataset":hashlib.sha256(DATA_PATH.read_bytes()).hexdigest(),
          "sklearn_version":sklearn.__version__, "fecha_preparacion_utc":datetime.now(timezone.utc).isoformat(),
          "nota":"El artefacto incluido es una réplica entrenada localmente, no el registro MLflow remoto."}
    (ROOT/'models'/'model_info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Modelo guardado:',output,'| filas:',len(X_train),'| sklearn:',sklearn.__version__)

if __name__=='__main__':
    main()
