# Solution diagrams (HolistiCare)

This page collects **Mermaid** diagrams for the running system: context, data, components, and flows. They render in GitHub, many IDEs (including Cursor/VS Code with a Mermaid preview), and static site generators.

For environment variables and local commands, see `setup.md`. For module-level notes, see `08-developer-guide-and-architecture.md`.

---

## 1. System context (C4 Level 1)

```mermaid
flowchart LR
  subgraph Actors
    CL[Clinician / Admin]
    PT[Patient]
  end

  subgraph HolistiCare
    FE[Web app\nReact + Vite]
    API[API\nFastAPI]
  end

  DB[(PostgreSQL\n+ pgvector)]
  AN[Anthropic API]
  OA[OpenAI API]

  CL --> FE
  PT --> FE
  FE -->|HTTPS /api proxy| API
  API --> DB
  API --> AN
  API --> OA
```

---

## 2. Containers (C4 Level 2)

```mermaid
flowchart TB
  subgraph Client
    B[Browser]
  end

  subgraph Deployable["HolistiCare stack"]
    FE[frontend\nstatic SPA]
    BE[backend\nPython FastAPI]
    PG[(PostgreSQL)]
  end

  B --> FE
  FE -->|REST + JWT| BE
  BE --> PG
  BE --> LLM[LLM providers\nAnthropic + OpenAI]
```

---

## 3. Logical entity relationship (application tables)

**Note:** There is no physical `patients` row store; `patient_id` (UUID) is the cross-cutting key. The diagram uses a **logical** `Patient` node for clarity. ORM models do not declare SQLAlchemy `relationship()` FK graphs for all pairs—associations are enforced in services and API contracts.

```mermaid
erDiagram
  Patient {
    string patient_id PK
  }

  intake_profiles {
    string id PK
    string patient_id FK
    string practitioner_id
    string intake_json
    string created_at
    string updated_at
  }

  intake_profile_audit {
    string id PK
    string patient_id FK
    string actor_sub
    string before_json
    string after_json
    string changed_at
  }

  treatment_plans {
    string id PK
    string patient_id FK
    string practitioner_id
    string status
    string plan_json
    string citations_used
    string approved_at
    string approved_by
    string created_at
    string updated_at
  }

  care_sessions {
    string id PK
    string patient_id FK
    string practitioner_id
    string occurred_at
    string session_json
    string created_at
    string updated_at
  }

  patient_diary_entries {
    string id PK
    string patient_id FK
    string entry_date
    string diary_json
    string created_at
    string updated_at
  }

  data_clinical_chunks {
    string id PK
    string chunk_text
    string metadata_
    string embedding
  }

  Patient ||--|| intake_profiles : "one profile"
  Patient ||--o{ intake_profile_audit : "history"
  Patient ||--o{ treatment_plans : "plans"
  Patient ||--o{ care_sessions : "sessions"
  Patient ||--o{ patient_diary_entries : "diary by day"
```

**Corpus:** `data_clinical_chunks` is managed by LlamaIndex `PGVectorStore` (ingestion pipeline). The physical column for chunk body is typically named `text` in PGVectorStore; the ER diagram uses `chunk_text` for readability. This table is **not** keyed by `patient_id`; retrieval binds evidence to a patient only at **query time** via the RAG pipeline (intake + goals → queries → chunks). No edge from `Patient` to `data_clinical_chunks` in the database.

---

## 4. Backend components (API → services → RAG)

```mermaid
flowchart TD
  MAIN[app/main.py]
  AUTH[app/api/auth.py]
  RAG[app/api/rag.py]

  MAIN --> AUTH
  MAIN --> RAG

  RAG --> DEPS[app/api/deps.py]
  RAG --> INTAKE[intake_service]
  RAG --> PLAN[plan_persistence]
  RAG --> CHUNK[chunk_query]
  RAG --> ING[ingestion_service]
  RAG --> DIARY[diary_service]
  RAG --> SESS[session_service]
  RAG --> ANLY[analytics_service]
  RAG --> PIPE[RAGPipeline]

  PIPE --> QB[QueryBuilder]
  PIPE --> VR[VectorRetriever]
  PIPE --> RR[Reranker]
  PIPE --> GEN[PlanGenerator]
```

