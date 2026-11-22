"""Prueba de extremo a extremo con urllib (sin librerías externas)."""
import argparse
import json
import urllib.request
import urllib.error

def get(url):
    with urllib.request.urlopen(url, timeout=15) as r:
        return r.status, json.load(r)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', default='http://127.0.0.1:8001')
    args = p.parse_args()
    base = args.url.rstrip('/')
    status, health = get(base+'/health')
    assert status == 200 and health['modelo_cargado'] is True, health
    status, meta = get(base+'/model-info')
    assert status == 200 and 'sklearn_version' in meta, meta
    status, example = get(base+'/albums?limit=1')
    assert status == 200 and example['items'], example
    album = example['items'][0]
    payload = json.dumps(album, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(base+'/predict', data=payload, method='POST', headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=30) as response:
        assert response.status == 200
        pred = json.load(response)
    assert pred['prediction'] in (0,1) and 0<=pred['probabilidad_favorito']<=1, pred
    print('Health OK:', health)
    print('Modelo:', meta.get('nombre_modelo'), 'sklearn:', meta['sklearn_version'])
    print('Predicción OK:', json.dumps(pred, indent=2, ensure_ascii=False))
if __name__ == '__main__':
    main()
