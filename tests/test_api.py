import json
from fastapi.testclient import TestClient
from app import main as api

client=TestClient(api.app)

def sample():
    return json.loads(api.EXAMPLES_FILE.read_text(encoding='utf-8'))[0]

def test_health():
    r=client.get('/health')
    assert r.status_code==200
    assert r.json()['modelo_cargado'] is True

def test_formulario_y_docs():
    assert 'Predicción de álbumes favoritos' in client.get('/').text
    assert client.get('/docs').status_code==200

def test_info():
    r=client.get('/model-info')
    assert r.status_code==200
    assert 'sklearn_version' in r.json()

def test_catalogo():
    r=client.get('/albums?limit=5')
    assert r.status_code==200
    assert len(r.json()['items'])==5

def test_prediccion_y_log(tmp_path,monkeypatch):
    target=tmp_path/'registros.jsonl'
    monkeypatch.setattr(api,'LOG_FILE',target)
    x=sample()
    r=client.post('/predict',json=x)
    assert r.status_code==200,r.text
    response=r.json()
    assert response['prediction'] in [0,1]
    assert 0<=response['probabilidad_favorito']<=1
    assert response['modelo']
    assert target.is_file()
    line=json.loads(target.read_text(encoding='utf-8').strip())
    assert line['request']['album']==x['album']
    assert line['response']['prediction']==response['prediction']

def test_rechaza_valor_invalido():
    x=sample()
    x['promedio_energy']=1.7
    assert client.post('/predict',json=x).status_code==422

def test_rechaza_faltante():
    x=sample()
    x.pop('promedio_tempo')
    assert client.post('/predict',json=x).status_code==422

def test_rechaza_columna_filtracion():
    x=sample()
    x['rating_rym']=10
    assert client.post('/predict',json=x).status_code==422
