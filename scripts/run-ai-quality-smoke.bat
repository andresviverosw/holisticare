@echo off
setlocal

cd /d "%~dp0.."

where docker >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Docker CLI not found. Install Docker Desktop first.
  exit /b 1
)

echo [INFO] Ensuring stack is running...
docker compose up -d
if errorlevel 1 (
  echo [ERROR] Failed to start containers.
  exit /b 1
)

echo [INFO] Running AI quality smoke checks...
docker compose exec backend env PYTHONPATH=/app python scripts/ai_quality_smoke.py --require-any-citations
if errorlevel 1 (
  echo [ERROR] AI quality smoke failed.
  exit /b 1
)

echo [OK] AI quality smoke passed.
endlocal
