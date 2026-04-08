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

### 3.1) Dev login (`ALLOW_DEV_AUTH`)

`docker-compose.yml` defaults **`ALLOW_DEV_AUTH` to `false`** (safe default). The SPA **“Entrar (desarrollo)”** button calls `POST /auth/dev-login`, which is **not registered** unless dev auth is on — you will see **404** until you opt in.

Add to your **`.env`** (copy from `.env.example` if needed):

```env
ALLOW_DEV_AUTH=true
```

Restart the backend container after changing env:

```powershell
docker compose up -d backend
```

Never set `ALLOW_DEV_AUTH=true` in production. See `09-security-audit-and-todos.md` (TODO-SEC-007).

### 3.2) Backend Docker image vs `requirements.txt`

Application code is bind-mounted from `./backend`, but **Python packages inside the image** come from the last **`docker compose build`**. After you change **`backend/requirements.txt`**, rebuild so the container matches (for example before exercising RAG or LLM imports):

```powershell
docker compose build backend
docker compose up -d backend
```

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

## 4.1) Ingestion smoke command

Basic ingestion (idempotent: skips already indexed chunks):

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/rag/ingest" -ContentType "application/json" -Body '{"source_dir":"data/mock","force_reindex":false}'
```

Force reindex for the same files (removes previous chunks by `source_file` and reindexes):

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/rag/ingest" -ContentType "application/json" -Body '{"source_dir":"data/mock","force_reindex":true}'
```

### 4.2) Scanned PDFs (OCR)

Digital PDFs with a text layer are ingested without OCR. **Scanned or image-only PDFs** need **Tesseract**: the backend uses **PyMuPDF** plus **pytesseract** when native text per file is very short or empty (see `backend/app/rag/ingestion/pdf_ocr.py`).

- **Docker:** the backend image installs `tesseract-ocr` with Spanish and English data (`Dockerfile`). Rebuild after pulling changes.
- **Local Python (no Docker):** install [Tesseract](https://github.com/tesseract-ocr/tesseract) and ensure it is on `PATH`, or OCR fallback will log a warning and skip those files.

Optional environment variables: `PDF_OCR_*` in `.env.example`.

### 4.3) HTML pages (`.html` / `.htm`)

The same ingestion endpoint indexes **static HTML** as well as PDFs. Drop `.html` or `.htm` files under your `source_dir` (for example `data/mock`). The backend strips `script`, `style`, and `noscript`, extracts visible text (preferring `<body>`), and indexes one document per file. **OCR and the “thin PDF” hybrid path apply only to `.pdf` files**, not HTML.

Implementation: `backend/app/rag/ingestion/html_reader.py`, wired in `backend/app/rag/ingestion/loader.py`.

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

GitHub Actions runs the same suite on push/PR (`.github/workflows/ci.yml`). The workflow also runs **`security-audit`** (`pip-audit`, `bandit`, `npm audit`) — **blocking** by default; see `docs/README.md` and `09-security-audit-and-todos.md`.

API smoke (from repository root, backend reachable at `http://127.0.0.1:8000`):

```powershell
npm run smoke:api
```

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
