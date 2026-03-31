-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── Clinical knowledge chunks ────────────────────────────────
CREATE TABLE IF NOT EXISTS clinical_chunks (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ref_id          TEXT UNIQUE NOT NULL,
    content         TEXT NOT NULL,
    embedding       VECTOR(1536),
    therapy_type    TEXT[],
    condition       TEXT[],
    evidence_level  TEXT CHECK (evidence_level IN ('A', 'B', 'C', 'expert_opinion')),
    language        TEXT CHECK (language IN ('en', 'es')),
    section         TEXT,
    has_contraindication BOOLEAN DEFAULT FALSE,
    source_file     TEXT,
    page_number     INT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Vector similarity index (cosine)
CREATE INDEX IF NOT EXISTS clinical_chunks_embedding_idx
    ON clinical_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Metadata filter indexes
CREATE INDEX IF NOT EXISTS clinical_chunks_therapy_idx  ON clinical_chunks USING GIN (therapy_type);
CREATE INDEX IF NOT EXISTS clinical_chunks_condition_idx ON clinical_chunks USING GIN (condition);
CREATE INDEX IF NOT EXISTS clinical_chunks_lang_idx     ON clinical_chunks (language);
CREATE INDEX IF NOT EXISTS clinical_chunks_contra_idx   ON clinical_chunks (has_contraindication);

-- ─── Ingestion log ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ingestion_log (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_file TEXT NOT NULL,
    chunk_count INT NOT NULL,
    status      TEXT CHECK (status IN ('success', 'partial', 'failed')),
    error_msg   TEXT,
    run_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Treatment plans ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS treatment_plans (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id      UUID NOT NULL,
    practitioner_id UUID,
    status          TEXT CHECK (status IN ('pending_review', 'approved', 'rejected', 'active')) DEFAULT 'pending_review',
    plan_json       JSONB NOT NULL,
    citations_used  TEXT[],
    approved_at     TIMESTAMPTZ,
    approved_by     UUID,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Intake profiles ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS intake_profiles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id      UUID NOT NULL UNIQUE,
    practitioner_id UUID,
    intake_json     JSONB NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS intake_profile_audit (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id      UUID NOT NULL,
    actor_sub       TEXT NOT NULL,
    before_json     JSONB NOT NULL,
    after_json      JSONB NOT NULL,
    changed_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Care sessions (clinical visit log) ───────────────────────
CREATE TABLE IF NOT EXISTS care_sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id      UUID NOT NULL,
    practitioner_id UUID,
    occurred_at     TIMESTAMPTZ NOT NULL,
    session_json    JSONB NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS care_sessions_patient_occurred_idx
    ON care_sessions (patient_id, occurred_at DESC);

-- ─── Patient diary (daily check-ins) ───────────────────────────
CREATE TABLE IF NOT EXISTS patient_diary_entries (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id      UUID NOT NULL,
    entry_date      DATE NOT NULL,
    diary_json      JSONB NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_patient_diary_entry_day UNIQUE (patient_id, entry_date)
);

CREATE INDEX IF NOT EXISTS patient_diary_entries_patient_date_idx
    ON patient_diary_entries (patient_id, entry_date DESC);
