from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from paper_workbench.auditlog import audit_log_markdown, load_audit_events
from paper_workbench.backups import plan_restore
from paper_workbench.bibtex import parse_bibtex_file, validate_bibtex
from paper_workbench.importers import import_generic_csv, import_ris, import_zotero_csv
from paper_workbench.integrity import check_workspace_integrity
from paper_workbench.notes import parse_note_file
from paper_workbench.registry import load_registry, validate_registry, validate_registry_headers
from paper_workbench.reporting import bibtex_audit_report, evidence_map_report, inventory_report
from paper_workbench.tags import load_themes


ROOT = Path(__file__).resolve().parents[1]
ADVERSARIAL = ROOT / "tests" / "fixtures" / "adversarial"


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], check=False, text=True, capture_output=True)


def codes(findings) -> set[str]:
    return {finding.code for finding in findings}


def test_adversarial_registry_loads_and_reports_expected_findings():
    registry = ADVERSARIAL / "registries" / "malformed_registry.csv"
    papers = load_registry(registry)
    findings = validate_registry(papers, root=registry.parent)
    found = codes(findings)
    assert "duplicate_paper_id" in found
    assert "duplicate_doi" in found
    assert "invalid_reading_status" in found
    assert "invalid_year" in found
    assert "path_escapes_workspace" in found
    report = inventory_report(papers, root=registry.parent)
    assert "Registry Findings" in report
    assert "path_escapes_workspace" in report


def test_missing_registry_headers_are_actionable():
    registry = ADVERSARIAL / "registries" / "missing_headers.csv"
    findings = validate_registry_headers(registry)
    assert [finding.code for finding in findings] == ["missing_required_column"]
    assert "Next step:" in findings[0].message
    result = run_cli("validate-registry", str(registry), "--strict")
    assert result.returncode == 1
    assert "missing_required_column" in result.stdout
    assert "Next step:" in result.stdout
    assert "Traceback" not in result.stderr


def test_bibtex_torture_fixture_recovers_with_warnings():
    entries = parse_bibtex_file(ADVERSARIAL / "bibtex" / "torture.bib")
    findings = validate_bibtex(entries)
    found = codes(findings)
    assert entries
    assert "duplicate_bibtex_key" in found
    assert "duplicate_bibtex_doi" in found
    assert "bibtex_parse_warning" in found
    assert "missing_title" in found
    report = bibtex_audit_report(entries, findings)
    assert "BibTeX Audit Report" in report
    assert "bibtex_parse_warning" in report


def test_malformed_note_produces_warnings_and_parseable_claim():
    note = parse_note_file(ADVERSARIAL / "notes" / "malformed_note.md")
    assert note.paper_id == ""
    assert any("Metadata is missing Paper ID" in warning for warning in note.warnings)
    assert any("Unknown reading status" in warning for warning in note.warnings)
    assert any("Claim A is missing claim text" in warning for warning in note.warnings)
    assert any("Claim B is missing evidence location" in warning for warning in note.warnings)
    assert len(note.claims) == 1
    assert note.claims[0].paper_id == ""


def test_reports_do_not_crash_with_imperfect_notes_and_registry():
    registry = ADVERSARIAL / "registries" / "malformed_registry.csv"
    papers = load_registry(registry)
    note = parse_note_file(ADVERSARIAL / "notes" / "malformed_note.md")
    themes = load_themes(ROOT / "data" / "examples" / "themes.json")
    report = evidence_map_report(papers, note.claims, themes, [note])
    assert "Literature Review Evidence Map" in report
    assert "Missing evidence" in report


def test_import_failure_paths_have_useful_errors(tmp_path):
    zotero = import_zotero_csv
    try:
        zotero(ADVERSARIAL / "imports" / "zotero_missing_fields.csv", [], registry_path=tmp_path / "papers.csv", dry_run=True)
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected missing Title column failure")
    assert "Zotero CSV import is missing required columns" in message
    assert "Next step:" in message

    try:
        import_generic_csv(
            ADVERSARIAL / "imports" / "generic_input.csv",
            ADVERSARIAL / "imports" / "generic_bad_mapping.json",
            [],
            registry_path=tmp_path / "papers.csv",
            dry_run=True,
        )
    except ValueError as exc:
        mapping_message = str(exc)
    else:
        raise AssertionError("expected bad mapping failure")
    assert "not a registry field" in mapping_message
    assert "Why it matters:" in mapping_message

    try:
        import_generic_csv(
            ADVERSARIAL / "imports" / "generic_input.csv",
            ADVERSARIAL / "imports" / "generic_missing_column_mapping.json",
            [],
            registry_path=tmp_path / "papers.csv",
            dry_run=True,
        )
    except ValueError as exc:
        missing_message = str(exc)
    else:
        raise AssertionError("expected missing mapped source column failure")
    assert "missing source columns" in missing_message
    assert "Missing Source Column" in missing_message


def test_ris_missing_terminator_is_recovered_as_one_record(tmp_path):
    result = import_ris(ADVERSARIAL / "imports" / "ris_missing_er.ris", [], registry_path=tmp_path / "papers.csv", dry_run=True)
    assert result.rows_read == 1
    assert result.imported == 1
    assert result.registry_papers[0].title == "Synthetic RIS Without Terminator"


def test_corrupted_audit_log_and_backup_manifest_are_safe(tmp_path):
    audit_log = tmp_path / ".paperwb" / "audit_log.jsonl"
    audit_log.parent.mkdir()
    audit_log.write_text("{bad json\n" + json.dumps({"timestamp": "now", "action": "valid", "summary": "ok"}) + "\n", encoding="utf-8")
    events = load_audit_events(audit_log)
    assert events[0]["action"] == "audit_log_parse_warning"
    assert events[1]["action"] == "valid"
    assert "audit_log_parse_warning" in audit_log_markdown(events)

    backup = tmp_path / "backups" / "broken"
    backup.mkdir(parents=True)
    (backup / "manifest.json").write_text("{bad json\n", encoding="utf-8")
    try:
        plan_restore(root=tmp_path, backup_id="broken", backups_dir=tmp_path / "backups")
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected corrupt manifest failure")
    assert "Backup manifest is not valid JSON" in message
    assert "Next step:" in message


def test_integrity_detects_broken_project_profile_paths(tmp_path):
    projects = tmp_path / "projects"
    shutil.copytree(ADVERSARIAL / "projects" / "broken_project", projects / "broken_project")
    result = check_workspace_integrity(root=tmp_path)
    assert "project_profile_path_escape" in codes(result.findings)


def test_cli_failure_paths_do_not_traceback(tmp_path):
    bad_mapping = run_cli(
        "import",
        "csv",
        str(ADVERSARIAL / "imports" / "generic_input.csv"),
        "--mapping",
        str(ADVERSARIAL / "imports" / "generic_bad_mapping.json"),
        "--registry",
        str(tmp_path / "papers.csv"),
        "--dry-run",
    )
    assert bad_mapping.returncode == 2
    assert "not a registry field" in bad_mapping.stderr
    assert "Next step:" in bad_mapping.stderr
    assert "Traceback" not in bad_mapping.stderr

    missing_project = run_cli("project", "validate", "does_not_exist")
    assert missing_project.returncode == 2
    assert "project profile not found" in missing_project.stderr
    assert "Traceback" not in missing_project.stderr

    restore = run_cli("backup", "restore", "missing_backup", "--dry-run")
    assert restore.returncode == 2
    assert "backup not found" in restore.stderr
    assert "Traceback" not in restore.stderr
