# HolistiCare

AI-powered holistic rehabilitation platform for continuity of care, data-driven treatment personalization, and measurable patient outcomes.

Master's **final project** for AI4devs — branch `finalproject-AVW` · tag `v1.0-final-AVW`.

**Source repository:** [github.com/andresviverosw/holisticare](https://github.com/andresviverosw/holisticare)

| Entrega | Enlace |
|---------|--------|
| Rama final | https://github.com/andresviverosw/holisticare/tree/finalproject-AVW |
| Tag release | https://github.com/andresviverosw/holisticare/releases/tag/v1.0-final-AVW |
| SPA (demo público) | https://holisticare-frontend.onrender.com |
| API (demo público) | https://holisticare-api.onrender.com (`/health`) |
| Documento de entrega (MD/PDF) | [`docs/entrega-final-capstone.md`](docs/entrega-final-capstone.md) · [`docs/entrega-final-capstone.pdf`](docs/entrega-final-capstone.pdf) |
| Prompts (plantilla AI4devs) | [`prompts.md`](prompts.md) |

### Demo rápida (clínico)

1. Abrir la SPA → **Entrar (desarrollo — clínico)** o usuario sembrado `clinician` (password en `docs/deploy-final-demo.md`).
2. Pegar paciente sintético *improving*: `be2ecd39-2ac6-5a8b-84af-b22f8fa7a4a8`.
3. Revisar intake, diario, gráfico de progreso (con proyección), trayectoria y recomendaciones.
4. Vista paciente: cerrar sesión → login desarrollo paciente con el mismo UUID → `/diario`.

> Free tier Render: cold start de API puede tardar ~50s+.

---

## Problem

Holistic rehab patients often receive care across modalities like acupuncture, hydrotherapy, herbal medicine, physiotherapy, and psycho-emotional therapy. In many clinics, progress tracking remains fragmented and treatment adaptation is mostly intuition-based.

This causes three major gaps:
- Low continuity between sessions
- Limited personalization over time
- Weak measurement of outcomes and treatment impact

## Solution

HolistiCare is an AI clinical decision support platform that helps practitioners:
- Build structured patient intake profiles
- Generate evidence-based multi-week treatment plan suggestions with RAG
- Log sessions with structured data and AI-assisted note completion
- Monitor symptom and wellbeing trends between sessions
- Detect plateaus and correlate therapies with outcomes
- Estimate recovery trajectory and suggest adjustments

Every AI-generated recommendation is reviewed and approved by a practitioner before activation.

## Target users

- Primary: Holistic rehab clinicians (physiotherapists, naturopaths, integrative medicine doctors)
- Secondary: Outpatient rehab patients
- Tertiary: Clinic administrators and directors

## MVP scope

1. Patient intake and profile builder with LLM risk flagging
2. AI treatment plan generator (RAG-powered) with practitioner approval gate
3. Session logger (structured + free text + LLM assistance)
4. Patient symptom and wellbeing diary (mobile-friendly)
5. Progress analytics dashboard
6. Outcome prediction model for recovery trajectory

## Technology stack

| Layer | Technology |
|-------|-----------|
| LLM | Anthropic Claude (primary) + optional OpenAI chat fallback |
| Embeddings | OpenAI text-embedding-3-small |
| RAG | Custom pipeline (`app/rag/`) + LlamaIndex PGVectorStore (ingest) |
| Vector store | PostgreSQL 16 + pgvector |
| Optional reranker | Cross-encoder (local) or Cohere |
| Backend | Python + FastAPI + SQLAlchemy 2 async |
| Frontend | React 19 + Tailwind CSS + Vite |
| Auth | JWT HS256 (clinician password, patient invite, optional dev login) |
| Deployment | Docker; **public demo on Render** (API + Static Site + Postgres) |
| CI/CD | GitHub Actions → CI gate → `cd-render.yml` |

## RAG architecture overview

HolistiCare uses a five-layer RAG pipeline:

1. Offline ingestion  
   PDF extraction -> chunking (400-600 tokens, 50-100 overlap) -> embeddings -> vector index with metadata (therapy type, condition, evidence level, language)
2. Query construction  
   LLM profile summarization + multi-query expansion (3-4 angles)
3. Retrieval and reranking  
   Retrieve top candidates, rerank, pass top 8-10 chunks
4. Prompt construction and generation  
   Citation-bound prompt with REF-ID traceability and contraindication checks
5. Structured output and governance  
   JSON treatment plan persisted with source refs and practitioner approval record

## Synthetic data strategy

To accelerate development while protecting patient privacy:

- 8 clinician archetypes × 4 trajectory variants = **32 patients** in the shipped package (`backend/data/synthetic/v1/dataset.json`)
- Optional full scale: `--variants 10` → **80 patients** (README target)
- Schema-first JSON generation with Pydantic (`generic_holistic_v0`, `patient_diary_v0`, `clinical_session_v0`)
- ~8 week longitudinal sessions + daily diary journeys
- Trajectory cohorts exercise KPIs: improving, high-pain plateau, worsening, short/insufficient series
- Realism rules: non-linear noise, ~15% missed diary days, adverse-event notes (~5%)
- NOM-024: every plan keeps `requires_practitioner_review: true`
- Generate / seed: see [`docs/synthetic-dataset-v1.md`](docs/synthetic-dataset-v1.md)

## Outcome instruments

- NRS or VAS (pain)
- SF-12 (quality of life)
- PSQI (sleep)
- PHQ-9 / GAD-7 (mental health)
- Barthel Index (functional independence)
- Condition-specific where relevant: DASH, WOMAC, ODI

## Regulatory and compliance context (Mexico)

- NOM-024-SSA3-2012 for electronic health records
- LFPDPPP for personal data protection

Implementation requirements:
- Data collection purpose and minimization rationale
- Encryption at rest
- Consent management
- Access control documentation
- Retention and deletion policy
- Recommendation traceability and audit logs

## Project documentation phases

Core documentation for the master's delivery is organized in:

1. Requirements and domain research
2. System architecture document
3. Data dictionary and privacy framework
4. Feature specs and user stories
5. Test plan
6. Deployment and operations runbook

See the `docs/` directory for templates and working files.

## Repository structure

```
holisticare/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   └── rag/
│   │       ├── ingestion/
│   │       ├── retrieval/
│   │       ├── generation/
│   │       └── pipeline.py
│   ├── scripts/
│   └── tests/
├── frontend/
│   └── src/
├── infra/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick start

For full local setup and troubleshooting steps, see `docs/setup.md`.

```bash
# 1) Configure local environment
cp .env.example .env
# Fill required keys in .env

# 2) Start services
docker compose up -d

# 3) Run ingestion on mock documents
docker compose exec backend python -m scripts.ingest --source data/mock

# 4) Open services
# Frontend: http://localhost:5173
# API docs:  http://localhost:8000/docs
```

## Capstone public demo (Render)

Final master’s demo hosts on **Render** (same approach as Entrega 2). Blueprint: [`render.yaml`](render.yaml). Operator guide: [`docs/deploy-final-demo.md`](docs/deploy-final-demo.md).

| Service | Public URL | Notes |
|---------|------------|-------|
| SPA | https://holisticare-frontend.onrender.com | `VITE_API_BASE_URL` → API |
| API | https://holisticare-api.onrender.com | `/health` → 200; free-tier cold start ~50s+ |

**CD:** pushes to `main` that pass CI trigger [`.github/workflows/cd-render.yml`](.github/workflows/cd-render.yml) (Render `autoDeploy` off). Requires GitHub secret `RENDER_API_KEY` — see deploy doc §6.

Local fallback: Quick start above + smoke script `backend/scripts/smoke_public_demo.py`.

Privacy / eval / feedback package: [`docs/03-data-dictionary-and-privacy-framework.md`](docs/03-data-dictionary-and-privacy-framework.md), [`docs/rag-evaluation-report.md`](docs/rag-evaluation-report.md), [`docs/feedback-01-synthetic-demo-waiver.md`](docs/feedback-01-synthetic-demo-waiver.md).

## Test command

Local CI-safe suite (no Docker or API keys required):

```bash
python -m pytest -q
```

Inside the backend container:

```bash
docker compose exec backend pytest tests/ -v
```

## Final delivery package (AI4devs)

Plantilla requerida:

- [`README.md`](README.md) (este archivo)
- [`prompts.md`](prompts.md) — prompts de producto y de desarrollo asistido por IA

Evidencia de despliegue:

- URLs públicas (tabla al inicio)
- Capturas + arquitectura: [`docs/entrega-final-capstone.pdf`](docs/entrega-final-capstone.pdf)
- Ops: [`docs/deploy-final-demo.md`](docs/deploy-final-demo.md)

Formulario de envío del programa: https://lidr.typeform.com/proyectoai4devs (pegar la URL de la rama `finalproject-AVW`).
