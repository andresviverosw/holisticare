# HolistiCare Documentation Hub

This directory contains the six core documentation phases for the AI4devs master's project.

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

## Active sprint

- `sprint-01.md` - Sprint 1 (backend, US-PLAN-001, generic holistic intake v0)
- `sprint-02.md` - Sprint 2 (backend, US-INT-001 intake persistence/retrieval API slice)
- `sprint-03.md` - Sprint 3 (backend, US-SESS-001 structured session logging)
- `sprint-04.md` - Sprint 4 (backend, US-DIARY-001 patient diary check-ins)
- `sprint-05.md` - Sprint 5 (backend, US-ANLY-001 outcome trends from diary)

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