---

## 5. RAG pipeline (UML-style composition)

```mermaid
classDiagram
  class RAGPipeline {
    +QueryBuilder query_builder
    +VectorRetriever retriever
    +BaseReranker reranker
    +PlanGenerator generator
    +run(...)
  }
  class QueryBuilder
  class VectorRetriever
  class BaseReranker
  class PlanGenerator

  RAGPipeline *-- QueryBuilder : composes
  RAGPipeline *-- VectorRetriever : composes
  RAGPipeline *-- BaseReranker : composes
  RAGPipeline *-- PlanGenerator : composes
```

---

## 6. Frontend routes (high level)

```mermaid
flowchart LR
  subgraph Public
    L["/login"]
  end

  subgraph Protected["JWT required"]
    D["/dashboard"]
    PR["/plan/:planId"]
    PS["/plan/:planId/sources"]
    C["/chunks"]
  end

  L --> D
  D --> PR
  PR --> PS
  D --> C
```

---

## 7. Flow: intake → draft plan generation

```mermaid
flowchart TD
  A[Clinician saves intake\nPOST /rag/intake] --> B[(intake_profiles)]
  C[Clinician requests plan\nPOST /rag/plan/generate] --> D[RAGPipeline.run]
  D --> E[QueryBuilder:\nsummary + query expansion]
  E --> F[VectorRetriever:\npgvector on data_clinical_chunks]
  F --> G[Reranker]
  G --> H{Chunks after rerank?}
  H -->|No| I[Insufficient evidence plan\npending_review]
  H -->|Yes| J[PlanGenerator\nstructured JSON + REF-IDs]
  J --> K[(treatment_plans)]
  I --> K
```

---

## 8. Flow: plan review and approval

```mermaid
flowchart TD
  A[Draft plan\nstatus pending_review] --> B[Clinician opens\nGET /rag/plan/{id}]
  B --> C{Decision}
  C -->|Approve| D[PATCH .../approve\naction=approve]
  C -->|Reject| E[PATCH .../approve\naction=reject + reason]
  D --> F[status approved]
  E --> G[status rejected]
```

---

## 9. Flow: corpus ingestion (admin)

```mermaid
flowchart TD
  A[PDF/HTML files in source_dir] --> B[POST /rag/ingest]
  B --> C[IngestionService / loader]
  C --> D[Chunk + embed]
  D --> E[(data_clinical_chunks)]
```

---

## 10. Flow: diary and analytics

```mermaid
flowchart TD
  P[Patient or clinician\nPOST /rag/diary] --> D[(patient_diary_entries)]
  Q[Clinician\nGET .../outcomes-trend] --> D
  R[Clinician\nGET .../plateau-flags] --> D
  Q --> S[Time series response]
  R --> T[Heuristic flags]
```

---

## 11. Sequence: plan generation (detail)

Same end-to-end as `08-developer-guide-and-architecture.md` (RAG pipeline sequence). Summary:

```mermaid
sequenceDiagram
  participant UI as Frontend
  participant API as POST /rag/plan/generate
  participant Pipe as RAGPipeline
  participant DB as PostgreSQL

  UI->>API: intake_json + therapies
  API->>Pipe: run(...)
  Pipe->>Pipe: query → retrieve → rerank → generate
  alt insufficient evidence
    API->>DB: persist stub plan
  else success
    API->>DB: persist plan_json + citations
  end
  API-->>UI: plan + plan_id
```

---

## 12. State: treatment plan status

```mermaid
stateDiagram-v2
  [*] --> pending_review : generate
  pending_review --> approved : clinician approves
  pending_review --> rejected : clinician rejects
  approved --> [*]
  rejected --> [*]
```

---

## Maintenance

- When adding tables or endpoints, update the **ER** and **flow** sections here and the narrative in `08-developer-guide-and-architecture.md`.
- Prefer Mermaid over binary images so diagrams **diff** cleanly in PRs.
