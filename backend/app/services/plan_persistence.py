from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.treatment_plan import TreatmentPlan


def build_treatment_plan_row(
    plan: dict[str, Any],
    *,
    patient_id: uuid.UUID,
    practitioner_id: uuid.UUID | None,
) -> TreatmentPlan:
    plan_id = uuid.UUID(str(plan["plan_id"]))
    citations_src = plan.get("citations_used")
    citations = list(citations_src) if citations_src is not None else []
    status = plan.get("status") or "pending_review"
    return TreatmentPlan(
        id=plan_id,
        patient_id=patient_id,
        practitioner_id=practitioner_id,
        status=status,
        plan_json=dict(plan),
        citations_used=citations,
    )


async def persist_generated_plan(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    practitioner_id: uuid.UUID | None,
    plan: dict[str, Any],
) -> uuid.UUID:
    row = build_treatment_plan_row(
        plan,
        patient_id=patient_id,
        practitioner_id=practitioner_id,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row.id
