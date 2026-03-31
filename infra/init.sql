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
