# Local Setup and Verification

This guide provides a clean, repeatable setup for HolistiCare on local development environments.

## 1) Prerequisites

- Docker Desktop (running)
- Python 3.10+
- Node.js LTS and npm

Optional but recommended:
- PowerShell 7+

## 2) First-time local setup

From repository root:

```powershell
Copy-Item ".env.example" ".env" -Force
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r "backend\requirements.txt"
```

Install frontend dependencies:

```powershell
cd frontend
npm install
cd ..
```

## 3) Start with Docker Compose

```powershell
docker compose up -d --build
```

Check running services:

```powershell
docker compose ps
```

Expected services:
- `holisticare_db`
- `holisticare_backend`
- `holisticare_frontend`

## 4) Health checks

Backend docs:

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
```

Frontend:

```powershell
Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
```

Both should return `200`.

## 5) Local test commands

Backend tests (no PostgreSQL or API keys required — `conftest.py` sets CI-safe defaults and stubs DB for HTTP tests):

From repository root (recommended — uses root `pytest.ini`):

```powershell
.\.venv\Scripts\python -m pytest -q
```

Or from `backend/` (venv at repo root):

```powershell
cd backend
..\.venv\Scripts\python -m pytest tests\ -q
```

GitHub Actions runs the same suite on push/PR (`.github/workflows/ci.yml`).

Frontend production build check:

```powershell
cd frontend
npm run build
cd ..
```

## 6) Common recovery commands

If Docker state gets inconsistent:

```powershell
docker compose down --remove-orphans
docker system prune -f
docker compose up -d --build
```

If dependencies changed:

```powershell
.\.venv\Scripts\python -m pip install -r "backend\requirements.txt"
cd frontend
npm install
cd ..
```

## 7) Stop environment

```powershell
docker compose down
```

## 8) Security note

- Do not commit `.env`.
- Avoid sharing terminal output that expands environment values.
- For compose inspection, use:

```powershell
.\scripts\compose-config-safe.ps1
```

- If running manually, prefer:

```powershell
docker compose config --no-interpolate
```
