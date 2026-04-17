-- US-PLAN-004: plan memory bank (idempotent for existing volumes)

CREATE TABLE IF NOT EXISTS plan_memory_bank (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_plan_id   UUID NOT NULL,
    title            VARCHAR(200) NOT NULL,
    tags             TEXT[],
    therapy_types    TEXT[],
    language         VARCHAR(8),
    snapshot_json    JSONB NOT NULL,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    created_by_sub   VARCHAR(255) NOT NULL
);

CREATE INDEX IF NOT EXISTS plan_memory_bank_created_at_idx ON plan_memory_bank (created_at DESC);
