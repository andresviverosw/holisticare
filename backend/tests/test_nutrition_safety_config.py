"""US-RAG-004: nutrition safety synonym JSON loader and validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.rag.nutrition_safety_config import (
    _default_config_path,
    clear_nutrition_synonym_groups_cache,
    get_nutrition_synonym_groups,
    load_nutrition_synonym_groups_from_path,
    normalize_nutrition_text,
)


def test_normalize_nutrition_text_strips_accents_and_punctuation() -> None:
    assert normalize_nutrition_text("Salmón, a la plancha!") == "salmon a la plancha"


def test_default_bundled_json_loads_and_contains_pescado_group() -> None:
    path = _default_config_path()
    assert path.is_file(), f"expected bundled config at {path}"
    groups = load_nutrition_synonym_groups_from_path(path)
    assert "pescado" in groups
    assert "salmon" in groups["pescado"]
    assert "atun" in groups["pescado"]


def test_load_raises_when_file_missing(tmp_path: Path) -> None:
    missing = tmp_path / "nope.json"
    with pytest.raises(ValueError, match="not found"):
        load_nutrition_synonym_groups_from_path(missing)


def test_load_raises_on_invalid_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{ not json", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_nutrition_synonym_groups_from_path(bad)


def test_load_raises_when_root_not_object(tmp_path: Path) -> None:
    f = tmp_path / "x.json"
    f.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="root must be an object"):
        load_nutrition_synonym_groups_from_path(f)


def test_load_raises_when_groups_missing(tmp_path: Path) -> None:
    f = tmp_path / "x.json"
    f.write_text(json.dumps({"version": 1}), encoding="utf-8")
    with pytest.raises(ValueError, match="'groups' array"):
        load_nutrition_synonym_groups_from_path(f)


def test_load_raises_on_duplicate_canonical_after_normalize(tmp_path: Path) -> None:
    f = tmp_path / "x.json"
    f.write_text(
        json.dumps(
            {
                "version": 1,
                "groups": [
                    {"canonical": "pescado", "synonyms": ["atun"]},
                    {"canonical": "PESCADO", "synonyms": ["salmon"]},
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate canonical"):
        load_nutrition_synonym_groups_from_path(f)


def test_get_nutrition_synonym_groups_uses_cached_default() -> None:
    clear_nutrition_synonym_groups_cache()
    a = get_nutrition_synonym_groups()
    b = get_nutrition_synonym_groups()
    assert a is b
    assert "gluten" in a
