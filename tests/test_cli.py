from __future__ import annotations

import json
import subprocess
import sys

from conftest import EXAMPLE_BIBTEX, EXAMPLE_NOTES, EXAMPLE_REGISTRY, EXAMPLE_THEMES, ROOT
from paper_workbench.registry import save_registry
from paper_workbench.schema import Author, Paper


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], check=False, text=True, capture_output=True)


def test_cli_help_smoke():
    result = run_cli("--help")
    assert result.returncode == 0
    assert "paperwb" in result.stdout


def test_cli_validate_registry_smoke():
    result = run_cli("validate-registry", str(EXAMPLE_REGISTRY))
    assert result.returncode == 0
    assert "duplicate_doi" in result.stdout


def test_cli_claims_output(tmp_path):
    target = tmp_path / "claims.csv"
    result = run_cli("claims", str(EXAMPLE_NOTES), "--output", str(target))
    assert result.returncode == 0
    assert target.exists()
    assert "Wrote 3 claims" in result.stdout


def test_cli_report_smoke(tmp_path):
    result = run_cli(
        "report",
        "citation-audit",
        "--registry",
        str(EXAMPLE_REGISTRY),
        "--bibtex",
        str(EXAMPLE_BIBTEX),
        "--notes-dir",
        str(EXAMPLE_NOTES),
        "--themes",
        str(EXAMPLE_THEMES),
        "--reports-dir",
        str(tmp_path),
    )
    assert result.returncode == 0
    assert (tmp_path / "citation_audit.md").exists()


def test_cli_inventory_report_uses_registry_validation_context(tmp_path):
    registry = tmp_path / "papers.csv"
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    save_registry(
        [
            Paper(
                paper_id="context_probe",
                title="Synthetic Context Probe",
                authors=[Author(given="Test", family="Author", raw_name="Test Author")],
                year="2026",
                local_pdf_path="missing/context_probe.pdf",
                bibtex_key="contextProbe2026",
                reading_status="read",
                notes_path=str(tmp_path / "missing_note.md"),
                included_in_lit_review="true",
            )
        ],
        registry,
    )
    out = tmp_path / "inventory.md"
    result = run_cli("report", "inventory", "--registry", str(registry), "--notes-dir", str(notes_dir), "--out", str(out), "--force")
    assert result.returncode == 0, result.stderr
    content = out.read_text(encoding="utf-8")
    assert "missing_local_pdf_path" in content
    assert "notes_path_missing_file" in content
    assert "included_without_claims" in content


def test_cli_init_smoke(tmp_path):
    result = run_cli("init", "--root", str(tmp_path))
    assert result.returncode == 0
    assert (tmp_path / "data" / "registries" / "papers.csv").exists()


def test_cli_project_search_and_report_smoke(tmp_path):
    search = run_cli("search", "photocorrosion", "--project", "zis_photocatalysis")
    assert search.returncode == 0
    assert "zis_stability_2024" in search.stdout
    report = run_cli(
        "report",
        "section-outline",
        "--project",
        "zis_photocatalysis",
        "--theme",
        "photocorrosion",
        "--out",
        str(tmp_path / "outline.md"),
    )
    assert report.returncode == 0
    assert (tmp_path / "outline.md").exists()


def test_cli_doctor_and_export_smoke(tmp_path):
    doctor = run_cli("doctor", "--project", "zis_photocatalysis", "--out", str(tmp_path / "health.md"))
    assert doctor.returncode == 0
    assert (tmp_path / "health.md").exists()
    export = run_cli("export", "claims-json", "--project", "zis_photocatalysis", "--out", str(tmp_path / "claims.json"))
    assert export.returncode == 0
    assert (tmp_path / "claims.json").exists()


