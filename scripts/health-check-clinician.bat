@echo off
setlocal

cd /d "%~dp0.."

where docker >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Docker CLI not found.
  exit /b 1
)

echo [INFO] Checking container status...
docker compose ps
if errorlevel 1 (
  echo [ERROR] Could not read docker compose status.
  exit /b 1
)

echo [INFO] Checking API and frontend endpoints...
powershell -NoProfile -Command ^
  "$ErrorActionPreference='Stop';" ^
  "$health=(Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing).StatusCode;" ^
  "$docs=(Invoke-WebRequest -Uri 'http://localhost:8000/docs' -UseBasicParsing).StatusCode;" ^
  "$front=(Invoke-WebRequest -Uri 'http://localhost:5173' -UseBasicParsing).StatusCode;" ^
  "if($health -ne 200 -or $docs -ne 200 -or $front -ne 200){ throw 'Unexpected status codes.' }" ^
  "Write-Host ('[OK] /health=' + $health + ', /docs=' + $docs + ', frontend=' + $front)"
if errorlevel 1 (
  echo [ERROR] HTTP checks failed. Verify Docker is healthy and ports 5173/8000 are available.
  exit /b 1
)

echo [INFO] Running API smoke script...
node scripts/smoke-api.mjs
if errorlevel 1 (
  echo [ERROR] API smoke checks failed.
  exit /b 1
)

echo [OK] Health checks passed.
endlocal
