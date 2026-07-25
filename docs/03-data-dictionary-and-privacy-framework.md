# Phase 3 - Data Dictionary and Privacy Framework

## Document control

- Owner: Andrés Viveros
- Contributors: Planning / Development agents
- Version: 1.0 (final-delivery closeout)
- Last updated: 2026-07-25
- Status: `[x]` Complete (MVP scope; synthetic-data pilot)

## 1. Objective

Define canonical data entities, field-level semantics, quality rules, and privacy controls required for compliant and safe operation of HolistiCare MVP.

## 2. Data domains

- Patient profile and demographics (UUID + intake JSON)
- Clinical intake and baseline assessments
- Session records and interventions
- Daily symptom and wellbeing diary
- AI recommendations and source traceability
- Outcomes and longitudinal metrics
- Auth users and diary invites
- Knowledge corpus chunks (non-PHI)

## 3. Data dictionary (core entities)

| Entity | Field | Type | Allowed values / format | Required | Source | Notes |
|--------|-------|------|-------------------------|----------|--------|-------|
| Patient (logical) | patient_id | UUID | UUIDv4 | Yes | System / clinician | Primary key across intake, plans, sessions, diary |
| IntakeProfile | intake_json | JSONB | `generic_holistic_v0` | Yes | Clinician | See schema below |
| IntakeProfile | practitioner_id | UUID | UUIDv4 | No | System | Optional attribution |
| IntakeAudit | before_json / after_json | JSONB | — | Yes | System | Admin PATCH trail |
| IntakeAudit | actor_sub | text | JWT `sub` | Yes | Auth | Who changed intake |
| TreatmentPlan | status | text | pending_review / approved / rejected / active | Yes | System | AI drafts start pending_review |
| TreatmentPlan | plan_json | JSONB | Plan contract | Yes | RAG + clinician | Includes citations, weeks, flags |
| TreatmentPlan | citations_used | text[] | REF-* | No | RAG | Traceability |
| CareSession | session_json | JSONB | Structured log | Yes | Clinician | Interventions + observations |
| DiaryEntry | entry_date | date | ISO date | Yes | Patient/clinician | UNIQUE (patient_id, entry_date) |
| DiaryEntry | diary_json | JSONB | `patient_diary_v0` | Yes | Patient/clinician | Scores 0–10 |
| DiaryInvite | token_hash | varchar(64) | SHA-256 hex | Yes | System | Plaintext token shown once |
| DiaryInvite | expires_at / redeemed_at | timestamptz | — | Yes / No | System | Single-use |
| AppUser | username / password_hash / role | — | clinician\|admin | Yes | Seed/admin | Prod clinician login |
| PlanMemoryBank | snapshot_json | JSONB | De-identified plan | Yes | Clinician | No patient_id in snapshot |
| ClinicalChunk | embedding | vector(1536) | — | Yes | Ingest | Non-PHI corpus |
| ClinicalChunk | ref_id | text | REF-… | Yes | Ingest | Citation id |

### 3.1 Intake schema (`generic_holistic_v0`)

| Field | Type | PII class | Sent to LLM after US-PRIV-001 |
|-------|------|-----------|-------------------------------|
| profile_version | literal | Operational | Yes |
| demographics.age_range / sex_at_birth | optional strings | Quasi-identifier | Yes (scrubbed free-text only) |
| chief_complaint | string | Clinical (+ possible free-text PII) | Yes (redacted) |
| conditions / goals | string[] | Clinical | Yes (redacted) |
| contraindications / allergies / medications | string[] | Clinical sensitive | Yes (redacted) |
| baseline_outcomes | object | Clinical | Yes (redacted notes) |
| psychosocial_summary | string | Clinical sensitive | Yes (redacted) |
| prior_interventions_tried | string[] | Clinical | Yes (redacted) |
| patient_id (API layer) | UUID | Identifier | **Never** in LLM prompt |

## 4. Data quality rules

- Completeness: intake requires chief_complaint + ≥1 condition + ≥1 goal.
- Validity: diary scores integer 0–10; UUIDv4 for patient_id on UI; Pydantic on API.
- Uniqueness: one intake row per patient_id; one diary row per (patient_id, entry_date); invite token_hash unique.
- Timeliness: diary upsert by date; sessions ordered by occurred_at desc.
- Referential integrity: logical FK via patient_id UUID (no hard SQL FK across all tables in MVP).

