from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from paper_workbench.auditlog import append_audit_event, clear_audit_log, default_audit_log_path, load_audit_events
from paper_workbench.backups import create_backup, list_backups, plan_restore, restore_backup
from paper_workbench.integrity import check_workspace_integrity, is_path_within, workspace_integrity_report
from paper_workbench.io import write_text
from paper_workbench.migration import plan_legacy_migration, run_legacy_migration
from paper_workbench.registry import save_registry
from paper_workbench.schema import Author, Paper, ValidationFinding


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], check=False, text=True, capture_output=True)


def make_legacy_workspace(root: Path) -> dict[str, Path]:
    registry = root / "data" / "registries" / "papers.csv"
    bibtex = root / "data" / "bibtex" / "library.bib"
    notes = root / "data" / "notes"
    themes = root / "data" / "examples" / "themes.json"
    reports = root / "reports"
    notes.mkdir(parents=True)
    bibtex.parent.mkdir(parents=True)
    themes.parent.mkdir(parents=True)
    reports.mkdir(parents=True)
    save_registry(
        [
            Paper(
                paper_id="synthetic_safe_2026",
                title="Synthetic Safety Workflows for Local Reviews",
                authors=[Author(given="Ari", family="Example", raw_name="Ari Example")],
                year="2026",
                bibtex_key="Example2026Safety",
                reading_status="read",
                notes_path="data/notes/synthetic_safe_2026.md",
            )
        ],
        registry,
    )
    bibtex.write_text(
        "@article{Example2026Safety,\n"
        "  title={Synthetic Safety Workflows for Local Reviews},\n"
        "  author={Example, Ari},\n"
        "  year={2026},\n"
        "  journal={Synthetic Review Methods}\n"
        "}\n",
        encoding="utf-8",
    )
    (notes / "synthetic_safe_2026.md").write_text(
        "# Paper Note: Synthetic Safety Workflows for Local Reviews\n\n"
        "## Metadata\n"
        "- Paper ID: synthetic_safe_2026\n"
        "- BibTeX key: Example2026Safety\n"
        "- Reading status: read\n"
        "- Tags: safety\n\n"
        "## Claims and evidence\n\n"
        "### Claim 1\n"
        "- Claim: Synthetic backups help demonstrate restore planning.\n"
        "- Evidence type: method_description\n"
        "- Section / page: Section 2\n"
        "- Quote or paraphrase: Synthetic local workflow description.\n"
        "- Confidence: high\n"
        "- Strength: strong\n"
        "- Tags: safety\n"
        "- Supports theme: safety\n",
        encoding="utf-8",
    )
    themes.write_text('{"themes":[{"theme_id":"safety","name":"Safety","tags":["safety"],"min_claims":1,"min_papers":1}]}\n', encoding="utf-8")
    (reports / "old_report.md").write_text("# Old Report\n", encoding="utf-8")
    return {"registry": registry, "bibtex": bibtex, "notes": notes, "themes": themes, "reports": reports}


def test_integrity_detects_path_escape_and_writes_report(tmp_path):
    paths = make_legacy_workspace(tmp_path)
    result = check_workspace_integrity(
        root=tmp_path,
        registry_path=paths["registry"],
        bibtex_path=paths["bibtex"],
        notes_dir=paths["notes"],
        themes_path=Path("/private/tmp/outside_themes.json"),
        reports_dir=paths["reports"],
    )
    assert any(finding.code == "path_escapes_workspace" for finding in result.findings)
    report = workspace_integrity_report(result)
    assert "Workspace Integrity Report v0.9" in report
    assert "path_escapes_workspace" in report


def test_path_containment_helper_handles_relative_and_absolute(tmp_path):
    inside = tmp_path / "data" / "notes"
    outside = tmp_path.parent / "outside"
    assert is_path_within(inside, tmp_path)
    assert not is_path_within(outside, tmp_path)


def test_audit_log_append_load_and_force_clear(tmp_path):
    path = default_audit_log_path(tmp_path)
    append_audit_event(
        root=tmp_path,
        command="unit",
        action="write",
        affected_paths=["data/registries/papers.csv"],
        warnings=[ValidationFinding("warning", "synthetic_warning", "Synthetic warning object")],
        summary="Synthetic event",
    )
    events = load_audit_events(path)
    assert len(events) == 1
    assert events[0]["summary"] == "Synthetic event"
    assert events[0]["warnings"] == ["synthetic_warning: Synthetic warning object"]
    with pytest.raises(PermissionError):
        clear_audit_log(path)
    assert clear_audit_log(path, force=True)
    assert load_audit_events(path) == []


