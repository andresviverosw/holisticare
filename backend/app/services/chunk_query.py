from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def list_clinical_chunks(
    db: AsyncSession,
    *,
    therapy_type: str | None,
    language: str | None,
    has_contraindication: bool | None,
    limit: int,
    offset: int,
) -> dict[str, Any]:
    filters: list[str] = []
    params: dict[str, Any] = {"limit": limit, "offset": offset}

    if therapy_type:
        filters.append(":therapy_type = ANY(therapy_type)")
        params["therapy_type"] = therapy_type
    if language:
        filters.append("language = :language")
        params["language"] = language
    if has_contraindication is not None:
        filters.append("has_contraindication = :has_contraindication")
        params["has_contraindication"] = has_contraindication

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    query = text(
        f"""
        SELECT ref_id, content, therapy_type, condition, evidence_level, language,
               section, has_contraindication, source_file, page_number
        FROM clinical_chunks
        {where_clause}
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
        """
    )
    result = await db.execute(query, params)
    items = [dict(row) for row in result.mappings().all()]
    return {
        "items": items,
        "limit": limit,
        "offset": offset,
    }