## 5. Sensitive data classification

| Data class | Examples | Risk level | Protection controls |
|------------|----------|------------|---------------------|
| Clinical sensitive | conditions, meds, allergies, diary scores, plans | High | JWT RBAC; TLS in transit; DB access controls; practitioner gate |
| Personal identifiable | patient_id UUID; free-text names/emails/phones if pasted | High | Minimize collection; **US-PRIV-001** scrub before LLM; no name/email fields in v0 schema |
| Operational metadata | ingestion_log, ref_id, timestamps | Medium | Admin-gated ingest |
| Public/non-sensitive | UI copy, synthetic demo corpus docs | Low | Repo / Static Site |

## 6. Privacy framework (LFPDPPP aligned)

### 6.1 Legal basis and purpose limitation

- Purpose: clinical decision support for holistic rehab outpatient care; between-session diary; practitioner documentation.
- Data minimization: intake v0 omits name/email/phone fields; UUID patient identifiers; synthetic data in development/demo.

### 6.2 Consent management

- Capture mechanism: clinic process / avisos outside MVP UI (documented gap).
- Granularity: care + diary + AI-assisted planning (policy-level).
- Revocation: manual ARCO process (below); technical delete not fully automated in MVP.

### 6.3 Data subject rights (ARCO)

| Right | MVP handling |
|-------|----------------|
| Access | Clinician retrieves intake/plans/diary via API/UI for a patient_id |
| Rectification | Admin `PATCH /rag/intake/{id}` + audit trail |
| Cancellation | Manual DB purge by operator (runbook); not self-serve portal |
| Opposition | Stop AI generation / reject plans; disable diary invite |
| Response SLA | Organizational (clinic policy); not enforced in software |

### 6.4 Retention and deletion policy

| Data category | Retention period | Deletion method | Exception handling |
|---------------|------------------|-----------------|--------------------|
| Synthetic demo data | Duration of academic demo | Drop Render DB / recreate | N/A |
| Intake / plans / sessions / diary | Clinic policy (suggest ≥5 years clinical record norms) | Manual SQL delete by patient_id | Legal holds |
| Diary invites | Until expiry or redeem | Row overwrite redeemed_at; TTL | — |
| Memory bank snapshots | Until clinician removes | Delete bank row | Already de-identified |
| LLM vendor logs | Per vendor DPA / retention settings | Configure Zero Data Retention where available | See ops DPA checklist |

## 7. Security controls

- Encryption in transit: HTTPS (Render / Caddy TLS).
- Encryption at rest: managed Postgres provider defaults.
- Access control: JWT HS256; roles clinician/admin/patient; patient `sub` must match patient_id.
- Audit logging: intake_profile_audit; plan approval fields; ingestion_log.
- Key rotation: rotate `SECRET_KEY` / API keys via host env; invalidate sessions on SECRET_KEY change.

## 8. Compliance mapping

| Requirement | Control | Evidence artifact | Owner |
|------------|---------|-------------------|-------|
| NOM-024 human approval | Plans `pending_review`; approve/reject API/UI; no auto-activation | US-PLAN-003 tests; Plan Review | Product |
| NOM-024 unique patient id | UUIDv4 patient_id | US-INT-005 | Product |
| NOM-024 modification trail | intake_profile_audit | US-INT-003 API tests | Product |
| LFPDPPP minimization / transfer | **US-PRIV-001** anonymize before Claude/OpenAI; synthetic MVP data | `patient_anonymizer` tests; this doc | Product |
| LFPDPPP access control | JWT RBAC | auth + diary tests | Product |
| International transfer residual risk | DPAs + anonymization; legal Q1 still open for real PHI | Phase 1 Q1/R-02; deploy notes | Product / legal |

## 9. Open risks and mitigations

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| Free-text still may contain residual identifiers | Medium | Regex scrub + clinical projection; clinician guidance not to paste names | Dev |
| Render / US-region LLM processing | High for real PHI | Synthetic-only demo; anonymization; future legal/DPA | PO |
| ARCO not automated | Medium | Manual runbook; defer portal | PO |
| Cold-start free tier exposes long waits | Low | Document for TA | Ops |

## Completion checklist

- [x] Core entities and fields documented
- [x] Data quality rules defined
- [x] Sensitive data classified with controls
- [x] ARCO and consent flows specified (MVP-manual where needed)
- [x] Retention and deletion policy approved (MVP / synthetic scope)
