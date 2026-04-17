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

echo [INFO] Running pilot rehearsal suite...
docker compose exec backend env PYTHONPATH=/app python scripts/pilot_rehearsal.py
if errorlevel 1 (
  echo [ERROR] Pilot rehearsal failed.
  exit /b 1
)

echo [OK] Pilot rehearsal completed successfully.
endlocal
