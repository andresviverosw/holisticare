# Current Context

## Ongoing Tasks

- **Final delivery planning complete (pending user lock on D1–D4):** see `docs/final-delivery-plan.md` and `docs/sprint-16.md`.
- Primary code story: **US-PRIV-001** (anonymize/pseudonymize before LLM egress).
- Companion Must tracks: Phase 1 FR/NFR fill, Phase 3 privacy dictionary, RAG eval short report, demo package, clinician feedback artifact.

## Known Issues

- Replace `api.example.com` in `Caddyfile` before first LE issue.
- SPA static host (`US-OPS-SPA-HOST`) still needed for a full public pilot — **cut from final delivery window** unless tutor requires a public URL.
- Phase 3 privacy doc and Phase 1 §7 FR/NFR tables are still stubs (academic DoD gap).
- Raw intake JSON + `patient_id` can still reach Claude/OpenAI (R-02).

## Next Steps

1. User confirms final-delivery decisions D1–D4.
2. Development: US-PRIV-001 TDD (scrubber + pipeline choke point).
3. Planning: DOC-CLOSE Phase 3 + FR/NFR in parallel.
4. QA: anonymization + regression + demo smoke; then package/tag.
