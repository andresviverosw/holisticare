@echo off
setlocal

cd /d "%~dp0.."

where docker >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Docker CLI not found.
  exit /b 1
)

echo [INFO] Stopping HolistiCare containers...
docker compose down
if errorlevel 1 (
  echo [ERROR] docker compose down failed.
  exit /b 1
)

echo [OK] HolistiCare has been stopped.
endlocal
