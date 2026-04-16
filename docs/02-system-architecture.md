# Phase 2 - System Architecture

## Document control

- Owner:
- Contributors:
- Version:
- Last updated: 2026-04-10
- Status: `[ ]` Draft `[x]` In progress `[ ]` Complete

## 1. Objective

Define the end-to-end architecture for HolistiCare, including application layers, AI pipeline, data flow, and governance controls.

**Rendered diagrams (Mermaid):** Canonical **context, containers, ER, flows, state, and component** figures live in [`10-solution-diagrams.md`](10-solution-diagrams.md). This phase document summarizes behavior and points there for visuals; implementation detail and env vars remain in [`08-developer-guide-and-architecture.md`](08-developer-guide-and-architecture.md).

## 2. Architecture principles

- Practitioner-in-the-loop by default
- Traceability for every AI recommendation
- Privacy and security by design
- Modular services for phased delivery
- Observable and testable AI behavior

## 3. Context diagram (C4 - Level 1)

- **System boundary:** HolistiCare — web client talking to a single backend API backed by PostgreSQL; the API calls external LLM providers for embeddings and generation.
- **External actors:** Clinicians and admins (full app); patients (diary and related flows where exposed).
- **External systems:** Anthropic (Claude) for summarization/query expansion/plan JSON; OpenAI for embeddings (and optional rerank, depending on configuration); HTTPS between browser and API.

See **Section 1** in [`10-solution-diagrams.md`](10-solution-diagrams.md).

## 4. Container architecture (C4 - Level 2)

| Container | Responsibility | Tech | Inputs | Outputs |
|-----------|----------------|------|--------|---------|
| Frontend | SPA: intake/plan UI, plan review, chunk browse, auth token handling | React, Vite | User actions, JWT | REST calls to `/api` |
| API backend | REST API, JWT auth, orchestration of services and RAG pipeline | FastAPI, Python | HTTP + JSON | JSON responses; DB writes |
| RAG pipeline | In-process retrieval, rerank, generation (not a separate deployable) | Python modules under `app/rag/` | Intake JSON, therapy filters | Plan JSON, citations |
| Relational DB | Transactional storage for profiles, plans, sessions, diary | PostgreSQL | SQL from SQLAlchemy/async | Persisted rows |
| Vector index | Chunk storage and similarity search | pgvector in PostgreSQL (`data_clinical_chunks`) | Embeddings + metadata | Retrieved chunks |
| Model services | Hosted LLM APIs | Anthropic, OpenAI | Prompts / vectors | Text, embeddings |

See **Section 2** in [`10-solution-diagrams.md`](10-solution-diagrams.md).

## 5. Core workflows

### 5.1 Intake to treatment plan

1. Clinician persists structured intake (`POST /rag/intake`) keyed by `patient_id`.
2. Clinician requests a draft plan (`POST /rag/plan/generate`); the RAG pipeline retrieves evidence from `data_clinical_chunks`, optionally reranks, and generates structured JSON with REF-IDs.
3. Draft is stored (`treatment_plans`) with `pending_review` until a clinician approves or rejects.

Flowchart: **Section 7** in [`10-solution-diagrams.md`](10-solution-diagrams.md). Sequence detail: **Section 11** and [`08-developer-guide-and-architecture.md`](08-developer-guide-and-architecture.md) (RAG pipeline sequence).

### 5.2 Session logging and analytics update

1. Clinician records a visit (`POST /rag/sessions`) with structured session JSON.
2. Longitudinal data for analytics is read from `patient_diary_entries` (and related services) for trend and plateau endpoints.
3. Dashboards consume `GET` analytics routes (outcomes trend, plateau flags) with role-guarded access.

Flowchart: **Section 10** in [`10-solution-diagrams.md`](10-solution-diagrams.md).

### 5.3 Patient diary ingestion

1. Patient or authorized role submits daily check-ins (`POST /rag/diary`), upserted by `(patient_id, entry_date)`.
2. Clinician queries diary history for charts and analytics windows.
3. Analytics services aggregate diary series for trends and heuristics (e.g. plateau detection).

Same flow reference as **5.2**; diary-specific API contracts: [`04-feature-specs-and-user-stories.md`](04-feature-specs-and-user-stories.md) (US-DIARY-001, US-ANLY-001/002).

## 6. RAG architecture detail

Normative behavior is implemented in `backend/app/rag/` and summarized below. Diagrams: **Sections 4–5, 7, 9, 11** in [`10-solution-diagrams.md`](10-solution-diagrams.md).

### 6.1 Offline ingestion

- **Source types:** PDF and HTML ingested from a configured `source_dir` (see [`08-developer-guide-and-architecture.md`](08-developer-guide-and-architecture.md)).
- **Chunking strategy:** Loader/chunking pipeline produces rows in `data_clinical_chunks` via LlamaIndex PGVectorStore.
- **Metadata schema:** JSON metadata includes `ref_id`, therapy tags, language, evidence level, etc. (see chunk listing SQL in `chunk_query`).
- **Embedding process:** OpenAI embedding model writes vectors into pgvector-backed storage.

