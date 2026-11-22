# Notas docentes — Práctica 8 RYM + Spotify

- Se adapta la misma aplicación y los endpoints de Práctica 7. No hay entrenamiento de modelos en CI, solo inferencia.
- Modelo incluido: réplica local Regresión Logística sklearn 1.8.0; el script importa el Champion real desde Práctica 7 si el estudiante ya lo configuró, en cuyo caso es 1.9.1 según las ejecuciones previas del estudiante.
- **No presentar la réplica como el modelo exportado por MLflow**.
- GitHub workflow: job `tests` corre pytest y comprueba versión de sklearn. Job `image` depende de `tests`, construye imagen y hace smoke-test. Job `publish` depende de `image` y publica GHCR solo desde main, tras superar todas las comprobaciones.
- Si alguien publica un repo público, `data/*.csv` está ignorado por defecto. `albumes_ejemplo.json` y el modelo sí se publican como parte del proyecto; revisar privacidad en clase.
- La prueba fallida intencional muestra la función de CI sin necesitar modificar algoritmos ni el modelo.
- El ejemplo usa componentes Python y GitHub Actions propios de 2026; las versiones de acciones están declaradas en `.github/workflows/cicd.yml`.
- Para comprobar que el runner publicó el mismo modelo, comparar `/model-info` del contenedor local y el publicado en GHCR.
- Trabajo local validado por pytest y parseo YAML. La ejecución remota en GitHub y la construcción Docker deben realizarse con cuenta/servicio reales.
