# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

HolistiCare is an AI clinical decision support platform for holistic rehabilitation clinics in Mexico. It helps practitioners generate evidence-based multi-week treatment plans using RAG, log clinical sessions, track patient outcomes via a daily diary, and detect progress plateaus. Every AI-generated recommendation requires practitioner approval before activation (NOM-024-SSA3-2012 compliance).

## Project context

This project serves two parallel purposes:
1. **AI4devs master's capstone** — final deliverable requires full 
   AI-assisted documentation followed by AI-assisted build. Milestone 
   tracking matters; always map work to user story IDs.
2. **Consulting portfolio anchor** — demonstrates end-to-end AI system 
   design for clinical use cases in the Mexican health tech space.

**My role:** Architect, ML engineer, and product owner (solo developer).

## Synthetic data strategy

Patient data is entirely synthetic. 8–10 clinician archetypes drive 
data generation (e.g., osteopath, nutritionist, acupuncturist). 
Pydantic validation enforces schema integrity on all synthetic records. 
Real patient data is never used in development or testing.

## Clinical co-design

Treatment plan structure and approval workflows were designed around 
practitioner input sessions. When modifying plan schemas or governance 
logic, flag any change that could affect the practitioner approval UX — 
these decisions have clinical and regulatory implications (NOM-024).

## Regulatory constraint

NOM-024-SSA3-2012 compliance is non-negotiable. Every AI-generated 
recommendation must require explicit practitioner approval. Never 
suggest architectural changes that would allow auto-activation of plans.

## Commands

### Backend

```bash
# Run all tests (no Docker, no real API keys needed — CI-safe)
python -m pytest -q

# Run a single test file or test function
python -m pytest backend/tests/test_plateau_service.py -v
python -m pytest backend/tests/test_plateau_service.py -k "test_worsening" -v

# Start backend only (requires Docker)
docker compose up -d db backend

# Trigger PDF ingestion (admin-gated API endpoint) after starting services
curl -X POST http://localhost:8000/rag/ingest -H "Authorization: Bearer <token>" \
  -d '{"source_dir": "data/mock", "force_reindex": false}'
```

### Frontend

```bash
cd frontend
npm run dev          # Vite dev server → http://localhost:5173
npm run lint         # ESLint
npm test             # Vitest unit tests
npm run test:e2e     # Playwright E2E (requires running backend+frontend)
npm run build        # Production build
```

### Full stack

```bash
docker compose up -d         # Starts db, backend, frontend
docker compose logs -f       # Tail all logs
```

## Architecture

### Request flow

```
HTTP → FastAPI (app/api/rag.py)
      → Dependency injection (deps.py: JWT auth, get_db, get_rag_pipeline)
      → Services layer (app/services/*.py) — pure async business logic
      → ORM models (app/models/*.py) / RAGPipeline
```

### RAG pipeline (`app/rag/pipeline.py`)

Five sequential phases, orchestrated by `RAGPipeline.generate_plan()`:

1. **Query construction** (`generation/query_builder.py`) — LLM builds a clinical summary from intake JSON, then expands it into N query variants (default: 4)
2. **Vector retrieval** (`retrieval/vector_search.py`) — searches `clinical_chunks` via pgvector (cosine similarity), top-K candidates per query variant
3. **Reranking** (`retrieval/reranker.py`) — cross-encoder (default: `cross-encoder/ms-marco-MiniLM-L-6-v2`) or Cohere reduces candidates to top-K final chunks
4. **Generation** (`generation/generator.py`) — Claude builds a structured JSON treatment plan citing chunks by `REF-ID`; if no chunks retrieved, an `insufficient_evidence` plan is returned instead of calling the LLM
5. **Nutrition safety guards** (`pipeline.py → apply_nutrition_safety_guards()`) — blocks any diet recommendation that matches an intake contraindication/allergy term, using configurable synonym groups

All LLM calls go through `app/rag/llm_chat.py → complete_claude_or_openai()`, which tries Claude first and falls back to OpenAI Chat (same prompt) when `RAG_LLM_FALLBACK_OPENAI=true`.

