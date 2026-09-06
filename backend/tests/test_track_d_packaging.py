"""Track D packaging — required thesis appendix artifacts must exist in the repo."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "relative_path",
    [
        "docs/thesis-appendix-index.md",
        "docs/01-requirements-and-domain-research.md",
        "docs/02-system-architecture.md",
        "docs/03-data-dictionary-and-privacy-framework.md",
        "docs/04-feature-specs-and-user-stories.md",
        "docs/05-test-plan.md",
        "docs/06-deployment-and-ops-runbook.md",
        "docs/rag-evaluation-report.md",
        "docs/feedback-01-synthetic-demo-waiver.md",
        "docs/deploy-final-demo.md",
        "docs/demo-01-public-walkthrough.md",
        "README.md",
        "CHANGELOG.md",
    ],
)
def test_track_d_appendix_artifact_exists(relative_path: str) -> None:
    path = REPO_ROOT / relative_path
    assert path.is_file(), f"Track D missing required artifact: {relative_path}"


def test_readme_documents_public_demo_urls() -> None:
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "holisticare-frontend.onrender.com" in text
    assert "holisticare-api.onrender.com" in text
    assert "Quick start" in text or "quick start" in text.lower()


def test_thesis_appendix_index_links_phases_and_demo() -> None:
    text = (REPO_ROOT / "docs/thesis-appendix-index.md").read_text(encoding="utf-8")
    assert "01-requirements-and-domain-research.md" in text
    assert "demo-01-public-walkthrough.md" in text
    assert "capstone-final" in text
    assert "feedback-01-synthetic-demo-waiver.md" in text
