"""Unit tests for seed_clinician CLI argument validation helpers."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scripts import seed_clinician


@pytest.mark.asyncio
async def test_seed_requires_env(monkeypatch):
    monkeypatch.delenv("SEED_CLINICIAN_USERNAME", raising=False)
    monkeypatch.delenv("SEED_CLINICIAN_PASSWORD", raising=False)
    code = await seed_clinician._run()
    assert code == 1


@pytest.mark.asyncio
async def test_seed_calls_create_or_update(monkeypatch):
    monkeypatch.setenv("SEED_CLINICIAN_USERNAME", "clinician1")
    monkeypatch.setenv("SEED_CLINICIAN_PASSWORD", "s3cret")
    monkeypatch.setenv("SEED_CLINICIAN_ROLE", "admin")

    fake_user = MagicMock()
    fake_user.id = "uid"
    fake_user.username = "clinician1"
    fake_user.role = "admin"

    session = AsyncMock()
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=None)

    with (
        patch.object(seed_clinician, "AsyncSessionLocal", return_value=session_cm),
        patch.object(
            seed_clinician,
            "create_or_update_user",
            new=AsyncMock(return_value=fake_user),
        ) as create_mock,
    ):
        code = await seed_clinician._run()

    assert code == 0
    create_mock.assert_awaited_once()
    kwargs = create_mock.await_args.kwargs
    assert kwargs["username"] == "clinician1"
    assert kwargs["password"] == "s3cret"
    assert kwargs["role"] == "admin"
