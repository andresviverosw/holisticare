# HolistiCare Documentation Hub

This directory contains the six core documentation phases for the AI4devs master's project.

## Documentation map (by audience)

| Need | Start here |
|------|------------|
| Run the app locally, tests, Docker | `setup.md` |
| Clinician quick trial on Windows | `quickstart-clinician.md` |
| Pilot rehearsal checklist and synthetic cases | `pilot-rehearsal-checklist.md` |
| Pilot go/no-go decision gate | `pilot-go-no-go.md` |
| Pilot rehearsal run history template | `pilot-rehearsal-log.md` |
| Clinician pilot feedback template | `pilot-clinician-feedback-form.md` |
| Mobile app planning draft | `mobile-strategy-v0.md` |
| Release notes (high-level) | `CHANGELOG.md` (repository root) |
| Clinician / demo usage of the MVP UI | `07-user-guide.md` |
| Architecture, modules, env vars, diagrams | `08-developer-guide-and-architecture.md` |
| Diagrams (ER, flows, UML-style, Mermaid) | `10-solution-diagrams.md` |
| Phase 2 architecture narrative (links to diagrams) | `02-system-architecture.md` |
| Security scanners, remediation history, CI behavior | `09-security-audit-and-todos.md` |
| Demo commands and expected outputs | `demo-smoke-checklist.md` |
| Product requirements and stories | `01-` … `04-` phase docs |
| Test strategy | `05-test-plan.md` |
| Deployment and ops templates | `06-deployment-and-ops-runbook.md` (plus HolistiCare-specific notes inside) |
| Sprint notes | `sprint-01.md` … `sprint-10.md` |
| Project memory (Cursor MCP) | `memory-bank/README.md` at repository root |

## How to use

1. Complete each phase in order.
2. Keep decisions traceable with dates and owners.
3. Link artifacts across phases (for example, requirements -> architecture -> tests).
4. Mark each section with status:
   - `[ ]` Draft
   - `[~]` In progress
   - `[x]` Complete

## Documentation phases

1. `01-requirements-and-domain-research.md`
2. `02-system-architecture.md`
3. `03-data-dictionary-and-privacy-framework.md`
4. `04-feature-specs-and-user-stories.md`
5. `05-test-plan.md`
6. `06-deployment-and-ops-runbook.md`

## Operational docs

- `setup.md` - local environment setup, Docker startup, and health verification
- `quickstart-clinician.md` - clinician trial setup on Windows with Docker Desktop
- `pilot-rehearsal-checklist.md` - synthetic pilot runbook and pass/fail gate before clinician handoff
- `pilot-go-no-go.md` - explicit pre-pilot release criteria and no-go triggers
- `pilot-rehearsal-log.md` - reusable run log template with example entry
- `pilot-clinician-feedback-form.md` - structured clinician questionnaire for pilot sessions
- `mobile-strategy-v0.md` - phased mobile strategy, options, and starter US-MOB backlog
- `demo-smoke-checklist.md` - demo-day command checklist with expected outputs
- `scripts/run-ai-quality-smoke.bat` + `backend/scripts/ai_quality_smoke.py` - deterministic AI quality smoke gate for plan outputs
- `07-user-guide.md` - clinician-facing usage guide for current MVP UI
- `08-developer-guide-and-architecture.md` - developer setup, module map, and mermaid diagrams
- `09-security-audit-and-todos.md` - security posture, scanner commands, completed remediation, and CI strict vs advisory mode

### CI security scans (advisory vs blocking)

GitHub Actions runs `pip-audit`, `bandit`, and `npm audit` in the `security-audit` job (see `.github/workflows/ci.yml`). By default this job is **blocking**: if any scanner fails, the workflow fails. To temporarily make it **advisory** (non-blocking) while triaging findings, set the repository variable **`SECURITY_AUDIT_ADVISORY=true`** (GitHub: repo **Settings → Secrets and variables → Actions → Variables**). Unset or set to anything other than `true` to restore strict behavior. Details and context live in `09-security-audit-and-todos.md`.

### CI AI quality smoke (advisory vs blocking)

GitHub Actions runs `backend/scripts/ai_quality_smoke.py` in the `ai-quality-smoke` job. By default this job is **blocking**. To temporarily make it **advisory** while tuning thresholds, set repository variable **`AI_QUALITY_SMOKE_ADVISORY=true`**. Keep repository secret **`OPENAI_API_KEY`** configured for embeddings-backed plan generation in CI. The workflow ingests `backend/data/ci_smoke` before running AI smoke; if `OPENAI_API_KEY` is missing, ingestion/smoke steps are skipped with a warning.

## Active sprint

- **Current:** _TBD (Planning Agent)_ — next candidate: **US-PRED-001** / **US-PRED-002** or hardening (migrations, E2E).
- **Recently completed:** [`sprint-10.md`](sprint-10.md) — Sprint 10 (US-PLAN-004 memory bank); [`sprint-09.md`](sprint-09.md) — Sprint 9 (US-INT-005).

### Sprint history (reference)

- `sprint-01.md` - Sprint 1 (backend, US-PLAN-001, generic holistic intake v0)
- `sprint-02.md` - Sprint 2 (backend, US-INT-001 intake persistence/retrieval API slice)
- `sprint-03.md` - Sprint 3 (backend, US-SESS-001 structured session logging)
- `sprint-04.md` - Sprint 4 (backend, US-DIARY-001 patient diary check-ins)
- `sprint-05.md` - Sprint 5 (backend, US-ANLY-001 outcome trends from diary)
- `sprint-06.md` - Sprint 6 (backend, US-ANLY-002 plateau / worsening flags)
- `sprint-07.md` - Sprint 7 (US-RAG-003 nutrition corpus, eat/avoid guidance in generated plans)
- `sprint-08.md` - Sprint 8 (US-RAG-004 config-driven nutrition safety dictionaries) — **complete**
- `sprint-09.md` - Sprint 9 (US-INT-005 automatic patient UUID + recent patients) — **complete**
- `sprint-10.md` - Sprint 10 (US-PLAN-004 approved plan memory bank) — **complete**

## Suggested cadence

- Weekly: review priorities, open decisions, and risks
- Biweekly: clinical feedback validation checkpoint
- Monthly: technical architecture and compliance review

## Definition of done (full documentation set)

- All six phase documents are complete and internally consistent
- Key architecture decisions are justified and linked to requirements
- Compliance controls are documented and mapped to implementation
- Test plan covers functional, AI quality, and safety checks
- Deployment and incident procedures are practical and testable
