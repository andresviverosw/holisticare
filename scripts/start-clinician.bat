@echo off
setlocal

cd /d "%~dp0.."

where docker >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Docker CLI not found. Install Docker Desktop first.
  exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Docker Desktop is not running. Start Docker Desktop and retry.
  exit /b 1
)

if not exist ".env" (
  if exist ".env.clinician.example" (
    copy ".env.clinician.example" ".env" >nul
    echo [INFO] .env created from .env.clinician.example
    echo [INFO] Edit .env and add API keys before using AI plan generation.
  ) else (
    echo [ERROR] Missing .env and .env.clinician.example.
    exit /b 1
  )
)

echo [INFO] Building and starting HolistiCare...
docker compose up -d --build
if errorlevel 1 (
  echo [ERROR] docker compose failed.
  exit /b 1
)

echo [OK] HolistiCare is running.
echo [INFO] Frontend: http://localhost:5173
echo [INFO] Backend API: http://localhost:8000/docs
endlocal
