from __future__ import annotations

import json
import subprocess
import sys

from conftest import ROOT, STRESS_ZIS_PROJECT


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], check=False, text=True, capture_output=True)


def assert_ok(result):
    assert result.returncode == 0, result.stderr
    assert "Traceback" not in result.stderr


def test_cli_stress_project_and_doctor_smoke(tmp_path):
    help_result = run_cli("--help")
    assert_ok(help_result)
    assert "synthetic" in help_result.stdout

    listed = run_cli("project", "list")
    assert_ok(listed)
    assert "stress_zis_photocatalysis" in listed.stdout

    validated = run_cli("project", "validate", "stress_zis_photocatalysis")
    assert_ok(validated)
    assert "duplicate_doi" in validated.stdout
    assert "claim_missing_evidence_location" in validated.stdout

    health = run_cli("doctor", "--project", "stress_zis_photocatalysis", "--out", str(tmp_path / "health.md"), "--force")
    assert_ok(health)
    assert "Wrote" in health.stdout
    assert (tmp_path / "health.md").exists()


def test_cli_stress_validation_claims_reports_and_exports(tmp_path):
    registry = run_cli("validate-registry", str(STRESS_ZIS_PROJECT / "registry.csv"))
    assert_ok(registry)
    assert "duplicate_title" in registry.stdout

    bibtex = run_cli(
        "validate-bib",
        str(STRESS_ZIS_PROJECT / "bibtex" / "library.bib"),
        "--registry",
        str(STRESS_ZIS_PROJECT / "registry.csv"),
    )
    assert_ok(bibtex)
    assert "duplicate_bibtex_key" in bibtex.stdout

    claims_out = tmp_path / "claims.csv"
    claims = run_cli("claims", "--project", "stress_zis_photocatalysis", "--output", str(claims_out))
    assert_ok(claims)
    assert "Wrote 111 claims" in claims.stdout
    assert claims_out.exists()

    for report_type in ("evidence-map", "citation-audit", "theme-dashboard"):
        out = tmp_path / f"{report_type}.md"
        result = run_cli("report", report_type, "--project", "stress_zis_photocatalysis", "--out", str(out), "--force")
        assert_ok(result)
        assert out.exists()

    outline = tmp_path / "photocorrosion_outline.md"
    outline_result = run_cli(
        "report",
        "section-outline",
        "--project",
        "stress_zis_photocatalysis",
        "--theme",
        "photocorrosion",
        "--out",
        str(outline),
        "--force",
    )
    assert_ok(outline_result)
    assert "Literature Review Section Outline" in outline.read_text(encoding="utf-8")

    claims_json = tmp_path / "claims.json"
    exported = run_cli("export", "claims-json", "--project", "stress_zis_photocatalysis", "--out", str(claims_json), "--force")
    assert_ok(exported)
    assert len(json.loads(claims_json.read_text(encoding="utf-8"))) == 111


def test_cli_stress_search_modes():
    registry = run_cli("search", "photocorrosion", "--project", "stress_zis_photocatalysis")
    assert_ok(registry)
    assert "stress_zis_photocatalysis_synthetic_002" in registry.stdout

    notes = run_cli("search", "Local Review Conditions", "--project", "stress_zis_photocatalysis", "--notes", "--exact")
    assert_ok(notes)
    assert "stress_zis_photocatalysis_synthetic_001.md" in notes.stdout

    claims = run_cli("search", "Synthetic claim 37", "--project", "stress_zis_photocatalysis", "--claims", "--exact")
    assert_ok(claims)
    assert "stress_zis_photocatalysis_synthetic" in claims.stdout


def test_cli_synthetic_generate_refuses_existing_project(tmp_path):
    created = run_cli(
        "synthetic",
        "generate",
        "--project",
        "stress_cli_fixture",
        "--root",
        str(tmp_path),
        "--papers",
        "10",
        "--claims",
        "20",
        "--themes",
        "3",
        "--domain",
        "finance",
    )
    assert_ok(created)
    assert "Generated synthetic project stress_cli_fixture" in created.stdout

    duplicate = run_cli(
        "synthetic",
        "generate",
        "--project",
        "stress_cli_fixture",
        "--root",
        str(tmp_path),
        "--papers",
        "10",
        "--claims",
        "20",
    )
    assert duplicate.returncode == 2
    assert "already exists" in duplicate.stderr
    assert "Traceback" not in duplicate.stderr

    forced = run_cli(
        "synthetic",
        "generate",
        "--project",
        "stress_cli_fixture",
        "--root",
        str(tmp_path),
        "--papers",
        "11",
        "--claims",
        "22",
        "--force",
    )
    assert_ok(forced)
    assert "papers: 11" in forced.stdout
