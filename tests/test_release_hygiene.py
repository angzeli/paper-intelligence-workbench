from __future__ import annotations

from conftest import ROOT
from paper_workbench.exports import report_index_markdown


def test_ci_workflow_runs_release_gates():
    workflow = ROOT / ".github" / "workflows" / "ci.yml"
    content = workflow.read_text(encoding="utf-8")

    assert "python -m pytest -q" in content
    assert "python scripts/validate_notebooks.py" in content
    assert 'python -c "import paper_workbench"' in content
    assert "python -m paper_workbench.cli --help" in content
    assert "python -m paper_workbench.cli files --help" in content
    assert "python -m paper_workbench.cli files scan --project zis_photocatalysis" in content
    assert "python -m paper_workbench.cli files audit --project zis_photocatalysis" in content
    assert '["git", "ls-files"]' in content


def test_versioned_hostile_review_drafts_are_ignored_but_latest_is_not():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert "reports/hostile_review_v0_*.md" in ignore
    assert "reports/hostile_review_latest.md" not in ignore


def test_report_index_groups_current_historical_and_next_reports(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    for name in (
        "evidence_matrix_v0_6.md",
        "release_readiness_v0_6.md",
        "v0_6_recommended_patch_plan.md",
        "v0_7_recommended_patch_plan.md",
        "inventory_v0_2.md",
        "inventory.md",
        "hostile_review_latest.md",
        "hostile_review_v0_2.md",
    ):
        (reports_dir / name).write_text(f"# {name}\n", encoding="utf-8")

    index = report_index_markdown(reports_dir, output_path=tmp_path / "index.md")

    assert "## Current v0.6 Release Reports" in index
    assert "[evidence_matrix_v0_6.md]" in index
    assert "[release_readiness_v0_6.md]" in index
    assert "## Next Patch Plan" in index
    assert "[v0_7_recommended_patch_plan.md]" in index
    assert "## Historical Versioned Reports" in index
    assert "[inventory_v0_2.md]" in index
    assert "[v0_6_recommended_patch_plan.md]" in index
    assert "## Legacy Unversioned Reports" in index
    assert "[inventory.md]" in index
    assert "[hostile_review_latest.md]" in index
    assert "hostile_review_v0_2.md" not in index


def test_report_index_treats_v1_reports_as_current(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    for name in (
        "release_readiness_v1_1.md",
        "draft_audit_v1_1.md",
        "release_readiness_v1_0_rc.md",
        "release_readiness_v0_10.md",
        "v1_2_recommended_patch_plan.md",
        "hostile_review_latest.md",
    ):
        (reports_dir / name).write_text(f"# {name}\n", encoding="utf-8")

    index = report_index_markdown(reports_dir, output_path=tmp_path / "index.md")

    assert "## Current v1.1 Release Reports" in index
    assert "[release_readiness_v1_1.md]" in index
    assert "[draft_audit_v1_1.md]" in index
    assert "## Next Patch Plan" in index
    assert "[v1_2_recommended_patch_plan.md]" in index
    assert "release_readiness_v1_0_rc.md" in index


def test_active_generated_reports_do_not_leak_maintainer_absolute_paths():
    checked_reports = [
        "reports/import_zotero_csv_v0_4.md",
        "reports/import_generic_csv_v0_4.md",
        "reports/import_bibtex_v0_4.md",
        "reports/import_ris_v0_4.md",
        "reports/stress_workspace_health_v0_3.md",
    ]

    for relative in checked_reports:
        content = (ROOT / relative).read_text(encoding="utf-8")
        assert "/Users/" not in content, relative
        assert "/private/tmp" not in content, relative
