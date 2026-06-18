from __future__ import annotations

from conftest import ROOT
from paper_workbench import __version__
from scripts import check_docs


def test_docs_site_source_sections_exist() -> None:
    expected = [
        "docs/getting-started/index.md",
        "docs/concepts/index.md",
        "docs/workflows/index.md",
        "docs/workflows/full-literature-review-walkthrough.md",
        "docs/command-reference/index.md",
        "docs/reports/index.md",
        "docs/safety/index.md",
        "docs/development/index.md",
        "docs/cookbook/index.md",
        "docs/troubleshooting/index.md",
    ]

    for relative in expected:
        path = ROOT / relative
        assert path.exists(), relative
        assert path.read_text(encoding="utf-8").startswith("#")


def test_docs_checker_passes_for_public_docs() -> None:
    assert check_docs.main([]) == 0


def test_v3_docs_match_current_version_label() -> None:
    assert __version__ == "3.5"
    stable_surface = (ROOT / "docs" / "STABLE_SURFACE_V3.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP_V3.md").read_text(encoding="utf-8")

    assert "v3.5" in stable_surface
    assert "v3.5 Private Dogfooding Adapter" in roadmap
    assert "v3.4 Documentation Site Source" in roadmap
