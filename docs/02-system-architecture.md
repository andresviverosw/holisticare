# Phase 2 - System Architecture

## Document control

- Owner:
- Contributors:
- Version:
- Last updated:
- Status: `[ ]` Draft `[~]` In progress `[x]` Complete

## 1. Objective

Define the end-to-end architecture for HolistiCare, including application layers, AI pipeline, data flow, and governance controls.

## 2. Architecture principles

- Practitioner-in-the-loop by default
- Traceability for every AI recommendation
- Privacy and security by design
- Modular services for phased delivery
- Observable and testable AI behavior

## 3. Context diagram (C4 - Level 1)

- System boundary:
- External actors:
- External systems:

## 4. Container architecture (C4 - Level 2)

| Container | Responsibility | Tech | Inputs | Outputs |
|-----------|----------------|------|--------|---------|
| Frontend |  |  |  |  |
| API backend |  |  |  |  |
| RAG services |  |  |  |  |
| Relational DB |  |  |  |  |
| Vector index |  |  |  |  |
| Model services |  |  |  |  |

## 5. Core workflows

### 5.1 Intake to treatment plan

1. 
2. 
3. 

### 5.2 Session logging and analytics update

1. 
2. 
3. 

### 5.3 Patient diary ingestion

1. 
2. 
3. 

## 6. RAG architecture detail

### 6.1 Offline ingestion

- Source types:
- Chunking strategy:
- Metadata schema:
- Embedding process:

### 6.2 Query construction

- Profile summarization:
- Multi-query expansion:

### 6.3 Retrieval and reranking

- Top-k policy:
- Filtering strategy:
- Reranker policy:

### 6.4 Prompt and generation

- Prompt template controls:
- Contraindication requirements:
- Output schema contract:

### 6.5 Approval and persistence

- Approval gate states:
- Audit events:
- Source traceability:

## 7. Data architecture

- Transactional schema overview:
- Analytical schema overview:
- Data lifecycle and retention:

## 8. Security and privacy architecture

- Authentication and authorization model:
- Encryption in transit and at rest:
- Key management approach:
- Consent and access logging:

## 9. Reliability and operations

- Availability targets:
- Backup and restore:
- Failure modes and fallbacks:
- Monitoring and alerting:

## 10. Architecture decisions (ADRs)

| ADR ID | Decision | Status | Rationale | Trade-offs |
|--------|----------|--------|-----------|------------|
| ADR-001 |  |  |  |  |
| ADR-002 |  |  |  |  |

## 11. Open issues

- 
- 
- 

## Completion checklist

- [ ] C4 context and container views complete
- [ ] Data and AI workflows documented
- [ ] Security and privacy controls mapped
- [ ] Reliability strategy defined
- [ ] Major decisions captured in ADRs