### 6.2 Query construction

- **Profile summarization:** `QueryBuilder` derives a clinical summary from intake JSON.
- **Multi-query expansion:** Same module expands queries for broader retrieval before vector search.

### 6.3 Retrieval and reranking

- **Top-k policy:** Configured via `VectorRetriever` / `RetrievalConfig` (see code for current limits).
- **Filtering strategy:** Therapy and metadata filters applied during retrieval.
- **Reranker policy:** Pluggable reranker (`get_reranker()`); may be cross-encoder or provider-specific.

### 6.4 Prompt and generation

- **Prompt template controls:** `PlanGenerator` builds prompts constrained to retrieved chunks and intake context.
- **Contraindication requirements:** Output must respect profile constraints as encoded in prompts and validation (see product specs for evolution).
- **Output schema contract:** Structured plan JSON with weeks, citations, and practitioner-review flags; insufficient-evidence path returns an explicit stub plan (see `build_insufficient_evidence_plan` in `pipeline.py`).

### 6.5 Approval and persistence

- **Approval gate states:** See plan status state diagram — **Section 12** in [`10-solution-diagrams.md`](10-solution-diagrams.md); persisted on `treatment_plans.status`.
- **Audit events:** Intake edits record audit rows (`intake_profile_audit`); plan approval timestamps and actor fields on `treatment_plans`.
- **Source traceability:** `citations_used` and `GET /rag/plan/{id}/sources` align with chunk `ref_id` metadata.

## 7. Data architecture

- **Transactional schema overview:** Logical ER — **Section 3** in [`10-solution-diagrams.md`](10-solution-diagrams.md). Tables: `intake_profiles`, `intake_profile_audit`, `treatment_plans`, `care_sessions`, `patient_diary_entries`, plus vector table `data_clinical_chunks`.
- **Analytical schema overview:** Analytics read from diary (and related) transactional tables via service-layer queries; no separate data warehouse in MVP.
- **Data lifecycle and retention:** Detailed retention and privacy rules belong in [`03-data-dictionary-and-privacy-framework.md`](03-data-dictionary-and-privacy-framework.md) (to be aligned with deployment policy).

## 8. Security and privacy architecture

- **Authentication and authorization model:** JWT bearer tokens; role claims (`clinician`, `admin`, `patient`) enforced per route (see [`08-developer-guide-and-architecture.md`](08-developer-guide-and-architecture.md) and [`09-security-audit-and-todos.md`](09-security-audit-and-todos.md)).
- **Encryption in transit and at rest:** TLS for client–server traffic in production; database encryption depends on hosting (document in ops runbook).
- **Key management approach:** API keys for LLM providers and `SECRET_KEY` for JWT — environment/secret store in deployment (`06-deployment-and-ops-runbook.md`).
- **Consent and access logging:** Product requirements in phase 1/3 docs; audit trails for intake edits as implemented above.

## 9. Reliability and operations

- **Availability targets:** MVP assumes single-region deployment; formal SLOs TBD with stakeholders.
- **Backup and restore:** PostgreSQL backup strategy per [`06-deployment-and-ops-runbook.md`](06-deployment-and-ops-runbook.md).
- **Failure modes and fallbacks:** LLM and embedding failures map to explicit HTTP errors (`502`/`503`); insufficient retrieval yields a non-fabricated insufficient-evidence plan (see RAG pipeline).
- **Monitoring and alerting:** CI health checks and manual smoke steps in `setup.md` / `demo-smoke-checklist.md`; production observability TBD.

## 10. Architecture decisions (ADRs)

| ADR ID | Decision | Status | Rationale | Trade-offs |
|--------|----------|--------|-----------|------------|
| ADR-001 | PostgreSQL holds both relational data and pgvector chunks (LlamaIndex PGVectorStore) | Accepted | One datastore for MVP; simpler ops than separate vector DB | Couples scaling of OLTP and vector load |
| ADR-002 | Practitioner approval required before treating AI output as care-ready; draft persisted with `pending_review` | Accepted | Safety and regulatory alignment | Extra clinician step |

## 11. Open issues

- Formal SLO/SLA and production monitoring stack.
- Retention/deletion automation versus [`03-data-dictionary-and-privacy-framework.md`](03-data-dictionary-and-privacy-framework.md) completion.
- Optional: split `rag.py` router for maintainability (see [`engineering-solid-dry-review.md`](engineering-solid-dry-review.md)).

## Completion checklist

- [x] C4 context and container views complete (see [`10-solution-diagrams.md`](10-solution-diagrams.md))
- [x] Data and AI workflows documented (cross-linked)
- [~] Security and privacy controls mapped (detail in phase 3 and security doc)
- [~] Reliability strategy defined (ops doc and open issues)
- [x] Major decisions captured in ADRs (initial set)
