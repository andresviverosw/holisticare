# SYNTH-01 — Synthetic Dataset v1 (capstone appendix)

| Field | Value |
|-------|--------|
| Story ID | **SYNTH-01** |
| Status | Ready for demo / thesis appendix |
| Package | `backend/data/synthetic/v1/dataset.json` |
| Generator | `backend/app/synthetic/` |
| Privacy | **100% synthetic** — no real patient data |

## Purpose

Provide a reproducible clinical corpus that exercises the full HolistiCare loop for final delivery demos and academic evidence:

1. Intake profiles (`generic_holistic_v0`)
2. Treatment plans with NOM-024 governance (`requires_practitioner_review`, status mix)
3. Care session logs (`clinical_session_v0`)
4. Daily diary check-ins (`patient_diary_v0`) with Spanish free text
5. KPI / analytics series (outcomes trend)
6. Plateau / worsening flags (`US-ANLY-002`)
7. Recovery trajectory labels (`US-PRED-001`)
8. Plan memory-bank templates (`US-PLAN-004`)

## Scale

| Mode | Command flag | Patients | Notes |
|------|--------------|----------|-------|
| **Default (demo)** | `--variants 4` | **32** (8 archetypes × 4) | Shipped JSON package |
| **README target** | `--variants 10` | **80** | Optional full-scale regenerate |

Default package uses `seed=42` for bit-stable IDs and series.

## Clinician archetypes (8)

| ID | Role flavor | Primary presentation |
|----|-------------|----------------------|
| `osteo_lumbar` | Osteopath / PT | Chronic low-back pain |
| `nutri_ibs` | Nutritionist | IBS + anxiety + lactose / shellfish constraints |
| `sleep_fatigue` | Holistic coach | Fatigue + non-restorative sleep |
| `acupuncture_cervical` | Acupuncturist | Cervical pain + tension headache |
| `knee_osteo` | Physiotherapist | Mild knee osteoarthritis |
| `anxiety_burnout` | Mindfulness | Anxiety / burnout |
| `shoulder_impingement` | Physiotherapist | Shoulder impingement |
| `metabolic_nutrition` | Nutritionist | Insulin resistance + gluten allergy |

## Trajectory cohorts (KPI coverage)

Each archetype cycles through these trajectories (by variant index):

| Trajectory | Diary shape | Exercises |
|------------|-------------|-----------|
| `improving` | Downward pain slope over ~8 weeks | Recovery label **improving**; trend charts |
| `high_pain_plateau` | High pain (~≥7) with little half-window change | Flag `HIGH_PAIN_PLATEAU` |
| `worsening` | Second-half pain mean ≥ first-half + 2 | Flag `PAIN_WORSENING` (+ function drop) |
| `short_series` | &lt; 7 diary points | `insufficient_data` for plateau + recovery |

Realism rules baked in:

- ~15% random diary-day skips on longitudinal cohorts
- ~5% adverse-event Spanish notes
- Non-linear noise on scores
- Plan status mix: `approved`, `pending_review`, `rejected`, plus `insufficient_evidence` empty-week plans

## How to regenerate

```bash
cd backend
python -m scripts.generate_synthetic_dataset --variants 4 --seed 42
# Full README-scale (~80 patients):
python -m scripts.generate_synthetic_dataset --variants 10 --seed 42 \
  --out data/synthetic/v1/dataset-full.json
```

## How to seed a live database

Requires `DATABASE_URL` pointing at Postgres (Compose / Render).

```bash
cd backend
# Uses committed dataset.json (or generates if missing)
python -m scripts.seed_synthetic_dataset

# Force regenerate then seed
python -m scripts.seed_synthetic_dataset --generate --write-dataset --variants 4
```

Idempotent: deterministic UUIDs (`uuid5`) upsert intakes, plans, sessions, diary rows, and memory-bank entries.

Suggested demo order after seed:

1. Login as clinician
2. Open a patient UUID from `manifest` / dataset (improving vs worsening)
3. Dashboard → outcomes trend + plateau flags
4. Plan review (approved / pending / rejected examples)
5. Memory bank templates list

## Validation

```bash
python -m pytest backend/tests/test_synthetic_dataset.py -q
```

Tests assert Pydantic schema validity, NOM-024 review flag, deterministic IDs, analytics/plateau cohort behavior, memory-bank de-identification, and adverse-event rate band.

## Relation to pilot cases

`backend/data/pilot/cases.json` remains the **AI quality / rehearsal** mini-set (3 live RAG cases).  
SYNTH-01 is the **longitudinal product corpus** for diaries, KPIs, and governance status coverage. Both are synthetic and complementary.

## Acceptance criteria (Planning → Dev → QA)

- [x] Deterministic generator with seed + stable UUIDs
- [x] Default package covers all 8 archetypes and 4 trajectories
- [x] Intake / diary / session payloads validate against v0 schemas
- [x] Plans always `requires_practitioner_review: true`; status mix includes approved / pending / rejected / insufficient_evidence
- [x] Improving / plateau / worsening / short cohorts exercise analytics services
- [x] Memory-bank snapshots strip `patient_id`
- [x] CLI generate + DB seed scripts documented
- [x] Unit tests green (no Docker / no API keys)
