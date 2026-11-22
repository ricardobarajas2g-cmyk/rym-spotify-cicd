# Práctica 8: CI/CD con GitHub Actions (RYM + Spotify) — 120 minutos

**Objetivo:** automatizar pruebas y publicación de una imagen Docker de FastAPI que clasifica álbumes como favoritos en RYM (rating 9–10). Los datos, endpoints, modelo y pruebas iniciales ya están preparados. **El trabajo se concentra en CI/CD.**

## 0–15 min. Revisión del proyecto

- Leer `README.md`, `models/model_info.json` y `.github/workflows/cicd.yml`.
- Opcional: importar el Champion real de Práctica 7 usando `scripts/importar_champion_practica7.ps1`.
- Identificar `app/main.py`, `tests/test_api.py`, `Dockerfile`, `compose.yaml`.
- Explicar en una frase qué tarea cumple cada archivo.

## 15–35 min. Ejecutar las pruebas locales

Ejecutar los comandos de instalación en la sección 2 de README. Comprobar que `pytest` termina correctamente. Identificar los asserts para `/health` y `/predict`.

## 35–55 min. Subir a GitHub

Crear un repositorio vacío `rym-spotify-cicd`, inicializar `main`, realizar `git add`, `commit` y `push` como indica README. Revisar que **el CSV de puntuaciones personales, .env y logs no se suban**. Abrir la pestaña Actions y localizar los jobs `tests` y `image`.

## 55–80 min. Un CI fallido y uno exitoso

- Modificar temporalmente la prueba `test_health` para esperar `404` en vez de `200`.
- Commit y push; observar `tests` fallido. Los jobs `image` y `publish` no deben comenzar.
- Restaurar `200`, commit y push; observar ejecución exitosa.
- Abrir logs de ambos runs y comparar.

## 80–100 min. Construcción y publicación Docker

- Examinar el `Dockerfile`, identificando Python, instalación de dependencias y modelo.
- Comprobar que Actions ejecutó la prueba del contenedor (endpoints `/health`, `/albums`, `/predict`).
- Abrir GitHub Packages; identificar `latest` y el tag del SHA del commit.
- Explicar por qué `image` depende de `tests` y por qué en Pull Request solo se validan pruebas e imagen, sin publicar.

## 100–115 min. Descargar imagen en tu equipo

Con Docker Desktop en Windows (o Docker Engine en Fedora), ejecutar `docker pull` y `docker run` desde GHCR según README, usando un puerto libre (8002). Abrir `/docs` y realizar la predicción de un álbum. Si el paquete es privado, revisar acceso antes de hacer pull.

## 115–120 min. Entrega

Entregar URL del repositorio GitHub y PDF de evidencias: pruebas correctas, fallo intencional, corrección, publicación del paquete, ejecución de imagen, y breve explicación de CI/CD.

## Preguntas

1. ¿Qué condición debe cumplirse antes de publicar una imagen?
2. ¿Por qué es importante guardar `model_info.json` junto con el modelo?
3. ¿Se publica la imagen en los Pull Requests? ¿Por qué?
4. ¿Qué diferencia existe entre ejecutar el Dockerfile localmente y descargar la imagen de GHCR?
5. ¿Qué datos se excluyen del repositorio y por qué?
