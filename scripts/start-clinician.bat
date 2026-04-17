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

set "HAS_ANTHROPIC="
set "HAS_OPENAI="
for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
  if /I "%%A"=="ANTHROPIC_API_KEY" if not "%%B"=="" set "HAS_ANTHROPIC=1"
  if /I "%%A"=="OPENAI_API_KEY" if not "%%B"=="" set "HAS_OPENAI=1"
)
if not defined HAS_ANTHROPIC if not defined HAS_OPENAI (
  echo [WARN] No API keys found in .env ^(ANTHROPIC_API_KEY or OPENAI_API_KEY^).
  echo [WARN] The app will start, but AI plan generation will fail until a key is configured.
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
echo [INFO] Running quick health checks...
call scripts\health-check-clinician.bat
endlocal
