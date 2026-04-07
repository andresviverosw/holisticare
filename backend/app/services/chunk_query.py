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
    params: dict[str, Any] = {
        "therapy_type": therapy_type,
        "language": language,
        "has_contraindication": has_contraindication,
        "limit": limit,
        "offset": offset,
    }
    query = text(
        """
        SELECT ref_id, content, therapy_type, condition, evidence_level, language,
               section, has_contraindication, source_file, page_number
        FROM clinical_chunks
        WHERE (CAST(:therapy_type AS TEXT) IS NULL OR CAST(:therapy_type AS TEXT) = ANY(therapy_type))
          AND (CAST(:language AS TEXT) IS NULL OR language = CAST(:language AS TEXT))
          AND (
            CAST(:has_contraindication AS BOOLEAN) IS NULL
            OR has_contraindication = CAST(:has_contraindication AS BOOLEAN)
          )
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
