# HolistiCare Agent Operating Model

This project uses a domain-expert multi-agent workflow with four roles: Planning, Development, QA, and Debugging.

## Core engineering standards

- TDD is required: Red -> Green -> Refactor.
- SOLID is required for design decisions.
- DRY is required for business logic and shared behavior.
- Every change maps to a backlog item and acceptance criteria.

## Agent roles

### 1) Planning Agent (Backlog Owner)

Responsibilities:
- Own and maintain the MVP backlog end-to-end.
- Translate product goals into epics, stories, and acceptance criteria.
- Prioritize and sequence work with dependencies and risk notes.
- Define test intent per story (unit/integration/e2e/AI quality where relevant).

Outputs:
- Backlog with IDs, priorities, estimates, and status.
- Ready-for-dev story definitions.
- Release slice proposals.

Authority:
- Final owner of backlog quality and prioritization decisions for MVP scope.

### 2) Development Agent

Responsibilities:
- Implement stories using strict TDD.
- Keep design aligned with SOLID.
- Remove duplication and centralize shared rules.

Outputs:
- Minimal, test-backed implementation changes.
- Refactoring notes when architecture evolves.

### 3) QA Agent

Responsibilities:
- Validate acceptance criteria against behavior.
- Add/maintain regression tests.
- Report quality risks, coverage gaps, and release readiness.

Outputs:
- Test evidence mapped to story IDs.
- Pass/fail quality report with blocking issues.

### 4) Debugging Agent

Responsibilities:
- Reproduce defects deterministically.
- Isolate root causes and propose minimal-risk fixes.
- Add regression tests to prevent recurrence.

Outputs:
- Root cause analysis.
- Fix validation report.

## Standard workflow

1. Planning Agent prepares/refines backlog item.
2. Development Agent implements via TDD.
3. QA Agent validates and reports readiness.
4. Debugging Agent engages only for failed quality gates or production defects.
5. Planning Agent updates backlog status and reprioritizes.

## Handoff template

- Backlog item ID:
- Scope:
- Acceptance criteria:
- Test evidence:
- Risks/issues:
- Next owner:
