# Práctica 8 — CI/CD con GitHub Actions | RYM + Spotify

Proyecto **independiente** basado en Práctica 7. Predice si un álbum recibirá una puntuación personal de **9–10** en RYM a partir de características acústicas y géneros de Spotify. Contiene FastAPI, formulario HTML, modelo guardado, pruebas pytest, Docker y workflow de GitHub Actions para GitHub Container Registry (GHCR).

> La imagen Docker incluye solamente modelo, aplicación y ejemplos de entrada. El dataset original (con puntuaciones personales) se entrega en el ZIP como material académico, pero **está excluido de Git y de la imagen Docker** (`data/*.csv`). El repositorio puede ser privado.

## Contenido principal

- `.github/workflows/cicd.yml`: CI en cada push / PR a main y ejecución manual. Publica una imagen en GHCR **solo desde main**, después de pruebas y comprobación del contenedor.
- `app/main.py` y `app/schemas.py`: endpoints `/`, `/health`, `/model-info`, `/albums`, `/predict`, con registro de solicitudes y respuestas en JSONL.
- `models/champion.joblib`: modelo de demostración incluido, entrenado con scikit-learn 1.8.0. **Puedes reemplazarlo por TU Champion real de Práctica 7.**
- `models/model_info.json`: procedencia y versión de scikit-learn del modelo, leída automáticamente durante CI/CD.
- `tests/test_api.py`, `tests/test_model_artifacts.py`: pruebas, incluida consistencia de versión.
- `Dockerfile`, `compose.yaml`: imagen y ejecución local en el puerto 8001.
- `data/albumes_ejemplo.json`: ejemplos para el formulario; `data/rym_spotify_con_generos.csv` es material local excluido del repositorio Git por defecto.
- `scripts/importar_champion_practica7.ps1`: importa el Champion de la Práctica 7, si ambas carpetas son hermanas.
- `scripts/probar_contenedor.py`: prueba HTTP de los endpoints tras ejecutar la imagen.
- `GUIA_ALUMNO.md`: secuencia de clase y evidencias.

## 1. Preparar Champion real (recomendado)

Descomprimir en la misma carpeta que `07_docker_rym_spotify`. Abrir `08_cicd_rym_spotify` en VS Code, terminal PowerShell:

```powershell
.\scripts\importar_champion_practica7.ps1
py -3.11 scripts/model_version.py
Get-Content .env
```

Deberá indicar **1.9.1** si tu Práctica 7 ya usaba el Champion real de MLflow. Si PowerShell impide ejecutar el script, copiar manualmente los archivos:

```powershell
Copy-Item ..\07_docker_rym_spotify\models\champion.joblib .\models\champion.joblib -Force
Copy-Item ..\07_docker_rym_spotify\models\model_info.json .\models\model_info.json -Force
```

Luego crear `.env` como copia de `.env.example` y actualizar `SKLEARN_VERSION` a la versión indicada en `models/model_info.json` (por ejemplo, 1.9.1). La instalación local y CI usarán la versión declarada en el archivo de metadatos.

