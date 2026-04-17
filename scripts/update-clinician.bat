@echo off
setlocal

cd /d "%~dp0.."

where docker >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Docker CLI not found.
  exit /b 1
)

echo [INFO] Pulling latest changes...
git pull --ff-only
if errorlevel 1 (
  echo [ERROR] git pull failed. Resolve local changes/conflicts and retry.
  exit /b 1
)

echo [INFO] Rebuilding and restarting HolistiCare...
docker compose up -d --build
if errorlevel 1 (
  echo [ERROR] docker compose up failed.
  exit /b 1
)

echo [OK] HolistiCare updated.
endlocal
