# Phase 3 - Data Dictionary and Privacy Framework

## Document control

- Owner:
- Contributors:
- Version:
- Last updated:
- Status: `[ ]` Draft `[~]` In progress `[x]` Complete

## 1. Objective

Define canonical data entities, field-level semantics, quality rules, and privacy controls required for compliant and safe operation.

## 2. Data domains

- Patient profile and demographics
- Clinical intake and baseline assessments
- Session records and interventions
- Daily symptom and wellbeing diary
- AI recommendations and source traceability
- Outcomes and longitudinal metrics

## 3. Data dictionary

| Entity | Field | Type | Allowed values / format | Required | Source | Notes |
|--------|-------|------|-------------------------|----------|--------|-------|
| Patient | patient_id | UUID | UUIDv4 | Yes | System | Primary key |
| Patient | consent_status | Enum | granted / revoked / pending | Yes | User | Consent lifecycle |

Add all fields used by backend, frontend, analytics, and ML pipelines.

## 4. Data quality rules

- Completeness rules:
- Validity rules:
- Uniqueness rules:
- Timeliness rules:
- Referential integrity rules:

## 5. Sensitive data classification

| Data class | Examples | Risk level | Protection controls |
|------------|----------|------------|---------------------|
| Clinical sensitive |  | High |  |
| Personal identifiable |  | High |  |
| Operational metadata |  | Medium |  |
| Public/non-sensitive |  | Low |  |

## 6. Privacy framework (LFPDPPP aligned)

### 6.1 Legal basis and purpose limitation

- Purpose statements:
- Data minimization policy:

### 6.2 Consent management

- Capture mechanism:
- Granularity:
- Revocation handling:

### 6.3 Data subject rights (ARCO)

- Access:
- Rectification:
- Cancellation:
- Opposition:
- Response SLA:

### 6.4 Retention and deletion policy

| Data category | Retention period | Deletion method | Exception handling |
|---------------|------------------|-----------------|--------------------|
|  |  |  |  |

## 7. Security controls

- Encryption at rest:
- Encryption in transit:
- Access control model:
- Audit logging:
- Key rotation policy:

## 8. Compliance mapping

| Requirement | Control | Evidence artifact | Owner |
|------------|---------|-------------------|-------|
| NOM-024 |  |  |  |
| LFPDPPP |  |  |  |

## 9. Open risks and mitigations

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
|  |  |  |  |

## Completion checklist

- [ ] Core entities and fields documented
- [ ] Data quality rules defined
- [ ] Sensitive data classified with controls
- [ ] ARCO and consent flows specified
- [ ] Retention and deletion policy approved
