from __future__ import annotations

import subprocess

from conftest import ROOT
from paper_workbench import __version__
from paper_workbench.exports import report_index_markdown
from paper_workbench.safety import ABSOLUTE_PATH_WARNING_ALLOWLIST, audit_data_safety


def test_ci_workflow_runs_release_gates():
    workflow = ROOT / ".github" / "workflows" / "ci.yml"
    content = workflow.read_text(encoding="utf-8")

    assert "python scripts/run_quality_gate.py release" in content
    assert 'python-version: ["3.10", "3.11", "3.12"]' in content
    assert 'python -c "import paper_workbench; print(paper_workbench.__version__)"' in content


def test_versioned_hostile_review_drafts_are_ignored_but_latest_is_not():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert "reports/hostile_review_v0_*.md" in ignore
    assert "reports/hostile_review_latest.md" not in ignore


def test_data_safety_absolute_path_allowlist_keeps_current_audit_clear():
    result = audit_data_safety(ROOT)

    assert not result.errors
    assert not [finding for finding in result.warnings if finding.code == "absolute_local_path"]
    assert "reports/hostile_review_v0_4.md" in ABSOLUTE_PATH_WARNING_ALLOWLIST


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


def test_report_index_keeps_rc_reports_current_with_post_roadmap(tmp_path):
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    for name in (
        "release_readiness_v3_0_rc.md",
        "data_safety_v3_0_rc.md",
        "post_v3_0_roadmap.md",
        "release_readiness_v2_6.md",
    ):
        (reports_dir / name).write_text(f"# {name}\n", encoding="utf-8")

    index = report_index_markdown(reports_dir, output_path=tmp_path / "index.md")

    assert "## Current v3.0 Release Reports" in index
    current_section = index.split("## Current v3.0 Release Reports", 1)[1]
    current_section = current_section.split("## Historical Versioned Reports", 1)[0]
    assert "[release_readiness_v3_0_rc.md]" in current_section
    assert "[data_safety_v3_0_rc.md]" in current_section
    assert "[post_v3_0_roadmap.md]" in current_section
    assert "[release_readiness_v2_6.md]" not in current_section


def test_checked_in_report_index_matches_latest_generated_reports():
    index_path = ROOT / "reports" / "index.md"
    content = index_path.read_text(encoding="utf-8")
    generated = report_index_markdown(ROOT / "reports", output_path=index_path)

    assert content == generated
    assert "## Current v3.5 Release Reports" in content
    current_section = content.split("## Current v3.5 Release Reports", 1)[1]
    current_section = current_section.split("## Next Patch Plan", 1)[0]
    current_section = current_section.split("## Historical Versioned Reports", 1)[0]
    assert "[hostile_review_latest.md]" in current_section
    assert "[private_dogfooding_adapter_v3_5.md]" in current_section
    assert "[external_workspace_safety_v3_5.md]" in current_section
    assert "[release_readiness_v3_5.md]" in current_section
    assert "[release_notes_v2_0_rc.md]" not in current_section
    assert "[release_readiness_v2_0_rc.md]" not in current_section
    historical_section = content.split("## Historical Versioned Reports", 1)[1]
    assert "[docs_audit_v3_4.md]" in historical_section
    assert "[cookbook_inventory_v3_4.md]" in historical_section
    assert "[command_reference_audit_v3_4.md]" in historical_section
    assert "[release_readiness_v3_4.md]" in historical_section
    assert "[quality_gate_v3_3.md]" in historical_section
    assert "[ci_matrix_v3_3.md]" in historical_section
    assert "[type_lint_summary_v3_3.md]" in historical_section
    assert "[release_readiness_v3_3.md]" in historical_section
    assert "[compatibility_matrix_v3_2.md]" in historical_section
    assert "[legacy_migration_dry_run_v3_2.md]" in historical_section
    assert "[partial_migration_conflict_v3_2.md]" in historical_section
    assert "[schema_preservation_v3_2.md]" in historical_section
    assert "[release_readiness_v3_2.md]" in historical_section
    assert "[support_bundle_demo_v3_1.md]" in historical_section
    assert "[support_bundle_data_safety_v3_1.md]" in historical_section
    assert "[redaction_preview_v3_1.md]" in historical_section
    assert "[release_readiness_v3_1.md]" in historical_section
    assert "[release_notes_v3_0_rc.md]" in historical_section
    assert "[release_readiness_v3_0_rc.md]" in historical_section
    assert "[final_release_verdict_v3_0_rc.md]" in historical_section
    assert "[external_dogfooding_simulation_v3_0_rc.md]" in historical_section
    assert "[data_safety_v3_0_rc.md]" in historical_section
    assert "[architecture_audit_v2_6.md]" in historical_section
    assert "[behavior_preservation_v2_6.md]" in historical_section
    assert "[refactor_summary_v2_6.md]" in historical_section
    assert "[release_readiness_v2_6.md]" in historical_section
    assert "[release_readiness_v2_5.md]" in historical_section
    assert "[performance_sanity_v2_5.md]" in historical_section
    assert "[incremental_rebuild_plan_v2_5.md]" in historical_section
    assert "[release_readiness_v2_4.md]" in historical_section
    assert "[release_readiness_v2_3.md]" in historical_section
    assert "[release_readiness_v2_2.md]" in historical_section
    assert "[release_readiness_v2_1.md]" in historical_section
    assert "[release_readiness_v2_0.md]" in historical_section
    assert "[dogfooding_project_template_v2_0.md]" in historical_section
    assert "[release_notes_v2_0_rc.md]" in historical_section
    assert "[release_readiness_v2_0_rc.md]" in historical_section


