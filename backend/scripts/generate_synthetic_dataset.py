"""
generate_synthetic_dataset.py — write SYNTH-01 dataset package to disk.

Usage (from backend/ or via pythonpath):
    python -m scripts.generate_synthetic_dataset
    python -m scripts.generate_synthetic_dataset --variants 10 --seed 42
    python -m scripts.generate_synthetic_dataset --out data/synthetic/v1/dataset.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.synthetic.generator import (  # noqa: E402
    DEFAULT_SEED,
    DEFAULT_VARIANTS_PER_ARCHETYPE,
    dataset_to_dict,
    generate_synthetic_dataset,
)

DEFAULT_OUT = Path(__file__).parent.parent / "data" / "synthetic" / "v1" / "dataset.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate HolistiCare SYNTH-01 dataset JSON.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--variants",
        type=int,
        default=DEFAULT_VARIANTS_PER_ARCHETYPE,
        help="Variants per archetype (4 → 32 patients; 10 → 80 patients).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output JSON path.",
    )
    args = parser.parse_args(argv)

    ds = generate_synthetic_dataset(seed=args.seed, variants_per_archetype=args.variants)
    payload = dataset_to_dict(ds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    m = payload["manifest"]
    print(
        f"OK: wrote {args.out} "
        f"(patients={m['patient_count']} diary={m['diary_entry_count']} "
        f"sessions={m['session_count']} memory_bank={m['memory_bank_count']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
