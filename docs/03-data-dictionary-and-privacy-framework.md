# Phase 3 - Data Dictionary and Privacy Framework

## Document control

- Owner: Andrés V (product owner / architect)
- Contributors: Planning + Development agents (capstone closeout)
- Version: 1.0
- Last updated: 2026-07-26
- Status: `[x]` Complete (academic closeout — synthetic-data deployment; not legal advice)

## 1. Objective

Define canonical data entities, field-level semantics, quality rules, and privacy controls required for compliant and safe operation of HolistiCare as a clinical decision-support platform under NOM-024-SSA3-2012 and LFPDPPP-aligned practices.

## 2. Data domains

- Patient profile and demographics (minimized; UUID-centric)
- Clinical intake and baseline assessments
- Session records and interventions
- Daily symptom and wellbeing diary (+ invite tokens)
- AI recommendations, citations, and approval lifecycle
- Outcomes, plateau flags, and recovery predictions
- Knowledge corpus (non-PHI clinical chunks)
- Auth identities (`app_users`, JWT claims)

## 3. Data dictionary

| Entity | Field | Type | Allowed values / format | Required | Source | Notes |
|--------|-------|------|-------------------------|----------|--------|-------|
| Patient (logical) | patient_id | UUID | UUIDv4 | Yes | System / clinician | Primary subject key across tables |
| IntakeProfile | intake_json | JSONB | `generic_holistic_v0` schema | Yes | Clinician | No name/email fields in schema |
| IntakeProfile | practitioner_id | UUID | UUIDv4 | No | Clinician | Optional attribution |
| IntakeAudit | before_json / after_json | JSONB | Intake snapshots | Yes | System | US-INT-003 trail |
| TreatmentPlan | status | TEXT | `pending_review` \| `approved` \| `rejected` \| `active` | Yes | System | AI drafts start `pending_review` |
| TreatmentPlan | plan_json | JSONB | Plan schema + citations | Yes | RAG + clinician | Includes `requires_practitioner_review` |
| CareSession | session_json | JSONB | `ClinicalSessionLogV0` | Yes | Clinician | Visit log |
| DiaryEntry | entry_date | DATE | ISO date | Yes | Patient/clinician | UNIQUE(patient_id, entry_date) |
| DiaryEntry | diary_json | JSONB | `PatientDiaryCheckinV0` | Yes | Patient/clinician | Pain/sleep/mood/function |
| DiaryInvite | token_hash | VARCHAR(64) | SHA-256 hex | Yes | System | Plaintext only in one-time URL |
| DiaryInvite | expires_at / redeemed_at | TIMESTAMPTZ | UTC | Yes / No | System | Single-use redeem |
| AppUser | username / password_hash | TEXT | bcrypt | Yes | Admin seed | Clinician/admin only |
| AppUser | role | TEXT | `clinician` \| `admin` | Yes | Admin | Patients use JWT `sub`=UUID, not this table |
| ClinicalChunk | embedding | VECTOR(1536) | OpenAI embedding | Yes | Ingestion | Non-patient corpus |
| ClinicalChunk | ref_id | TEXT | `REF-…` | Yes | Ingestion | Citation key |
| MemoryBank | snapshot_json | JSONB | De-identified plan | Yes | Clinician | `patient_id` stripped (US-PLAN-004) |

Intake clinical fields (inside `intake_json`): `profile_version`, `demographics` (age_range, sex_at_birth), `chief_complaint`, `conditions[]`, `goals[]`, `contraindications[]`, `current_medications[]`, `allergies[]`, `baseline_outcomes`, `psychosocial_summary`, `prior_interventions_tried[]`.

## 4. Data quality rules

- Completeness: intake requires non-empty `chief_complaint`, `conditions`, `goals`; diary day uniqueness enforced in DB.
- Validity: Pydantic `_v0` schemas on API write paths; evidence_level / language CHECKs on chunks.
- Uniqueness: `intake_profiles.patient_id`; diary `(patient_id, entry_date)`; `clinical_chunks.ref_id`; invite `token_hash`.
- Timeliness: diary invites expire; JWT `exp` on patient/clinician production auth.
- Referential integrity: application-level binding of plans/sessions/diaries to `patient_id` (UUID); memory bank references `source_plan_id`.

## 5. Sensitive data classification

