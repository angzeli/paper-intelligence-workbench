from __future__ import annotations

import subprocess
import sys

from conftest import EXAMPLE_BIBTEX, EXAMPLE_NOTES, EXAMPLE_REGISTRY, EXAMPLE_THEMES


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
