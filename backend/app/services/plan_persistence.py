from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import bindparam, select, text
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


async def get_persisted_plan(
    db: AsyncSession,
    *,
    plan_id: uuid.UUID,
) -> TreatmentPlan | None:
    stmt = select(TreatmentPlan).where(TreatmentPlan.id == plan_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_plan_sources_payload(
    db: AsyncSession,
    *,
    plan_id: uuid.UUID,
) -> dict[str, Any] | None:
    plan_row = await get_persisted_plan(db, plan_id=plan_id)
    if plan_row is None:
        return None

    citations = list(plan_row.citations_used or plan_row.plan_json.get("citations_used", []))
    if not citations:
        return {
            "plan_id": str(plan_row.id),
            "citations_used": [],
            "sources": [],
        }

    # ref_id is our citation key in plan_json and clinical_chunks.
    query = text(
        """
        SELECT ref_id, content, source_file, page_number, section, language,
               evidence_level, has_contraindication
        FROM clinical_chunks
        WHERE ref_id IN :refs
        """
    ).bindparams(bindparam("refs", expanding=True))
    chunk_result = await db.execute(query, {"refs": citations})
    source_rows = [dict(row) for row in chunk_result.mappings().all()]
    by_ref_id = {row["ref_id"]: row for row in source_rows if "ref_id" in row}
    sources = [by_ref_id[ref] for ref in citations if ref in by_ref_id]
    return {
        "plan_id": str(plan_row.id),
        "citations_used": citations,
        "sources": sources,
    }
