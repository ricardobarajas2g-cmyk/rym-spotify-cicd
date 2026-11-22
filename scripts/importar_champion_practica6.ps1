# Copia el Champion (y sus metadatos) desde una Práctica 6 ejecutada y exportada.
# Ejecutar en PowerShell desde la raíz de 07_docker_rym_spotify:
# .\scripts\importar_champion_practica6.ps1
param([string]$CarpetaPractica6 = "..\06_fastapi_rym_spotify")
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
$origen = Resolve-Path -LiteralPath (Join-Path $raiz $CarpetaPractica6)
$modelo = Join-Path $origen "models\champion.joblib"
$info = Join-Path $origen "models\model_info.json"
if (-not (Test-Path -LiteralPath $modelo)) { throw "Falta archivo: $modelo" }
if (-not (Test-Path -LiteralPath $info)) { throw "Falta archivo: $info" }
$metadata = Get-Content -LiteralPath $info -Raw -Encoding UTF8 | ConvertFrom-Json
$version = [string]$metadata.sklearn_version
if ($version -notmatch '^\d+\.\d+\.\d+$') { throw "Versión scikit-learn no identificada: $version" }
Copy-Item -LiteralPath $modelo -Destination (Join-Path $raiz "models\champion.joblib") -Force
Copy-Item -LiteralPath $info -Destination (Join-Path $raiz "models\model_info.json") -Force
$envPath = Join-Path $raiz ".env"
$port = "8001"
if (Test-Path -LiteralPath $envPath) {
    $line = Get-Content -LiteralPath $envPath | Where-Object { $_ -match '^APP_PORT=\d+$' } | Select-Object -First 1
    if ($line) { $port = $line.Split('=')[1] }
}
[System.IO.File]::WriteAllText($envPath, "SKLEARN_VERSION=$version`nAPP_PORT=$port`n", (New-Object System.Text.UTF8Encoding($false)))
Write-Host "Modelo copiado desde: $origen"
Write-Host "Versión scikit-learn configurada en Docker: $version"
Write-Host "Siguiente comando: docker compose up -d --build --force-recreate"
