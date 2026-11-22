# Ejecutar desde la raíz de 08_cicd_rym_spotify (PowerShell).
param([string]$CarpetaPractica7 = "..\07_docker_rym_spotify")
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
$origen = [System.IO.Path]::GetFullPath((Join-Path $raiz $CarpetaPractica7))
$modelo = Join-Path $origen "models\champion.joblib"
$meta = Join-Path $origen "models\model_info.json"
if (-not (Test-Path -LiteralPath $modelo)) { throw "No se encuentra: $modelo" }
if (-not (Test-Path -LiteralPath $meta)) { throw "No se encuentra: $meta" }
$json = Get-Content -LiteralPath $meta -Raw -Encoding UTF8 | ConvertFrom-Json
$version = [string]$json.sklearn_version
if ($version -notmatch '^\d+\.\d+\.\d+$') { throw "sklearn_version inválida: $version" }
Copy-Item -LiteralPath $modelo -Destination (Join-Path $raiz "models\champion.joblib") -Force
Copy-Item -LiteralPath $meta -Destination (Join-Path $raiz "models\model_info.json") -Force
[System.IO.File]::WriteAllText((Join-Path $raiz ".env"), "SKLEARN_VERSION=$version`nAPP_PORT=8001`n", (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Modelo importado desde Práctica 7: $origen"
Write-Host "scikit-learn requerido: $version"
Write-Host "Verificar: py -3.11 scripts/model_version.py"
