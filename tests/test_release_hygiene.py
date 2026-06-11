from __future__ import annotations

from conftest import ROOT
from paper_workbench import __version__
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


def test_checked_in_report_index_matches_latest_generated_reports():
    index_path = ROOT / "reports" / "index.md"
    content = index_path.read_text(encoding="utf-8")
    generated = report_index_markdown(ROOT / "reports", output_path=index_path)

    assert content == generated
    assert "## Current v1.7 Release Reports" in content
    assert "[template_photocatalysis_overview.md]" in content
    assert "[template_finance_overview.md]" in content
    assert "[template_ml_methods_overview.md]" in content
    assert "[dogfooding_workflow_v1_7.md]" in content
    assert "[release_readiness_v1_7.md]" in content
    assert "## Next Patch Plan" in content
    assert "[v1_8_recommended_patch_plan.md]" in content
    current_section = content.split("## Current v1.7 Release Reports", 1)[1].split("## Next Patch Plan", 1)[0]
    legacy_section = content.split("## Legacy Unversioned Reports", 1)[1]
    for report in (
        "template_photocatalysis_overview.md",
        "template_finance_overview.md",
        "template_ml_methods_overview.md",
    ):
        assert f"[{report}]" in current_section
        assert f"[{report}]" not in legacy_section


def test_local_build_artifacts_do_not_claim_stale_versions():
    dist = ROOT / "dist"
    if dist.exists():
        stale_dist = [
            path.name
            for path in dist.iterdir()
            if path.is_file()
            and path.name.startswith("paper_intelligence_workbench-")
            and __version__ not in path.name
        ]
        assert not stale_dist

    pkg_info = ROOT / "paper_intelligence_workbench.egg-info" / "PKG-INFO"
    if pkg_info.exists():
        assert f"Version: {__version__}" in pkg_info.read_text(encoding="utf-8")


def test_v1_4_manuscript_docs_are_wired_into_release_docs():
    docs_index = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")
    site_map = (ROOT / "docs" / "SITE_MAP.md").read_text(encoding="utf-8")
    report_matrix = (ROOT / "docs" / "REPORT_MATRIX.md").read_text(encoding="utf-8")
    test_matrix = (ROOT / "docs" / "TEST_MATRIX.md").read_text(encoding="utf-8")

    for expected in ("MANUSCRIPT_QA.md", "CITATION_CONTEXT_TABLE.md", "CLAIM_TRACEABILITY.md", "MANUSCRIPT_LIMITATIONS.md"):
        assert expected in docs_index
        assert expected in site_map
    for expected in ("Manuscript QA", "Citation context table", "Claim traceability", "Manuscript revision checklist"):
        assert expected in report_matrix
    assert "Manuscript QA" in test_matrix
    assert "tests/test_manuscript_v1_4.py" in test_matrix


def test_v1_6_dashboard_docs_and_smoke_are_wired_into_release_docs():
    cli_surface = (ROOT / "docs" / "CLI_SURFACE.md").read_text(encoding="utf-8")
    command_contracts = (ROOT / "docs" / "COMMAND_CONTRACTS.md").read_text(encoding="utf-8")
    report_matrix = (ROOT / "docs" / "REPORT_MATRIX.md").read_text(encoding="utf-8")
    report_gallery = (ROOT / "docs" / "REPORT_GALLERY.md").read_text(encoding="utf-8")
    test_matrix = (ROOT / "docs" / "TEST_MATRIX.md").read_text(encoding="utf-8")
    smoke_script = (ROOT / "scripts" / "smoke_cli_workflow.py").read_text(encoding="utf-8")

    assert "paperwb dashboard" in cli_surface
    assert "dashboard" in command_contracts
    assert "Terminal dashboard" in report_matrix
    assert "reports/dashboard_v1_6.md" in report_gallery
    assert "tests/test_dashboard_v1_6.py" in test_matrix
    assert "dashboard next actions" in smoke_script
    assert "--no-audit-log" in smoke_script


def test_v1_7_template_docs_and_smoke_are_wired_into_release_docs():
    docs_index = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")
    site_map = (ROOT / "docs" / "SITE_MAP.md").read_text(encoding="utf-8")
    cli_surface = (ROOT / "docs" / "CLI_SURFACE.md").read_text(encoding="utf-8")
    command_contracts = (ROOT / "docs" / "COMMAND_CONTRACTS.md").read_text(encoding="utf-8")
    test_matrix = (ROOT / "docs" / "TEST_MATRIX.md").read_text(encoding="utf-8")
    smoke_script = (ROOT / "scripts" / "smoke_cli_workflow.py").read_text(encoding="utf-8")

    for expected in ("PROJECT_TEMPLATES.md", "DOGFOODING_WORKFLOW.md"):
        assert expected in docs_index
        assert expected in site_map
    assert "paperwb template" in cli_surface
    assert "`template`" in command_contracts
    assert "tests/test_templates_v1_7.py" in test_matrix
    assert "template create" in smoke_script


def test_active_generated_reports_do_not_leak_maintainer_absolute_paths():
    checked_reports = [
        "reports/import_zotero_csv_v0_4.md",
        "reports/import_generic_csv_v0_4.md",
        "reports/import_bibtex_v0_4.md",
        "reports/import_ris_v0_4.md",
        "reports/stress_workspace_health_v0_3.md",
        "reports/sync_plan_v1_3.md",
        "reports/sync_conflicts_v1_3.md",
        "reports/sync_apply_dry_run_v1_3.md",
        "reports/obsidian_roundtrip_v1_3.md",
    ]

    for relative in checked_reports:
        content = (ROOT / relative).read_text(encoding="utf-8")
        assert "/Users/" not in content, relative
        assert "/private/tmp" not in content, relative
