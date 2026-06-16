from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from conftest import ROOT
from paper_workbench.compatibility import compatibility_matrix_markdown, compatibility_report, inspect_workspace
from paper_workbench.migration import plan_legacy_migration, run_legacy_migration


FIXTURES = ROOT / "tests" / "fixtures" / "workspaces"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "paper_workbench.cli", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def copy_fixture(name: str, tmp_path: Path) -> Path:
    target = tmp_path / name
    shutil.copytree(FIXTURES / name, target)
    return target


def codes(inspection) -> set[str]:
    return {finding.code for finding in inspection.findings}


def test_inspect_v0_1_legacy_fixture_is_migratable() -> None:
    inspection = inspect_workspace(FIXTURES / "v0_1_legacy_data")

    assert inspection.workspace_type == "legacy_data_workflow"
    assert inspection.approximate_version == "v0.1-v0.9 legacy data workflow"
    assert inspection.migration_needed
    assert inspection.migratable
    assert not inspection.errors
    assert "Compatibility Inspection Report" in compatibility_report(inspection)


def test_inspect_project_profile_generations() -> None:
    early = inspect_workspace(FIXTURES / "v0_2_project_profiles")
    v2 = inspect_workspace(FIXTURES / "v2_0_rc_workspace")
    v3 = inspect_workspace(FIXTURES / "v3_0_rc_workspace")

    assert early.workspace_type == "project_profile_workspace"
    assert early.approximate_version == "v0.2 early project-profile workflow"
    assert "v2.0 dogfood" in v2.approximate_version
    assert "v3.0rc-or-newer" in v3.approximate_version
    assert not v3.errors


def test_inspect_malformed_fixtures_reports_helpful_errors() -> None:
    missing_registry = inspect_workspace(FIXTURES / "malformed_missing_registry")
    broken_notes = inspect_workspace(FIXTURES / "malformed_broken_notes")

    assert "project_registry_missing" in codes(missing_registry)
    assert missing_registry.requires_manual_review
    assert "note_parse_warning" in codes(broken_notes)
    assert broken_notes.requires_manual_review


def test_inspect_extra_columns_and_unsafe_pdf_paths() -> None:
    inspection = inspect_workspace(FIXTURES / "extra_columns_registry")

    assert "extra_registry_columns" in codes(inspection)
    assert "unsafe_local_pdf_path" in codes(inspection)
    assert inspection.registry_observations[0].extra_columns == ["reviewer_private_code", "legacy_score"]
    assert inspection.requires_manual_review


def test_inspect_rejects_project_profile_path_traversal() -> None:
    inspection = inspect_workspace(FIXTURES / "path_traversal_workspace")

    assert "project_profile_path_escape" in codes(inspection)
    assert inspection.errors
    assert not inspection.migratable


def test_partial_migration_conflict_blocks_default_target() -> None:
    inspection = inspect_workspace(FIXTURES / "partial_migration_conflict")
    plan = plan_legacy_migration(root=FIXTURES / "partial_migration_conflict", to_project="migrated_review")

    assert "partial_migration_workspace" in codes(inspection)
    assert "migration_target_conflict" in codes(inspection)
    assert not inspection.migratable
    assert plan.conflicts


def test_legacy_migration_dry_run_and_force_preserve_extra_columns(tmp_path: Path) -> None:
    workspace = copy_fixture("extra_columns_registry", tmp_path)

    dry_plan, dry_backup = run_legacy_migration(root=workspace, to_project="migrated_extra", dry_run=True)
    assert dry_plan.dry_run
    assert dry_backup is None
    assert not (workspace / "projects" / "migrated_extra").exists()

    applied, backup = run_legacy_migration(root=workspace, to_project="migrated_extra", dry_run=False, force=True)
    migrated_registry = workspace / "projects" / "migrated_extra" / "registry.csv"

    assert not applied.dry_run
    assert backup is not None
    assert migrated_registry.exists()
    migrated_text = migrated_registry.read_text(encoding="utf-8")
    assert "reviewer_private_code" in migrated_text
    assert "keep-me" in migrated_text
    assert (workspace / "data" / "registries" / "papers.csv").exists()


def test_compatibility_cli_smoke_and_report_output(tmp_path: Path) -> None:
    report = tmp_path / "compatibility.md"
    matrix = tmp_path / "matrix.md"

    help_result = run_cli("compatibility", "--help")
    inspect_result = run_cli("compatibility", "inspect", str(FIXTURES / "v0_1_legacy_data"))
    report_result = run_cli("compatibility", "report", str(FIXTURES / "v0_1_legacy_data"), "--out", str(report))
    matrix_result = run_cli("compatibility", "matrix", "--out", str(matrix))

    assert help_result.returncode == 0
    assert "inspect" in help_result.stdout
    assert inspect_result.returncode == 0, inspect_result.stderr
    assert "legacy_data_workflow" in inspect_result.stdout
    assert report_result.returncode == 0, report_result.stderr
    assert "Compatibility Inspection Report" in report.read_text(encoding="utf-8")
    assert matrix_result.returncode == 0, matrix_result.stderr
    assert "Compatibility Matrix" in matrix.read_text(encoding="utf-8")


def test_compatibility_cli_strict_returns_nonzero_for_errors() -> None:
    result = run_cli("compatibility", "inspect", str(FIXTURES / "path_traversal_workspace"), "--strict")

    assert result.returncode == 1
    assert "project_profile_path_escape" in result.stdout


def test_compatibility_matrix_mentions_historical_shapes() -> None:
    matrix = compatibility_matrix_markdown()

    assert "legacy data/ workflow" in matrix
    assert "v2.0rc dogfood workspace" in matrix
    assert "workspace with extra registry columns" in matrix
