# Engineering review: SOLID and DRY (HolistiCare)

Snapshot audit of the codebase with file references and suggested refactors. Last updated: 2026-04-09.

## Summary

The backend is **service-oriented** (intake, diary, plans in separate modules), which is good. The main structural issue is **`app/api/rag.py` as a single large router** mixing many domains and a **long, repetitive LLM error-mapping block** in `generate_plan`. The frontend already **DRYs API errors** via `formatApiError`, with one notable inconsistency.

---

## SOLID

### S — Single responsibility

| Area | Observation |
|------|-------------|
| **`backend/app/api/rag.py` (~550+ lines)** | Declares many Pydantic request models **and** wires intake, sessions, diary, analytics, chunks, ingest, plan generate/approve/sources. The **module** does too much; splitting into sub-routers (e.g. `intake.py`, `plans.py`, `diary.py`) would align each file with one bounded context. |
| **Services layer** | Generally **good**: `intake_service`, `diary_service`, `session_service`, etc. keep domain logic out of handlers. |
| **`RAGPipeline`** | Orchestration only — **appropriate** responsibility. |

### O — Open/closed

| Area | Observation |
|------|-------------|
| **Reranker** | `BaseReranker` + `get_reranker()` factory — **good** extension point. |
| **New LLM providers** | Logic is centralized in `llm_chat.py` — **reasonable** for OpenAI fallback; adding a third provider would push you toward a small strategy/protocol. |
| **`generate_plan` exception list** | Adding a new provider means **editing** the same big `try/except` — better closed for extension via a **single mapper** or middleware-style handler. |

### L — Liskov substitution

| Area | Observation |
|------|-------------|
| **Reranker hierarchy** | Subclasses honor `rerank(...)` contract — **no red flags** from a quick read. |

### I — Interface segregation

| Area | Observation |
|------|-------------|
| **FastAPI `Depends`** | Per-route dependencies are **narrow** (`require_roles`, `get_db`) — **fine**. |
| **No fat “god” service interfaces** | Python duck-typing; not a major issue here. |

### D — Dependency inversion

| Area | Observation |
|------|-------------|
| **`deps.get_rag_pipeline` / `get_ingestion_service`** | Return **concrete** types; tests use overrides — **acceptable** for FastAPI, but production code **always** depends on concrete `RAGPipeline` / `IngestionService`. |
| **`RAGPipeline.__init__`** | Builds `QueryBuilder`, `VectorRetriever`, `PlanGenerator` internally — **harder to unit-test** the pipeline with stubbed collaborators without replacing the whole class. Injecting interfaces (or factories) would improve **D** and test ergonomics. |
| **Module-level `settings = get_settings()`** | Used in `pipeline`, `query_builder`, `generator`, `embedder`, `loader`, `vector_search`, `reranker`. `get_settings` is `@lru_cache`d, so behavior is stable, but modules are **tightly coupled to global config** instead of receiving `Settings` (constructor injection would be purer **D**). |

---

## DRY

| Issue | Where | Note |
|--------|--------|------|
| **Repeated LLM → HTTP mapping** | `rag.generate_plan` | Many `except …: raise HTTPException(503, detail=…)` blocks — **strong candidate** for one function, e.g. `plan_generation_http_error(exc) -> HTTPException`. |
| **Same `ValueError` → 422** | Analytics routes (e.g. outcomes trend, plateau flags) | Identical `try` / `except ValueError` — small **DRY** win with a decorator or shared helper. |
| **Repeated 404 phrasing** | `approve_plan`, `get_plan`, `get_plan_sources` | Same `"Plan not found"` — optional helper `not_found("Plan not found")` (cosmetic). |
| **JSON metadata projection SQL** | `chunk_query` vs `plan_persistence` | Both select from `data_clinical_chunks` with similar `metadata_::jsonb->>'…'` — **conceptual duplication**. Centralizing in a **single SQL text constant** or a thin repository module reduces drift (watch **Bandit B608** if you interpolate; static strings are fine). |
| **`get_settings()` at import** | Multiple RAG modules | Not copy-paste **DRY** violation, but a **shared pattern** that spreads coupling to config everywhere. |

### Frontend

| Issue | Where | Note |
|--------|--------|------|
| **Error handling** | Most pages use `formatApiError` | **Good DRY**. |
| **Inconsistency** | `PlanReview.jsx` initial load | `.catch(() => setError("No se pudo cargar el plan."))` — **does not** use `formatApiError`, unlike `PlanSources` / `Chunks` / `Dashboard`. |

---

## Other inconsistencies (quality / maintainability)

1. **`GET /rag/intake/{patient_id}`** — confirm whether omitting auth on read is **intentional** (privacy) or oversight vs writes that require clinician/admin.
2. **`list_chunks`** — **no** `require_roles`; may be intentional for admin tooling; document or align with product policy.
3. **`PlanReview` load error** — generic string hides API **status/body** detail; inconsistent with the rest of the app’s error UX.

---

## Suggested order of work (if you refactor)

1. **Extract LLM exception → HTTP** from `generate_plan` (biggest DRY + readability win).
2. **Split `rag.py`** into domain routers + `include_router` (biggest SRP win).
3. **Unify analytics `ValueError` handling** (small, quick).
4. **`PlanReview`** — use `formatApiError` on initial fetch.
5. **Optional deeper D** — inject `Settings` / pipeline collaborators where tests need finer control.

---

## Related paths (for implementers)

- Backend: `backend/app/api/rag.py`, `backend/app/api/deps.py`, `backend/app/rag/*`, `backend/app/services/chunk_query.py`, `backend/app/services/plan_persistence.py`
- Frontend: `frontend/src/pages/PlanReview.jsx`, `frontend/src/utils/apiErrors.js`
