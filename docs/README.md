# HolistiCare Documentation Hub

This directory contains the six core documentation phases for the AI4devs master's project.

## Documentation map (by audience)

| Need | Start here |
|------|------------|
| Run the app locally, tests, Docker | `setup.md` |
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
| Sprint notes | `sprint-01.md` … `sprint-07.md` |
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
- `demo-smoke-checklist.md` - demo-day command checklist with expected outputs
- `07-user-guide.md` - clinician-facing usage guide for current MVP UI
- `08-developer-guide-and-architecture.md` - developer setup, module map, and mermaid diagrams
- `09-security-audit-and-todos.md` - security posture, scanner commands, completed remediation, and CI strict vs advisory mode

### CI security scans (advisory vs blocking)

GitHub Actions runs `pip-audit`, `bandit`, and `npm audit` in the `security-audit` job (see `.github/workflows/ci.yml`). By default this job is **blocking**: if any scanner fails, the workflow fails. To temporarily make it **advisory** (non-blocking) while triaging findings, set the repository variable **`SECURITY_AUDIT_ADVISORY=true`** (GitHub: repo **Settings → Secrets and variables → Actions → Variables**). Unset or set to anything other than `true` to restore strict behavior. Details and context live in `09-security-audit-and-todos.md`.

## Active sprint

- `sprint-01.md` - Sprint 1 (backend, US-PLAN-001, generic holistic intake v0)
- `sprint-02.md` - Sprint 2 (backend, US-INT-001 intake persistence/retrieval API slice)
- `sprint-03.md` - Sprint 3 (backend, US-SESS-001 structured session logging)
- `sprint-04.md` - Sprint 4 (backend, US-DIARY-001 patient diary check-ins)
- `sprint-05.md` - Sprint 5 (backend, US-ANLY-001 outcome trends from diary)
- `sprint-06.md` - Sprint 6 (backend, US-ANLY-002 plateau / worsening flags)
- `sprint-07.md` - Sprint 7 (planned: US-RAG-003 nutrition corpus, eat/avoid guidance in generated plans)

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