### Auth

JWT (HS256), claims `sub` + `role`. Roles: `clinician`, `admin`, `patient`. The `require_roles()` dependency in `deps.py` enforces RBAC. The dev login endpoint (`POST /auth/dev-login`) is only registered when `ALLOW_DEV_AUTH=true` (must never be true in production). Patient diary access additionally enforces that `sub == patient_id` UUID.

### Database

PostgreSQL 16 + pgvector. Schema initialized from `infra/init.sql`. Async driver is `asyncpg` via SQLAlchemy 2.0. All ORM models inherit from `Base` defined in `app/core/database.py`. The `app.models` import in `main.py` registers all table metadata before the engine is used.

Key tables:
- `clinical_chunks` — 1536-dim pgvector index of ingested clinical documents with IVFFlat cosine index
- `treatment_plans` — plan JSON + status lifecycle (`pending_review → approved | rejected`)
- `intake_profiles` + `intake_profile_audit` — patient profiles with change history
- `care_sessions` — structured session logs (JSONB)
- `patient_diary_entries` — one row per patient per day (UNIQUE constraint enforced)
- `plan_memory_bank` — de-identified approved plan snapshots reusable as templates (US-PLAN-004)

### Configuration

All settings in `app/core/config.py` (pydantic-settings, loaded once via `@lru_cache`). `.env.example` lists every variable. Key non-obvious settings:

- `ALLOW_DEV_AUTH` — defaults to `false` in docker-compose; must be set in `.env` to enable dev login
- `RAG_LLM_FALLBACK_OPENAI` — enables OpenAI chat fallback when Anthropic fails
- `NUTRITION_SAFETY_TERMS_PATH` — overrides bundled `app/config/nutrition_safety_terms.json`; API refuses to start if the file is missing or schema-invalid
- `PDF_OCR_FALLBACK_ENABLED` — hybrid OCR via PyMuPDF + Tesseract for scanned PDFs (spa+eng by default)
- `RERANKER_BACKEND` — `crossencoder` (free, model downloaded on first use) or `cohere`

## Key conventions

**Services layer**: Business logic lives in `app/services/` as plain async functions (not on ORM models). Services receive a `db: AsyncSession` and return ORM rows or dicts.

**Pydantic schemas**: Input schemas are versioned (`_v0` suffix, e.g. `GenericHolisticIntakeV0`, `PatientDiaryCheckinV0`). They live in `app/schemas/`, separate from ORM models in `app/models/`.

**All clinical routes**: Live in a single `APIRouter` in `app/api/rag.py` mounted at `/rag`. There is no sub-router split.

**Plan governance**: Every generated plan has `requires_practitioner_review: true` and `status: pending_review`. The generator system prompt hard-codes this rule (NOM-024 compliance). Plans with `insufficient_evidence: true` skip LLM generation and return a structured empty-weeks response for manual completion.

**Testing strategy**: The `conftest.py` fixture `client` stubs the DB session (AsyncMock) and injects a `clinician` auth user, so tests never need PostgreSQL or real API keys. Tests that need the real RAG pipeline mock `get_rag_pipeline` via `app.dependency_overrides`. CI runs `pytest tests/ -q` from within the `backend/` directory.

**Frontend routing**: Protected routes wrap under `<RequireClinician>` (JWT check) then `<Layout>`. Public route is only `/login`.

**Ingestion**: PDFs go in `backend/data/mock/` (synthetic) or `backend/data/raw/` (real). The ingestion endpoint is admin-only. Each file gets a deterministic `ref_id` (`SHA256[:8]` + page). Chunks already indexed are skipped unless `force_reindex=true`.

## Engineering standards

This project follows TDD (Red → Green → Refactor), SOLID design, and DRY for shared business logic. Every change should map to a user story ID (e.g. `US-RAG-004`, `US-ANLY-002`, `US-PRED-001`). Comments in code reference story IDs when a constraint is non-obvious.
