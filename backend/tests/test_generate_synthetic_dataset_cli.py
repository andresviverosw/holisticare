"""CLI smoke for SYNTH-01 generate script (no DB)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.generate_synthetic_dataset import main


def test_generate_cli_writes_dataset(tmp_path: Path):
    out = tmp_path / "dataset.json"
    code = main(["--seed", "1", "--variants", "1", "--out", str(out)])
    assert code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["dataset_version"] == "v1"
    assert payload["manifest"]["patient_count"] == 8
    assert out.stat().st_size > 1000