def test_cli_missing_inputs_return_user_facing_errors(tmp_path):
    missing_registry = tmp_path / "missing.csv"
    result = run_cli("validate-registry", str(missing_registry))
    assert result.returncode == 2
    assert "error:" in result.stderr
    assert "Traceback" not in result.stderr

    bad_status = run_cli("add-paper", "--registry", str(tmp_path / "papers.csv"), "--title", "Synthetic", "--status", "invalid_status")
    assert bad_status.returncode == 2
    assert "Traceback" not in bad_status.stderr

    duplicate_project = run_cli("project", "init", "finance_reading")
    assert duplicate_project.returncode == 2
    assert "Traceback" not in duplicate_project.stderr


def test_report_missing_registry_does_not_create_empty_file(tmp_path):
    missing_registry = tmp_path / "missing_registry.csv"
    out = tmp_path / "evidence_map.md"
    result = run_cli(
        "report",
        "evidence-map",
        "--registry",
        str(missing_registry),
        "--bibtex",
        str(EXAMPLE_BIBTEX),
        "--notes-dir",
        str(EXAMPLE_NOTES),
        "--themes",
        str(EXAMPLE_THEMES),
        "--out",
        str(out),
    )
    assert result.returncode == 2
    assert not missing_registry.exists()
    assert not out.exists()
    assert "Traceback" not in result.stderr


def test_report_and_export_refuse_overwrite_without_force(tmp_path):
    report_out = tmp_path / "inventory.md"
    report_out.write_text("keep me", encoding="utf-8")
    report = run_cli("report", "inventory", "--registry", str(EXAMPLE_REGISTRY), "--out", str(report_out))
    assert report.returncode == 2
    assert report_out.read_text(encoding="utf-8") == "keep me"

    forced_report = run_cli("report", "inventory", "--registry", str(EXAMPLE_REGISTRY), "--out", str(report_out), "--force")
    assert forced_report.returncode == 0
    assert "Paper Inventory Report" in report_out.read_text(encoding="utf-8")

    export_out = tmp_path / "claims.json"
    export_out.write_text("keep me", encoding="utf-8")
    export = run_cli("export", "claims-json", "--project", "zis_photocatalysis", "--out", str(export_out))
    assert export.returncode == 2
    assert export_out.read_text(encoding="utf-8") == "keep me"

    forced_export = run_cli("export", "claims-json", "--project", "zis_photocatalysis", "--out", str(export_out), "--force")
    assert forced_export.returncode == 0
    assert json.loads(export_out.read_text(encoding="utf-8"))


def test_project_path_overrides_are_rejected(tmp_path):
    result = run_cli("report", "inventory", "--project", "zis_photocatalysis", "--reports-dir", str(tmp_path))
    assert result.returncode == 2
    assert "--project cannot be combined with --reports-dir" in result.stderr


def test_unknown_section_outline_theme_fails_without_output(tmp_path):
    out = tmp_path / "unknown.md"
    result = run_cli(
        "report",
        "section-outline",
        "--project",
        "zis_photocatalysis",
        "--theme",
        "unknown-theme",
        "--out",
        str(out),
    )
    assert result.returncode == 2
    assert "Unknown theme" in result.stderr
    assert not out.exists()


def test_project_list_uses_relative_paths():
    result = run_cli("project", "list")
    assert result.returncode == 0
    assert "projects/zis_photocatalysis/registry.csv" in result.stdout
    assert str(ROOT) not in result.stdout


def test_theme_claims_export_uses_portable_note_paths(tmp_path):
    out = tmp_path / "theme_claims.json"
    result = run_cli(
        "export",
        "theme-claims",
        "--project",
        "zis_photocatalysis",
        "--theme",
        "photocorrosion",
        "--out",
        str(out),
    )
    assert result.returncode == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data
    assert "projects/zis_photocatalysis/notes" in data[0]["note_file"]
    assert str(ROOT) not in data[0]["note_file"]


def test_root_evidence_map_report_matches_current_examples():
    content = (ROOT / "reports" / "evidence_map.md").read_text(encoding="utf-8")
    assert "synth_photo_2023:c1" in content
