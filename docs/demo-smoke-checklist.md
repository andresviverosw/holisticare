# Demo Smoke Checklist

Use this checklist before demos to verify core backend paths quickly.

## 1) Start stack

```powershell
docker compose up -d --build
docker compose ps
```

Expected:
- `holisticare_db`, `holisticare_backend`, `holisticare_frontend` are `Up`.

## 2) API health and docs

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing | Select-Object -ExpandProperty StatusCode
```

Expected:
- both commands return `200`.

## 3) Ingestion (normal)

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/rag/ingest" -ContentType "application/json" -Body '{"source_dir":"data/mock","force_reindex":false}'
```

Expected response shape:
- `files_processed` (>= 0)
- `chunks_created` (>= 0)
- `status` (`success` or `partial`)

## 4) Ingestion (force reindex)

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/rag/ingest" -ContentType "application/json" -Body '{"source_dir":"data/mock","force_reindex":true}'
```

Expected:
- same response shape as above,
- endpoint completes without `500` for existing files.

## 5) Generate plan

```powershell
$body = @{
  patient_id = "11111111-1111-1111-1111-111111111111"
  intake_json = @{
    profile_version = "generic_holistic_v0"
    chief_complaint = "Dolor lumbar mecanico."
    conditions = @("lumbalgia subaguda")
    goals = @("Reducir dolor")
  }
  available_therapies = @("fisioterapia","acupuntura")
  preferred_language = "es"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/rag/plan/generate" -ContentType "application/json" -Body $body
```

Expected:
- `plan_id`, `status = "pending_review"`, `requires_practitioner_review = true`.

## 6) Retrieve plan and sources

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/rag/plan/<PLAN_ID>"
Invoke-RestMethod -Uri "http://localhost:8000/rag/plan/<PLAN_ID>/sources"
```

Expected:
- plan payload returns persisted `plan_json`,
- sources payload returns `plan_id`, `citations_used`, `sources`.

## 7) Approve/reject

```powershell
Invoke-RestMethod -Method Patch -Uri "http://localhost:8000/rag/plan/<PLAN_ID>/approve" -ContentType "application/json" -Body '{"action":"approve","practitioner_notes":"Aprobado para continuar."}'
```

Expected:
- `status = "approved"` and `plan_json.status = "approved"`.

## 8) CI-safe regression

```powershell
.\.venv\Scripts\python -m pytest -q
```

Expected:
- full suite passes.

## 9) AI quality smoke (deterministic contract checks)

```powershell
scripts\run-ai-quality-smoke.bat
```

Expected:
- Script exits `0`.
- For each pilot case, generation returns `200`, `status = pending_review`, non-empty `weeks`, and `insufficient_evidence = false`.
- At least one citation is produced across all evaluated cases (`--require-any-citations` gate).
