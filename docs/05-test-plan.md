# Phase 5 - Test Plan

## Document control

- Owner:
- Contributors:
- Version:
- Last updated:
- Status: `[ ]` Draft `[~]` In progress `[x]` Complete

## 1. Objective

Define how HolistiCare will be verified for functional correctness, AI quality, safety constraints, and operational reliability.

## 2. Test strategy

- Shift-left testing from feature design
- Automated tests for critical flows
- Human evaluation for clinical relevance and AI outputs
- Regression checks before each release

## 3. Test levels

| Level | Scope | Owner | Tooling |
|-------|-------|-------|---------|
| Unit |  |  |  |
| Integration |  |  |  |
| API contract |  |  |  |
| End-to-end |  |  |  |
| AI evaluation |  |  |  |
| Security and privacy |  |  |  |

## 4. Test environments

- Local development:
- Staging:
- Pre-production:
- Test data approach:

## 5. Functional test scenarios

| Scenario ID | Feature | Preconditions | Steps | Expected result |
|-------------|---------|---------------|-------|-----------------|
| TS-001 | Intake |  |  |  |
| TS-002 | Treatment plan |  |  |  |
| TS-003 | Session logger |  |  |  |
| TS-004 | Diary |  |  |  |
| TS-005 | Analytics |  |  |  |

## 6. AI quality and safety tests

### 6.1 RAG quality

- Retrieval precision@k: tracked operationally via `retrieval_metadata` in generated plans (`candidates_retrieved`, `chunks_passed_to_llm`), reviewed in smoke output.
- Groundedness check: baseline deterministic gate in `backend/scripts/ai_quality_smoke.py` (fails when `insufficient_evidence=true` or plan contract is broken).
- Citation correctness: deterministic checks ensure `citations_used` is list-typed and non-empty at suite level (`--require-any-citations`), with optional strict per-case enforcement (`--require-case-citations`).

### 6.2 Clinical safety checks

- Contraindication detection coverage:
- Hallucination policy and thresholds:
- Practitioner override validation:

### 6.3 Prompt and output contract tests

- JSON schema compliance: validated through backend response contract checks in `ai_quality_smoke.py` and API tests.
- Required fields presence: `plan_id`, `status`, `weeks`, `insufficient_evidence`, and `citations_used` are verified by smoke runner.
- Deterministic validation where possible: `scripts/run-ai-quality-smoke.bat` executes repeatable AI quality gates against synthetic pilot cases.

## 7. Non-functional testing

- Performance and load:
- Reliability and recovery:
- Security testing:
- Privacy and access control tests:

## 8. Traceability matrix

| Requirement ID | Test case ID | Type | Status |
|----------------|--------------|------|--------|
| FR-01 | TS-001 | Functional |  |
| NFR-01 | NFT-001 | Performance |  |

## 9. Defect management

- Severity levels:
- Triage process:
- SLA by severity:
- Exit criteria:

## 10. Release quality gates

- Must-pass suites:
- Coverage threshold:
- Critical defect threshold:
- Manual sign-off requirements:

## Completion checklist

- [ ] Requirements mapped to test cases
- [ ] AI quality metrics defined
- [ ] Safety and hallucination tests defined
- [ ] Release gates agreed