def test_backup_create_list_plan_and_restore_force(tmp_path):
    paths = make_legacy_workspace(tmp_path)
    manifest, backup_path = create_backup(
        root=tmp_path,
        registry_path=paths["registry"],
        bibtex_path=paths["bibtex"],
        notes_dir=paths["notes"],
        themes_path=paths["themes"],
        reports_dir=paths["reports"],
        backups_dir=tmp_path / "backups",
        notes="unit backup",
    )
    assert backup_path.exists()
    assert manifest.included_files
    assert not any(item.source_path.endswith(".pdf") for item in manifest.included_files)
    assert list_backups(tmp_path, backups_dir=tmp_path / "backups")[0].backup_id == manifest.backup_id

    original = paths["registry"].read_text(encoding="utf-8")
    paths["registry"].write_text("broken\n", encoding="utf-8")
    plan = plan_restore(root=tmp_path, backup_id=manifest.backup_id, backups_dir=tmp_path / "backups")
    assert "data/registries/papers.csv" in plan.files_to_overwrite
    restore_backup(
        root=tmp_path,
        backup_id=manifest.backup_id,
        registry_path=paths["registry"],
        bibtex_path=paths["bibtex"],
        notes_dir=paths["notes"],
        themes_path=paths["themes"],
        reports_dir=paths["reports"],
        backups_dir=tmp_path / "backups",
        force=True,
        create_pre_restore_backup=False,
    )
    assert paths["registry"].read_text(encoding="utf-8") == original


def test_migration_plan_and_force_copy_are_non_destructive(tmp_path):
    paths = make_legacy_workspace(tmp_path)
    plan = plan_legacy_migration(root=tmp_path, to_project="migrated_review")
    assert not plan.conflicts
    assert any(operation.target_path == "projects/migrated_review/registry.csv" for operation in plan.operations)

    dry_plan, backup = run_legacy_migration(root=tmp_path, to_project="migrated_review", dry_run=True)
    assert dry_plan.dry_run
    assert backup is None
    assert not (tmp_path / "projects" / "migrated_review").exists()

    applied, backup = run_legacy_migration(root=tmp_path, to_project="migrated_review", force=True, dry_run=False)
    assert not applied.dry_run
    assert backup is not None
    assert (tmp_path / "projects" / "migrated_review" / "registry.csv").exists()
    assert paths["registry"].exists()
    conflict_plan = plan_legacy_migration(root=tmp_path, to_project="migrated_review")
    assert conflict_plan.conflicts


def test_cli_integrity_backup_migration_and_audit_log_smoke(tmp_path):
    paths = make_legacy_workspace(tmp_path)
    integrity_out = tmp_path / "integrity.md"
    integrity = run_cli(
        "integrity",
        "check",
        "--registry",
        str(paths["registry"]),
        "--bibtex",
        str(paths["bibtex"]),
        "--notes-dir",
        str(paths["notes"]),
        "--themes",
        str(paths["themes"]),
        "--reports-dir",
        str(paths["reports"]),
        "--out",
        str(integrity_out),
        "--force",
    )
    assert integrity.returncode == 0, integrity.stderr
    assert integrity_out.exists()

    backup = run_cli(
        "backup",
        "create",
        "--registry",
        str(paths["registry"]),
        "--bibtex",
        str(paths["bibtex"]),
        "--notes-dir",
        str(paths["notes"]),
        "--themes",
        str(paths["themes"]),
        "--reports-dir",
        str(paths["reports"]),
        "--backups-dir",
        str(tmp_path / "backups"),
    )
    assert backup.returncode == 0, backup.stderr
    backup_id = backup.stdout.splitlines()[0].split()[-1]

    inspect_out = tmp_path / "backup_manifest.md"
    inspect = run_cli("backup", "inspect", backup_id, "--backups-dir", str(tmp_path / "backups"), "--out", str(inspect_out))
    assert inspect.returncode == 0, inspect.stderr
    assert "Backup Manifest Demo v0.9" in inspect_out.read_text(encoding="utf-8")

    restore_out = tmp_path / "restore.md"
    restore = run_cli("backup", "restore", backup_id, "--backups-dir", str(tmp_path / "backups"), "--dry-run", "--out", str(restore_out))
    assert restore.returncode == 0, restore.stderr
    assert f"Wrote {restore_out}" in restore.stdout
    assert "Dry run: true" in restore_out.read_text(encoding="utf-8")

    migration_out = tmp_path / "migration.md"
    migration = run_cli("migrate", "run", "--root", str(tmp_path), "--to-project", "cli_migrated", "--dry-run", "--out", str(migration_out))
    assert migration.returncode == 0, migration.stderr
    assert "Migration Plan v0.9" in migration_out.read_text(encoding="utf-8")

    audit_path = tmp_path / "audit.jsonl"
    write_text(audit_path, json.dumps({"timestamp": "now", "project": "", "action": "unit", "summary": "ok"}) + "\n")
    audit = run_cli("audit-log", "show", "--path", str(audit_path), "--markdown")
    assert audit.returncode == 0
    assert "Audit Log" in audit.stdout
