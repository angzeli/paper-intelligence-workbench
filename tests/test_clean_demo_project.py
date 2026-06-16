from __future__ import annotations

import subprocess
import sys

from conftest import ROOT


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "paper_workbench.cli", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_clean_demo_project_stable_first_run_path(tmp_path) -> None:
    registry = ROOT / "projects" / "clean_demo" / "registry.csv"
    bibtex = ROOT / "projects" / "clean_demo" / "bibtex" / "library.bib"
    report = tmp_path / "integrity.md"

    registry_result = run_cli("validate-registry", str(registry), "--strict")
    assert registry_result.returncode == 0, registry_result.stderr
    assert "No findings." in registry_result.stdout

    bibtex_result = run_cli("validate-bib", str(bibtex), "--registry", str(registry), "--strict")
    assert bibtex_result.returncode == 0, bibtex_result.stderr
    assert "No findings." in bibtex_result.stdout

    rules_result = run_cli("rules", "run", "--project", "clean_demo", "--strict")
    assert rules_result.returncode == 0, rules_result.stderr
    assert "No rule findings." in rules_result.stdout

    dashboard_result = run_cli("dashboard", "--project", "clean_demo", "--no-audit-log")
    assert dashboard_result.returncode == 0, dashboard_result.stderr
    assert "BibTeX findings: 0 error(s), 0 warning(s)" in dashboard_result.stdout
    assert "Citation audit findings: 0 error(s), 0 warning(s)" in dashboard_result.stdout
    assert "Workspace health findings: 0 error(s), 0 warning(s)" in dashboard_result.stdout
    assert "Rule findings: 0 error(s), 0 warning(s)" in dashboard_result.stdout

    integrity_result = run_cli("integrity", "check", "--project", "clean_demo", "--out", str(report), "--force")
    assert integrity_result.returncode == 0, integrity_result.stderr
    assert "Integrity errors: 0" in integrity_result.stdout
    assert "Integrity warnings: 0" in integrity_result.stdout