def test_public_quickstarts_use_clean_demo_and_label_zis_as_imperfect():
    docs = [
        ROOT / "README.md",
        ROOT / "docs" / "GETTING_STARTED_V2.md",
        ROOT / "docs" / "EXTERNAL_USER_QUICKSTART.md",
        ROOT / "docs" / "QUICKSTART_EXTERNAL_USER.md",
    ]
    for path in docs:
        content = path.read_text(encoding="utf-8")
        assert "validate-registry projects/clean_demo/registry.csv --strict" in content
        assert (
            "validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict"
            in content
        )
        assert "zis_photocatalysis" in content
    getting_started = (ROOT / "docs" / "GETTING_STARTED_V2.md").read_text(encoding="utf-8")
    assert "intentionally imperfect" in getting_started
    assert "green first-run validation path" in getting_started


def test_command_contracts_document_non_strict_validation_exit_behavior():
    content = (ROOT / "docs" / "COMMAND_CONTRACTS_V2.md").read_text(encoding="utf-8")

    assert "Validation and audit commands default to review mode" in content
    assert "Use `--strict` in CI" in content
    assert "`0` with printed `ERROR` findings" in content


def test_manifest_includes_public_docs_examples_and_fixtures():
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    for required in [
        "include AGENTS.md",
        "include CHANGELOG.md",
        "include CONTRIBUTING.md",
        "graft data",
        "graft docs",
        "graft drafts",
        "graft examples",
        "graft notebooks",
        "graft projects",
        "graft reports",
        "graft scripts",
        "graft tests/fixtures",
        "include tests/conftest.py",
    ]:
        assert required in manifest
    for excluded in [
        "prune .paperwb",
        "prune build",
        "prune dist",
        "prune scratch",
        "recursive-exclude projects */.paperwb/*",
        "global-exclude audit_log.jsonl",
        "global-exclude *.pdf",
        "global-exclude *.sqlite",
        "global-exclude *.db",
        "exclude reports/hostile_review_v0_*.md",
    ]:
        assert excluded in manifest


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
    tracked_pkg_info = subprocess.run(
        ["git", "ls-files", str(pkg_info.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    ).stdout.strip()
    if pkg_info.exists() and tracked_pkg_info:
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