## 2. Pruebas locales (Windows 11, PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-ci.txt
$version = & .\.venv\Scripts\python.exe scripts/model_version.py
.\.venv\Scripts\python.exe -m pip install "scikit-learn==$version"
.\.venv\Scripts\python.exe -m pytest -v
```

**La instalación de scikit-learn se realiza por separado** para coincidir con la versión del Champion; `requirements-ci.txt` (o `requirements.txt`) instala solamente el resto de dependencias.

Si estás usando un entorno virtual ya existente, basta con instalar las dependencias y verificar que `sklearn.__version__` coincida con `models/model_info.json`.

## 3. Prueba local con Docker

Con Docker Desktop iniciado, desde esta carpeta:

```powershell
docker compose up -d --build
# esperar estado healthy:
docker compose ps
py -3.11 scripts/probar_contenedor.py --url http://127.0.0.1:8001
```

Abrir http://localhost:8001/ y http://localhost:8001/docs. Los cambios en el modelo requieren reconstruir la imagen. Detener con `docker compose down` (sin `-v` para conservar registros).

Si el puerto 8001 está ocupado, modificar `APP_PORT` en `.env`.

## 4. Publicar en GitHub (sin desplegar servidores externos)

Crear un repositorio GitHub vacío llamado `rym-spotify-cicd` (puede ser privado; no agregar README inicial), y ejecutar:

```powershell
git init -b main
git add .
git status --short
git commit -m "Preparar CI CD para RYM Spotify"
git remote add origin https://github.com/TU_USUARIO/rym-spotify-cicd.git
git push -u origin main
```

**Antes de hacer push**, comprobar que `data/rym_spotify_con_generos.csv`, `.env`, `.venv` y `logs/*.jsonl` **no están en `git status --short`**. El modelo y su metadato deben estar incluidos. Si quieres mantener privados los nombres de artistas/álbumes de los ejemplos, usa repositorio privado; la imagen publicada en GHCR también puede requerir configurar visibilidad.

En GitHub > Actions se ejecutarán tres jobs:

1. `CI - pytest y API`: instala dependencias con versión de sklearn igual a la del modelo y ejecuta pytest.
2. `Docker - construir y probar`: construye imagen, inicia contenedor y comprueba `/health`, `/albums` y `/predict` sin necesidad de permisos de publicación.
3. `CD - publicar GHCR`: tras los dos trabajos exitosos, publica la imagen únicamente desde `main`.

El workflow usa `GITHUB_TOKEN` con `packages: write` para la publicación. En repositorios de organizaciones con restricciones de Actions o Packages, revisar los permisos del repositorio.

## 5. Provocar un error de pruebas (actividad guiada)

En `tests/test_api.py`, cambia temporalmente `assert r.status_code==200` de `test_health` por `assert r.status_code==404`, guarda y publica:

```powershell
git add tests/test_api.py
git commit -m "test: provocar fallo intencional"
git push origin main
```

Comprobar que `CI - pytest y API` falla y `Docker - construir y probar` y `CD - publicar GHCR` **no se ejecutan**, por sus dependencias. Corregir `404` a `200`, commit y push para comprobar recuperación. **En un proyecto real, conviene realizar esta actividad en una rama y Pull Request**, en lugar de insertar una prueba rota en main.

## 6. Descargar desde GHCR y ejecutar en Windows o Fedora

Después de una ejecución exitosa, abrir GitHub > Packages. La imagen se publica con dos tags:

- `ghcr.io/tu_usuario/rym-spotify-cicd:latest`
- `ghcr.io/tu_usuario/rym-spotify-cicd:<hash_commit>`

Sustituir el usuario/nombre según la URL real del repositorio. Si la imagen es privada, autenticarse en GHCR con un token con `read:packages`; **nunca incluir tokens en el repositorio**.

```powershell
docker pull ghcr.io/tu_usuario/rym-spotify-cicd:latest
docker run --rm -p 127.0.0.1:8002:8000 --name rym-ghcr ghcr.io/tu_usuario/rym-spotify-cicd:latest
```

Abrir `http://localhost:8002/docs` y efectuar una predicción. El mismo comando puede utilizarse desde Fedora (terminal Bash; sustituir cuenta y repositorio). Si un puerto está ocupado, elegir otro, por ejemplo 8003.

**El registro local** de FastAPI se escribe en `/app/logs/predicciones.jsonl` dentro del contenedor. Para conservarlo tras eliminarlo, utilizar un volumen: `-v rym_predicciones:/app/logs`. No enviar estos logs a GitHub.

## 7. Entregables

- Captura de `python -m pytest -v` exitoso.
- Captura del workflow correcto en GitHub Actions.
- Captura del workflow fallido y su corrección.
- Captura del paquete GHCR publicado y sus tags.
- Captura de `docker pull`, `docker run` y `/predict` desde la imagen publicada.
- Explicación breve: diferencia entre CI, Continuous Delivery y Continuous Deployment.

## Limitaciones / resolución de problemas

- La imagen de ejemplo incluida tiene un modelo de demostración con **scikit-learn 1.8.0**. Si quieres tu Champion real 1.9.1, importa ambos archivos de Práctica 7 antes de subir el repositorio.
- El estado `python -m pytest -v` permite verificar consistencia: si las versiones difieren, instalar sklearn igual a `model_info.json` y reconstruir la imagen.
- Sin `Docker Engine` local no puede verificarse el `docker build`; GitHub Actions ejecuta los trabajos Docker en un runner Linux.
- Evitar imprimir secretos o registrar datos privados en logs de CI.
- Esta práctica **automatiza pruebas y publicación de imagen**. El despliegue a Windows/Fedora es manual (Continuous Delivery).
- `joblib`/pickle pueden ejecutar código al deserializar: cargar solamente modelos confiables.