| Data class | Examples | Risk level | Protection controls |
|------------|----------|------------|---------------------|
| Clinical sensitive | Intake free text, diary scores/notes, session notes, plans | High | JWT RBAC; practitioner review; no public listing APIs |
| Personal identifiable | `patient_id` UUID, invite URLs, usernames | High | UUID pseudonyms; invite hash-at-rest; egress scrub (US-PRIV-001) |
| Operational metadata | ingestion_log, retrieval_metadata, audit actor_sub | Medium | Admin/clinician roles; avoid PII in logs |
| Public/non-sensitive | Clinical guideline PDFs in corpus, REF-IDs | Low | Still access-controlled for ops integrity |

## 6. Privacy framework (LFPDPPP aligned)

### 6.1 Legal basis and purpose limitation

- Purpose statements: continuity of care, CDS plan drafting, outcome tracking for holistic rehab clinics; capstone demo uses **synthetic patients only**.
- Data minimization policy: intake schema omits name/email/phone; LLM egress uses clinical projection + redaction (`app/services/patient_anonymizer.py`, US-PRIV-001). Local DB keeps UUID keys for care linkage (pseudonymization at egress, not erasure).

### 6.2 Consent management

- Capture mechanism: clinic-operated process / avisos de privacidad (policy documented; no in-app consent portal in MVP).
- Granularity: treatment of clinical data for care + optional use of de-identified templates in memory bank.
- Revocation handling: manual admin process (see ARCO); disable invites; reject further generation for subject.

### 6.3 Data subject rights (ARCO)

- Access: clinician exports via existing GET intake/plan/diary APIs for a `patient_id` (manual package).
- Rectification: `PATCH /rag/intake/{patient_id}` with audit trail.
- Cancellation: manual SQL/admin deletion across subject tables (automation deferred).
- Opposition: stop processing / disable invites; document in clinic SOP.
- Response SLA: clinic policy target ≤ 20 business days (LFPDPPP-oriented; not automated).

### 6.4 Retention and deletion policy

| Data category | Retention period | Deletion method | Exception handling |
|---------------|------------------|-----------------|--------------------|
| Synthetic demo data | Duration of capstone + 90 days | Drop/reseed DB | N/A |
| Clinical operational (future real PHI) | Per clinic NOM-024 retention | Manual purge runbook | Legal hold |
| Diary invites | Until expiry or redeem | Row delete / expire | Audit of creator sub |
| Memory bank snapshots | Until clinician deletes | API/DB delete | Already de-identified |
| Auth passwords | While account active | bcrypt hash only; deactivate user | — |

## 7. Security controls

- Encryption at rest: managed Postgres (Render/host) disk encryption; app does not store LLM API keys in DB.
- Encryption in transit: TLS (Caddy prod Compose / Render HTTPS).
- Access control model: JWT HS256 claims `sub` + `role`; `require_roles`; diary subject `sub == patient_id`.
- Audit logging: `intake_profile_audit`; plan approval timestamps/`approved_by`.
- Key rotation policy: rotate `SECRET_KEY` and provider API keys via host secrets; invalidate outstanding JWTs on rotation.

## 8. Compliance mapping

| Requirement | Control | Evidence artifact | Owner |
|------------|---------|-------------------|-------|
| NOM-024 practitioner gate | `requires_practitioner_review: true`; status lifecycle | Generator prompt + approve/reject API + tests | Dev |
| NOM-024 traceability | Intake audit + plan persistence | `intake_profile_audit`, `treatment_plans` | Dev |
| LFPDPPP minimization / international transfer | US-PRIV-001 LLM egress scrub + synthetic-only demo | `patient_anonymizer.py`, tests, this doc | Dev / PO |
| LFPDPPP ARCO | Manual process (no full portal) | §6.3 above | Clinic / PO |
| Corpus ≠ PHI | Ingest clinical literature only | `clinical_chunks`, ingestion admin gate | Admin |

## 9. Open risks and mitigations

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| Residual free-text identifiers bypass regex scrub | PHI leak to model vendor | Fail-closed `assert_egress_safe`; expand patterns; US-PRIV-002 for memory bank | Dev |
| Legal Q1 (cross-border LLM) not fully closed | Compliance claim overstated | Document control + residual legal review required before real PHI | PO / counsel |
| `ALLOW_DEV_AUTH=true` on demo host | Auth bypass risk | Demo-only; seed clinician path documented; never for real PHI | Ops |
| Free-tier cold starts | Demo UX | Document ~50s+ in deploy notes | Ops |

## Completion checklist

- [x] Core entities and fields documented
- [x] Data quality rules defined
- [x] Sensitive data classified with controls
- [x] ARCO and consent flows specified (manual policy OK for MVP)
- [x] Retention and deletion policy approved (capstone / synthetic scope)
