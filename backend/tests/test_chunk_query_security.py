from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.chunk_query import list_clinical_chunks


@pytest.mark.asyncio
async def test_list_clinical_chunks_uses_static_parameterized_query():
    db = AsyncMock()
    execute_result = MagicMock()
    execute_result.mappings.return_value.all.return_value = []
    db.execute.return_value = execute_result

    await list_clinical_chunks(
        db,
        therapy_type="fisioterapia",
        language="es",
        has_contraindication=True,
        limit=10,
        offset=0,
    )

    stmt = db.execute.await_args.args[0]
    params = db.execute.await_args.args[1]
    sql = str(stmt)

    # Query text should be static with optional parameter predicates.
    assert (
        "WHERE (CAST(:therapy_type AS TEXT) IS NULL OR CAST(:therapy_type AS TEXT) = ANY(therapy_type))"
        in sql
    )
    assert (
        "AND (CAST(:language AS TEXT) IS NULL OR language = CAST(:language AS TEXT))" in sql
    )
    assert (
        "CAST(:has_contraindication AS BOOLEAN) IS NULL" in sql
        and "has_contraindication = CAST(:has_contraindication AS BOOLEAN)" in sql
    )

    # Inputs are bound via params, not interpolated in SQL text.
    assert params["therapy_type"] == "fisioterapia"
    assert params["language"] == "es"
    assert params["has_contraindication"] is True

