"""
seed_synthetic_dataset.py — load SYNTH-01 dataset into PostgreSQL (idempotent).

Usage:
    python -m scripts.seed_synthetic_dataset
    python -m scripts.seed_synthetic_dataset --dataset data/synthetic/v1/dataset.json
    python -m scripts.seed_synthetic_dataset --generate --variants 4

Idempotent: upserts by deterministic primary keys / patient_id unique constraints.
Requires a live DATABASE_URL (same as the API).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: E402

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.models.care_session import CareSession  # noqa: E402
from app.models.intake_profile import IntakeProfile  # noqa: E402
from app.models.patient_diary_entry import PatientDiaryEntry  # noqa: E402
from app.models.plan_memory_bank import PlanMemoryBankEntry  # noqa: E402
from app.models.treatment_plan import TreatmentPlan  # noqa: E402
from app.synthetic.generator import (  # noqa: E402
    DEFAULT_SEED,
    DEFAULT_VARIANTS_PER_ARCHETYPE,
    SyntheticDataset,
    dataset_from_dict,
    dataset_to_dict,
    generate_synthetic_dataset,
)

DEFAULT_DATASET = Path(__file__).parent.parent / "data" / "synthetic" / "v1" / "dataset.json"


async def _upsert_intake(
    db: AsyncSession,
    *,
    patient_id: UUID,
    practitioner_id: UUID,
    intake_json: dict[str, Any],
) -> None:
    stmt = select(IntakeProfile).where(IntakeProfile.patient_id == patient_id)
    row = (await db.execute(stmt)).scalar_one_or_none()
    if row is None:
        db.add(
            IntakeProfile(
                id=patient_id,  # stable: one profile id per synthetic patient
                patient_id=patient_id,
                practitioner_id=practitioner_id,
                intake_json=dict(intake_json),
            )
        )
    else:
        row.practitioner_id = practitioner_id
        row.intake_json = dict(intake_json)


async def _upsert_plan(
    db: AsyncSession,
    *,
    plan: dict[str, Any],
    patient_id: UUID,
    practitioner_id: UUID,
) -> None:
    plan_id = UUID(str(plan["plan_id"]))
    stmt = select(TreatmentPlan).where(TreatmentPlan.id == plan_id)
    row = (await db.execute(stmt)).scalar_one_or_none()
    citations = list(plan.get("citations_used") or [])
    status = plan.get("status") or "pending_review"
    approved_at = None
    approved_by = None
    if status == "approved":
        raw = plan.get("approved_at")
        if isinstance(raw, str):
            approved_at = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        else:
            approved_at = datetime.now(timezone.utc)
        approved_by = practitioner_id

    if row is None:
        db.add(
            TreatmentPlan(
                id=plan_id,
                patient_id=patient_id,
                practitioner_id=practitioner_id,
                status=status,
                plan_json=dict(plan),
                citations_used=citations,
                approved_at=approved_at,
                approved_by=approved_by,
            )
        )
    else:
        row.patient_id = patient_id
        row.practitioner_id = practitioner_id
        row.status = status
        row.plan_json = dict(plan)
        row.citations_used = citations
        row.approved_at = approved_at
        row.approved_by = approved_by


async def _upsert_session(
    db: AsyncSession,
    *,
    session_id: UUID,
    patient_id: UUID,
    practitioner_id: UUID,
    occurred_at: datetime,
    session_json: dict[str, Any],
) -> None:
    stmt = select(CareSession).where(CareSession.id == session_id)
    row = (await db.execute(stmt)).scalar_one_or_none()
    if row is None:
        db.add(
            CareSession(
                id=session_id,
                patient_id=patient_id,
                practitioner_id=practitioner_id,
                occurred_at=occurred_at,
                session_json=dict(session_json),
            )
        )
    else:
        row.patient_id = patient_id
        row.practitioner_id = practitioner_id
        row.occurred_at = occurred_at
        row.session_json = dict(session_json)


async def _upsert_diary(
    db: AsyncSession,
    *,
    entry_id: UUID,
    patient_id: UUID,
    entry_date,
    diary_json: dict[str, Any],
) -> None:
    stmt = select(PatientDiaryEntry).where(PatientDiaryEntry.id == entry_id)
    row = (await db.execute(stmt)).scalar_one_or_none()
    if row is None:
        # Also honor unique (patient_id, entry_date)
        stmt2 = select(PatientDiaryEntry).where(
            PatientDiaryEntry.patient_id == patient_id,
            PatientDiaryEntry.entry_date == entry_date,
        )
        existing = (await db.execute(stmt2)).scalar_one_or_none()
        if existing is None:
            db.add(
                PatientDiaryEntry(
                    id=entry_id,
                    patient_id=patient_id,
                    entry_date=entry_date,
                    diary_json=dict(diary_json),
                )
            )
        else:
            existing.diary_json = dict(diary_json)
    else:
        row.patient_id = patient_id
        row.entry_date = entry_date
        row.diary_json = dict(diary_json)


async def _upsert_memory(
    db: AsyncSession,
    *,
    entry: dict[str, Any],
) -> None:
    mid = UUID(entry["id"])
    stmt = select(PlanMemoryBankEntry).where(PlanMemoryBankEntry.id == mid)
    row = (await db.execute(stmt)).scalar_one_or_none()
    if row is None:
        db.add(
            PlanMemoryBankEntry(
                id=mid,
                source_plan_id=UUID(entry["source_plan_id"]),
                title=entry["title"][:200],
                tags=entry.get("tags"),
                therapy_types=entry.get("therapy_types"),
                language=entry.get("language") or "es",
                snapshot_json=dict(entry["snapshot_json"]),
                created_by_sub=str(entry["created_by_sub"])[:255],
            )
        )
    else:
        row.source_plan_id = UUID(entry["source_plan_id"])
        row.title = entry["title"][:200]
        row.tags = entry.get("tags")
        row.therapy_types = entry.get("therapy_types")
        row.language = entry.get("language") or "es"
        row.snapshot_json = dict(entry["snapshot_json"])
        row.created_by_sub = str(entry["created_by_sub"])[:255]


async def seed_dataset(db: AsyncSession, ds: SyntheticDataset) -> dict[str, int]:
    payload = dataset_to_dict(ds)
    practitioner_id = ds.practitioner_id
    counts = {"patients": 0, "sessions": 0, "diary": 0, "memory_bank": 0}

    for p in ds.patients:
        await _upsert_intake(
            db,
            patient_id=p.patient_id,
            practitioner_id=practitioner_id,
            intake_json=p.intake_json,
        )
        await _upsert_plan(
            db,
            plan=p.plan,
            patient_id=p.patient_id,
            practitioner_id=practitioner_id,
        )
        counts["patients"] += 1
        for s in p.sessions:
            await _upsert_session(
                db,
                session_id=s.id,
                patient_id=p.patient_id,
                practitioner_id=practitioner_id,
                occurred_at=s.occurred_at,
                session_json=s.session_json,
            )
            counts["sessions"] += 1
        for e in p.diary_entries:
            await _upsert_diary(
                db,
                entry_id=e.id,
                patient_id=p.patient_id,
                entry_date=e.entry_date,
                diary_json=e.diary_json,
            )
            counts["diary"] += 1

    for m in payload["memory_bank"]:
        await _upsert_memory(db, entry=m)
        counts["memory_bank"] += 1

    await db.commit()
    return counts


async def _run(args: argparse.Namespace) -> int:
    if args.generate or not args.dataset.exists():
        ds = generate_synthetic_dataset(
            seed=args.seed,
            variants_per_archetype=args.variants,
        )
        if args.write_dataset or not args.dataset.exists():
            args.dataset.parent.mkdir(parents=True, exist_ok=True)
            args.dataset.write_text(
                json.dumps(dataset_to_dict(ds), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    else:
        payload = json.loads(args.dataset.read_text(encoding="utf-8"))
        ds = dataset_from_dict(payload)

    async with AsyncSessionLocal() as db:
        counts = await seed_dataset(db, ds)

    print(
        "OK: seeded synthetic dataset "
        f"patients={counts['patients']} sessions={counts['sessions']} "
        f"diary={counts['diary']} memory_bank={counts['memory_bank']}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed SYNTH-01 dataset into the database.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--generate", action="store_true", help="Regenerate before seed.")
    parser.add_argument(
        "--write-dataset",
        action="store_true",
        help="When generating, also write JSON to --dataset.",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--variants", type=int, default=DEFAULT_VARIANTS_PER_ARCHETYPE)
    args = parser.parse_args(argv)

    import asyncio

    return asyncio.run(_run(args))


if __name__ == "__main__":
    raise SystemExit(main())
