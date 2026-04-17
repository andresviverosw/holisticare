from __future__ import annotations

import copy
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan_memory_bank import PlanMemoryBankEntry
from app.services.plan_persistence import get_persisted_plan, persist_generated_plan


def extract_therapy_types(plan: dict[str, Any]) -> list[str]:
    out: set[str] = set()
    for week in plan.get("weeks") or []:
        if not isinstance(week, dict):
            continue
        for t in week.get("therapies") or []:
            if isinstance(t, dict):
                typ = t.get("type")
                if isinstance(typ, str) and typ.strip():
                    out.add(typ.strip().lower())
    return sorted(out)


def sanitize_plan_for_memory_bank(plan: dict[str, Any]) -> dict[str, Any]:
    """De-identify plan JSON for storage as a reusable template snapshot."""
    snap = copy.deepcopy(plan)
    snap.pop("patient_id", None)
    snap.pop("retrieval_metadata", None)
    snap.pop("practitioner_notes", None)
    snap.pop("nutrition_safety_flags", None)
    snap["memory_bank_snapshot"] = True
    return snap


def build_draft_from_template(
    snapshot: dict[str, Any],
    *,
    new_plan_id: uuid.UUID,
    new_patient_id: uuid.UUID,
    memory_bank_entry_id: uuid.UUID,
) -> dict[str, Any]:
    """Produce a new pending_review plan dict from a bank snapshot."""
    draft = copy.deepcopy(snapshot)
    draft.pop("memory_bank_snapshot", None)
    now = datetime.now(timezone.utc).isoformat()
    draft["plan_id"] = str(new_plan_id)
    draft["patient_id"] = str(new_patient_id)
    draft["status"] = "pending_review"
    draft["generated_at"] = now
    draft["requires_practitioner_review"] = True
    draft["insufficient_evidence"] = False
    draft["nutrition_safety_flags"] = []
    draft["derived_from_memory_bank"] = {
        "template_id": str(memory_bank_entry_id),
        "instantiated_at": now,
    }
    draft["confidence_note"] = (
        (draft.get("confidence_note") or "").strip()
        + " [Borrador desde biblioteca de plantillas; valide nutrición y contraindicaciones para este paciente.]"
    ).strip()
    return draft


async def add_plan_to_memory_bank(
    db: AsyncSession,
    *,
    source_plan_id: uuid.UUID,
    title: str,
    tags: list[str],
    created_by_sub: str,
) -> PlanMemoryBankEntry | None:
    row = await get_persisted_plan(db, plan_id=source_plan_id)
    if row is None:
        return None
    if row.status != "approved":
        raise ValueError("only_approved_plans")

    snapshot = sanitize_plan_for_memory_bank(dict(row.plan_json))
    therapies = extract_therapy_types(snapshot)
    tags_norm = [t.strip() for t in tags if isinstance(t, str) and t.strip()][:32]

    entry = PlanMemoryBankEntry(
        id=uuid.uuid4(),
        source_plan_id=source_plan_id,
        title=title.strip()[:200],
        tags=tags_norm or None,
        therapy_types=therapies or None,
        language="es",
        snapshot_json=snapshot,
        created_by_sub=created_by_sub[:255],
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


def _search_filter(stmt: Select[Any], q: str) -> Select[Any]:
    qt = f"%{q.strip().lower()}%"
    return stmt.where(
        or_(
            func.lower(PlanMemoryBankEntry.title).like(qt),
            func.lower(func.coalesce(func.array_to_string(PlanMemoryBankEntry.tags, ","), "")).like(qt),
            func.lower(func.coalesce(func.array_to_string(PlanMemoryBankEntry.therapy_types, ","), "")).like(
                qt
            ),
        )
    )


async def list_memory_bank_entries(
    db: AsyncSession,
    *,
    q: str | None,
    limit: int,
    offset: int,
) -> list[PlanMemoryBankEntry]:
    stmt = select(PlanMemoryBankEntry).order_by(PlanMemoryBankEntry.created_at.desc())
    if q and q.strip():
        stmt = _search_filter(stmt, q)
    stmt = stmt.limit(min(limit, 100)).offset(max(offset, 0))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_memory_bank_entry(
    db: AsyncSession,
    *,
    entry_id: uuid.UUID,
) -> PlanMemoryBankEntry | None:
    stmt = select(PlanMemoryBankEntry).where(PlanMemoryBankEntry.id == entry_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def instantiate_plan_from_template(
    db: AsyncSession,
    *,
    template_id: uuid.UUID,
    patient_id: uuid.UUID,
    practitioner_id: uuid.UUID | None,
) -> dict[str, Any] | None:
    template = await get_memory_bank_entry(db, entry_id=template_id)
    if template is None:
        return None
    new_plan_id = uuid.uuid4()
    draft = build_draft_from_template(
        template.snapshot_json,
        new_plan_id=new_plan_id,
        new_patient_id=patient_id,
        memory_bank_entry_id=template.id,
    )
    await persist_generated_plan(
        db,
        patient_id=patient_id,
        practitioner_id=practitioner_id,
        plan=draft,
    )
    return draft
