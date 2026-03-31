# HolistiCare

AI-powered holistic rehabilitation platform for continuity of care, data-driven treatment personalization, and measurable patient outcomes.

Master's final project for AI4devs (March 2026), and the first consulting deliverable for clinics in the holistic and integrative medicine sector in Mexico.

**Source repository:** [github.com/andresviverosw/holisticare](https://github.com/andresviverosw/holisticare)

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
| LLM | Claude API (claude-sonnet) |
| Embeddings | OpenAI text-embedding-3-small |
| RAG and orchestration | LangChain or LlamaIndex |
| Vector store | PostgreSQL + pgvector (or Chroma for experimentation) |
| Optional reranker | Cohere Rerank |
| Backend | Python + FastAPI |
| Frontend | React + Tailwind CSS + Vite |
| ML models | scikit-learn / XGBoost |
| Auth and privacy | JWT + encryption at rest |
| Deployment | Docker + GCP or AWS |

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

- 8-10 clinician-validated patient archetypes
- 6-12 variants each (~80-100 synthetic patients)
- Schema-first JSON generation with strict field constraints
- 8-12 week longitudinal session journeys
- Daily diary entries (including Spanish free text)
- Realism rules: non-linear improvement, adverse events (~5%), motivation-dependent recovery speed
- Validation with Pydantic, clinician spot-checks, and distribution review

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

## Test command

Local CI-safe suite (no Docker or API keys required):

```bash
python -m pytest -q
```

Inside the backend container:

```bash
docker compose exec backend pytest tests/ -v
```

## Immediate next steps

- Confirm final project name and bilingual branding
- Run first clinical co-design session
- Curate first 10-15 clinical PDFs for RAG seed set
- Select 3-4 priority outcome instruments for MVP
- Generate first 20 synthetic patient profiles for schema validation
- Draft full architecture diagram and decision record set
