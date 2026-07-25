# Sprint 16 — Final delivery: US-PRIV-001 (patient anonymization) + capstone closeout

## Sprint parameters

| Field | Value |
|-------|--------|
| Length | Capstone closeout slice (privacy code + academic packaging) |
| Primary story | **US-PRIV-001** |
| Companion tracks | DOC-CLOSE-01..03, EVAL-01, DEMO-01, FEEDBACK-01 |
| Priority | Must (final master’s delivery) |
| Scope | LLM egress anonymization/pseudonymization; privacy docs; submission package |
| Owner | Planning → Development (TDD) → QA |
| Status | **Ready for confirmation / then Ready for dev** |
| Plan of record | [`final-delivery-plan.md`](final-delivery-plan.md) |

## Problem statement

HolistiCare’s MVP product loop is implemented through Sprint 15, but Phase 1 risk **R-02** (LFPDPPP × international LLM APIs) is still open: intake JSON and `patient_id` can reach Claude/OpenAI without an anonymization layer. The master’s DoD also requires completed academic documentation (FR/NFR, privacy framework) and demo evidence — currently the largest submission risk.

## Why this slice

| Candidate | Decision |
|-----------|----------|
| **US-PRIV-001** | **Selected** — closes R-02 control gap called out since Phase 1 |
| Phase 3 privacy + FR/NFR fill | **Selected** — academic DoD blocker |
| R4 mobile / SPA host / JWT harden | **Cut** — see final-delivery-plan Track C |
| Full ARCO automation | **Out of scope** — document manual process only |

## Planning decisions (locked pending D1–D4 confirmation)

1. Anonymize at **egress** (before `complete_claude_or_openai`); keep DB UUIDs locally.
2. Single choke point in `RAGPipeline.generate_plan` preferred.
3. TDD mandatory: redact fixtures + mock LLM call assertions.
4. Docs land in the same PR series as code (Phase 3 + backlog status).
5. No mobile/PWA work in this sprint.

## Ready-for-dev checklist

- [x] Story ID, AC, test intent in [`04-feature-specs-and-user-stories.md`](04-feature-specs-and-user-stories.md)
- [x] Sequence and cut list in [`final-delivery-plan.md`](final-delivery-plan.md)
- [ ] User confirms open decisions D1–D4
- [ ] Development starts Red tests for scrubber

## Handoff

- Backlog item ID: **US-PRIV-001** (+ DOC-CLOSE / EVAL / DEMO companions)
- Scope: Final delivery plan §3 Track A
- Acceptance criteria: US-PRIV-001 AC + final DoD checklist §7 in plan
- Test evidence: pending Development/QA
- Risks/issues: over-scrubbing clinical text; residual legal Q1
- Next owner: **User (confirm D1–D4)** → Development Agent
