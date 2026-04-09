from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.ingestion.embedder import PGVECTOR_DATA_TABLE


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
    # Rows live in LlamaIndex PGVectorStore table data_<index>, with metadata in metadata_ JSON.
    query = text(
        f"""
        SELECT
            metadata_::jsonb->>'ref_id' AS ref_id,
            text AS content,
            ARRAY(
                SELECT jsonb_array_elements_text(
                    COALESCE(metadata_::jsonb->'therapy_type', '[]'::jsonb)
                )
            ) AS therapy_type,
            ARRAY(
                SELECT jsonb_array_elements_text(
                    COALESCE(metadata_::jsonb->'condition', '[]'::jsonb)
                )
            ) AS condition,
            metadata_::jsonb->>'evidence_level' AS evidence_level,
            metadata_::jsonb->>'language' AS language,
            metadata_::jsonb->>'section' AS section,
            COALESCE((metadata_::jsonb->>'has_contraindication')::boolean, false)
                AS has_contraindication,
            metadata_::jsonb->>'source_file' AS source_file,
            (metadata_::jsonb->>'page_number')::int AS page_number
        FROM {PGVECTOR_DATA_TABLE}
        WHERE (
            CAST(:therapy_type AS TEXT) IS NULL
            OR COALESCE(metadata_::jsonb->'therapy_type', '[]'::jsonb)
                @> jsonb_build_array(CAST(:therapy_type AS TEXT))
        )
          AND (
            CAST(:language AS TEXT) IS NULL
            OR metadata_::jsonb->>'language' = CAST(:language AS TEXT)
          )
          AND (
            CAST(:has_contraindication AS BOOLEAN) IS NULL
            OR COALESCE((metadata_::jsonb->>'has_contraindication')::boolean, false)
                = CAST(:has_contraindication AS BOOLEAN)
          )
        ORDER BY id DESC
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
