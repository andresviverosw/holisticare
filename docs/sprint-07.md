# Sprint 7 — Knowledge base + plans: US-RAG-003 (nutrition corpus, eat/avoid guidance)

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | 1–2 weeks (estimate **M**) |
| Primary story | [US-RAG-003](04-feature-specs-and-user-stories.md) (section **US-RAG-003**) |
| Scope | Corpus ingest + retrieval tagging, plan generation contract (eat/avoid), citations, contraindication guardrails, pytest |
| Owner | _TBD (Planning Agent assigns)_ |
| E2E | Deferred (optional smoke: generate + verify sections in UI) |

## Dependencies

- **US-RAG-002** — curated corpus path and ingest verification (operational baseline).
- **US-PLAN-002** — citation traceability (REF-IDs on nutrition lines).

## Goal

Add nutrition evidence to the RAG corpus so draft treatment plans include **what to eat** and **what to avoid**, grounded in retrieved sources and aligned with the patient profile (conditions, goals, contraindications/allergies where captured).

## Today execution plan (kickoff)

### Confirmed inputs

- Nutrition corpus source path (provided): `C:\Users\andre\OneDrive\Documentos\Andres\AI4devs\holisticare\corpus_pdfs\rehab_nutrition_corpus`
- Current files detected in that folder: `main.pdf` (can expand later with more PDFs).

### Work blocks for today

- [x] **Planning lock:** freeze v1 contract (`eat` / `avoid`, citation required per recommendation, contraindication guard).
- [x] **TDD block 1 (ingestion/retrieval):** write failing tests for nutrition chunk tagging/filtering, then implement minimal ingestion metadata support.
- [x] **TDD block 2 (generation):** write failing contract tests for nutrition sections in generated plan payload, then implement prompt/output changes.
- [x] **TDD block 3 (safety):** write failing tests for allergy/contraindication conflicts, then implement post-generation guard.
- [x] **Regression + QA:** run plan/citation/approval regressions and capture pass/fail evidence in this sprint note.

### Definition of done for today

- [x] Nutrition corpus path is documented and used by ingest workflow.
- [x] Backend tests for nutrition retrieval + generation + safety are green.
- [x] No regression in existing citation/approval behavior.
- [x] Handoff note added (scope done, tests run, open risks).

## Planned deliverables

- [x] Stable nutrition corpus location (e.g. `backend/data/corpus/nutrition/`) documented; licensing/provenance noted in ops/research appendix as needed.
- [x] Ingestion indexes nutrition sources; chunk metadata supports nutrition topic (and optional subtopics) for targeted recall.
- [x] Plan generation prompt + output shape include normalized nutrition sections (`eat` / `avoid` or equivalent) without breaking existing plan consumers.
- [x] Each nutrition bullet carries citation REF-IDs where claims are made; insufficiency stated when evidence is thin.
- [x] Post-generation rule check: flag or block obvious conflicts with profile contraindications/allergies before clinician approval path.
- [x] Automated tests: unit (validator, retrieval filters), integration (`POST /rag/plan/generate` scenarios), regression on existing plan/citation tests.

## Test evidence (target)

- New/updated tests under `backend/tests/` for nutrition retrieval, plan payload shape, and conflict rules.
- Full backend suite green before merge.

## Test evidence (today)

- `python -m pytest -q backend/tests/test_nutrition_ingestion.py backend/tests/test_html_ingestion.py` -> **7 passed**.
- `python -m pytest -q backend/tests/test_rag.py` -> **15 passed**.
- `python -m pytest -q backend/tests/test_plan_generate_api.py` -> **39 passed**.
- `python -m pytest -q backend/tests/test_plan_generate_api.py backend/tests/test_nutrition_ingestion.py backend/tests/test_html_ingestion.py` -> **46 passed**.

## Operational ingest + smoke evidence (real corpus)

- **Docker status:** backend/db/frontend running (`docker compose ps`).
- **Corpus staged for ingestion:** copied PDFs into `backend/data/corpus/nutrition/` from `C:\Users\andre\OneDrive\Documentos\Andres\AI4devs\holisticare\corpus_pdfs\rehab_nutrition_corpus` (13 PDFs detected in target folder).
- **Container ingestion command:**  
  `docker compose exec backend env PYTHONPATH=/app python scripts/run_corpus_ingest.py --source-dir data/corpus/nutrition --force-reindex`
- **Ingestion result notes:** embeddings were successfully requested/stored (multiple OpenAI `200 OK` calls observed). One file (`main.pdf`) was skipped due to invalid PDF header/EOF warnings.
- **Chunk API smoke (topic filter):**  
  `GET /rag/chunks?topic=nutrition&limit=5` returned `200` with non-empty `items`; sample rows included `topic: ["nutrition"]`, valid `ref_id`, and source files such as `GuiaAlimentacion.pdf`.
- **Plan generation smoke (JWT clinician token):**
  - `POST /rag/plan/generate` returned `200`.
  - Response included `diet_recommendations.eat` and `diet_recommendations.avoid`, `citations_used`, and `insufficient_evidence: false`.
  - Additional smoke with allergy constraint triggered `nutrition_safety_flags` and removed blocked diet entries as expected.

## Handoff note (today)

- **Story ID:** US-RAG-003
- **Scope completed today:**
  - Nutrition corpus kickoff path documented and validated.
  - Ingestion metadata now tags nutrition chunks (`topic=["nutrition"]`) for retrieval targeting.
  - Plan generation contract now supports `diet_recommendations.eat/avoid` with citation normalization.
  - Safety guard implemented in pipeline to block diet entries that match intake contraindications/allergies and emit `nutrition_safety_flags`.
- **Acceptance criteria coverage (today):**
  - Nutrition metadata indexing: covered by new ingestion tests.
  - Eat/avoid output contract + citations: covered by updated RAG tests.
  - Conflict handling (blocked or flagged): covered by safety unit tests and pipeline integration test.
  - Regression stability: plan API + ingestion regression suites green.
- **Open risks / follow-ups:**
  - Safety matching is now token + synonym based; still requires clinician review and periodic synonym list calibration for edge cases.
  - Topic tagging is heuristic (`text` + filename); optional future improvement via structured taxonomy tagger.

## Risks / follow-ups

- Clinical review of thresholds for “insufficient evidence” vs general healthy-eating boilerplate.
- i18n: Spanish UX for eat/avoid labels if UI surfaces them explicitly.
- Deeper diet personalization (calories, macros) out of scope unless profile fields exist — document boundary in story notes.
