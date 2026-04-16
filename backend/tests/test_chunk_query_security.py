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
        topic="nutrition",
        language="es",
        has_contraindication=True,
        limit=10,
        offset=0,
    )

    stmt = db.execute.await_args.args[0]
    params = db.execute.await_args.args[1]
    sql = str(stmt)

    # Query text should be static with optional parameter predicates (PGVector JSON metadata).
    assert "FROM data_clinical_chunks" in sql
    assert (
        "CAST(:therapy_type AS TEXT) IS NULL" in sql
        and "jsonb_build_array(CAST(:therapy_type AS TEXT))" in sql
    )
    assert (
        "CAST(:topic AS TEXT) IS NULL" in sql
        and "jsonb_build_array(CAST(:topic AS TEXT))" in sql
    )
    assert "metadata_::jsonb->>'language' = CAST(:language AS TEXT)" in sql
    assert (
        "CAST(:has_contraindication AS BOOLEAN) IS NULL" in sql
        and "CAST(:has_contraindication AS BOOLEAN)" in sql
    )

    # Inputs are bound via params, not interpolated in SQL text.
    assert params["therapy_type"] == "fisioterapia"
    assert params["topic"] == "nutrition"
    assert params["language"] == "es"
    assert params["has_contraindication"] is True


@pytest.mark.asyncio
async def test_list_clinical_chunks_null_optional_filters_use_typed_cast_sql():
    """Guards PostgreSQL/asyncpg: untyped NULL bind caused AmbiguousParameterError before CAST()."""
    db = AsyncMock()
    execute_result = MagicMock()
    execute_result.mappings.return_value.all.return_value = []
    db.execute.return_value = execute_result

    await list_clinical_chunks(
        db,
        therapy_type=None,
        topic=None,
        language=None,
        has_contraindication=None,
        limit=1,
        offset=0,
    )

    stmt = db.execute.await_args.args[0]
    params = db.execute.await_args.args[1]
    sql = str(stmt)

    assert "CAST(:therapy_type AS TEXT)" in sql
    assert "CAST(:topic AS TEXT)" in sql
    assert "CAST(:language AS TEXT)" in sql
    assert "CAST(:has_contraindication AS BOOLEAN)" in sql
    assert params["therapy_type"] is None
    assert params["topic"] is None
    assert params["language"] is None
    assert params["has_contraindication"] is None
    assert params["limit"] == 1
    assert params["offset"] == 0

