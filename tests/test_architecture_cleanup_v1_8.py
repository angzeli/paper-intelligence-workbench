from __future__ import annotations

from pathlib import Path

from paper_workbench.exports import export_theme_claims, report_index_markdown
from paper_workbench.index import display_path as indexed_display_path
from paper_workbench.paths import display_path
from paper_workbench.schema import Claim
from paper_workbench.search import results_markdown
from paper_workbench.tags import normalize_tag, normalize_theme_id


def test_display_path_shared_by_search_and_index_markdown(tmp_path: Path) -> None:
    base = tmp_path / "workspace"
    note = base / "notes" / "paper.md"
    note.parent.mkdir(parents=True)
    note.write_text("# Synthetic note\n", encoding="utf-8")

    assert display_path(note, base_path=base) == "notes/paper.md"
    assert indexed_display_path(note, base_path=base) == "notes/paper.md"
    assert "| note | n1 | Synthetic | notes/paper.md |" in results_markdown(
        [{"kind": "note", "id": "n1", "title": "Synthetic", "path": str(note)}],
        "synthetic",
        base_path=base,
    )


def test_theme_id_normalization_matches_tag_normalization() -> None:
    assert normalize_theme_id("Charge Separation") == normalize_tag("Charge Separation")
    assert normalize_theme_id("charge_separation") == "charge-separation"


def test_theme_claim_export_uses_shared_theme_normalization(tmp_path: Path) -> None:
    out = tmp_path / "claims.json"
    claim = Claim(
        claim_id="c1",
        paper_id="p1",
        claim_text="Synthetic claim.",
        supports_theme="Charge Separation",
    )

    export_theme_claims([claim], out, theme="charge_separation", force=False)

    assert "Synthetic claim." in out.read_text(encoding="utf-8")


def test_v1_8_report_index_groups_current_architecture_reports(tmp_path: Path) -> None:
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    for name in (
        "architecture_review_v1_8.md",
        "release_readiness_v1_8.md",
        "release_readiness_v1_7.md",
        "v1_9_recommended_patch_plan.md",
        "hostile_review_latest.md",
    ):
        (reports_dir / name).write_text(f"# {name}\n", encoding="utf-8")

    index = report_index_markdown(reports_dir, output_path=reports_dir / "index.md")
    current = index.split("## Current v1.8 Release Reports", 1)[1].split("## Next Patch Plan", 1)[0]

    assert "[architecture_review_v1_8.md]" in current
    assert "[release_readiness_v1_8.md]" in current
    assert "[hostile_review_latest.md]" in current
    assert "[v1_9_recommended_patch_plan.md]" in index
