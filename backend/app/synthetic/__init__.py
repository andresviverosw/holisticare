"""
SYNTH-01 — deterministic synthetic clinical dataset for HolistiCare demos/tests.

Generates intake → plans → sessions → diary journeys that exercise analytics,
plateau flags, recovery trajectories, and memory-bank packaging.
"""

from app.synthetic.generator import (
    DEFAULT_SEED,
    DEFAULT_VARIANTS_PER_ARCHETYPE,
    dataset_to_dict,
    generate_synthetic_dataset,
)

__all__ = [
    "DEFAULT_SEED",
    "DEFAULT_VARIANTS_PER_ARCHETYPE",
    "dataset_to_dict",
    "generate_synthetic_dataset",
]
