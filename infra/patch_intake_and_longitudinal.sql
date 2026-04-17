-- Idempotent DDL for databases created before these tables were added to init.sql.
-- Safe to run multiple times (CREATE TABLE IF NOT EXISTS / CREATE INDEX IF NOT EXISTS).

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

-- ─── Care sessions ────────────────────────────────────────────
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

-- ─── Patient diary ───────────────────────────────────────────
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
