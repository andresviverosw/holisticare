"""
Load and validate nutrition safety synonym groups from JSON.

Default file: app/config/nutrition_safety_terms.json
Override: set NUTRITION_SAFETY_TERMS_PATH to an absolute path (or path relative to cwd).
"""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.config import get_settings


def normalize_nutrition_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    no_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    lowered = no_accents.lower()
    return re.sub(r"[^a-z0-9]+", " ", lowered).strip()


def _default_config_path() -> Path:
    return Path(__file__).resolve().parent.parent / "config" / "nutrition_safety_terms.json"


def load_nutrition_synonym_groups_from_path(path: Path) -> dict[str, set[str]]:
    """
    Parse JSON into a map: normalized canonical -> set of normalized tokens (canonical + synonyms).

    Raises ValueError with a clear message if the file is missing, invalid JSON, or schema violations.
    """
    if not path.is_file():
        raise ValueError(f"Nutrition safety terms file not found: {path}")

    try:
        raw = path.read_text(encoding="utf-8")
        data: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in nutrition safety terms file {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Nutrition safety terms root must be an object, got {type(data).__name__}")

    version = data.get("version")
    if version is not None and not isinstance(version, int):
        raise ValueError("Nutrition safety terms 'version' must be an integer when present")

    groups = data.get("groups")
    if not isinstance(groups, list):
        raise ValueError("Nutrition safety terms must contain a 'groups' array")

    result: dict[str, set[str]] = {}
    for i, group in enumerate(groups):
        if not isinstance(group, dict):
            raise ValueError(f"groups[{i}] must be an object")
        canonical = group.get("canonical")
        if not isinstance(canonical, str) or not canonical.strip():
            raise ValueError(f"groups[{i}].canonical must be a non-empty string")
        syns = group.get("synonyms", [])
        if syns is None:
            syns = []
        if not isinstance(syns, list):
            raise ValueError(f"groups[{i}].synonyms must be an array")
        for j, s in enumerate(syns):
            if not isinstance(s, str) or not s.strip():
                raise ValueError(f"groups[{i}].synonyms[{j}] must be a non-empty string")

        key = normalize_nutrition_text(canonical)
        if not key:
            raise ValueError(f"groups[{i}].canonical normalizes to empty token")
        tokens: set[str] = {key}
        for s in syns:
            t = normalize_nutrition_text(s)
            if t:
                tokens.add(t)
        if key in result:
            raise ValueError(f"Duplicate canonical after normalization: {key!r}")
        result[key] = tokens

    return result


@lru_cache
def get_nutrition_synonym_groups() -> dict[str, set[str]]:
    """
    Cached synonym map for nutrition safety guards.

    Uses Settings.nutrition_safety_terms_path when set; otherwise the bundled default JSON.
    """
    settings = get_settings()
    override = settings.nutrition_safety_terms_path
    if override:
        path = Path(override)
        if not path.is_absolute():
            path = Path.cwd() / path
    else:
        path = _default_config_path()
    return load_nutrition_synonym_groups_from_path(path)


def clear_nutrition_synonym_groups_cache() -> None:
    """Test helper: reset lru_cache after env/settings change."""
    get_nutrition_synonym_groups.cache_clear()
