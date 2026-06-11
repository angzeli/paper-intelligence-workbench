from __future__ import annotations

import subprocess
import sys

from conftest import ROOT
from paper_workbench import __version__
from paper_workbench.safety import audit_data_safety, safety_audit_markdown


def run_script(*args: str):
    return subprocess.run([sys.executable, *args], cwd=ROOT, check=False, text=True, capture_output=True)


def test_package_metadata_matches_import_version_and_cli_entrypoint():
    content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert f'version = "{__version__}"' in content
    assert __version__ == "1.1.0"
    assert 'requires-python = ">=3.10"' in content
    assert "dependencies = []" in content
    assert 'paperwb = "paper_workbench.cli:main"' in content
    assert "test = [\"pytest>=8\"]" in content


def test_release_docs_site_and_matrices_exist():
    expected = [
        "docs/index.md",
        "docs/getting-started.md",
        "docs/workflows.md",
        "docs/cli-reference.md",
        "docs/reports.md",
        "docs/project-profiles.md",
        "docs/local-search.md",
        "docs/import-export.md",
        "docs/authoring-workbench.md",
        "docs/local-files.md",
        "docs/safety-and-boundaries.md",
        "docs/SITE_MAP.md",
        "docs/EXTERNAL_USER_QUICKSTART.md",
        "docs/TEST_MATRIX.md",
        "docs/CLI_BEHAVIOR_MATRIX.md",
        "docs/REPORT_MATRIX.md",
        "docs/DATA_SAFETY_MATRIX.md",
        "docs/INSTALLATION.md",
        "docs/API_SURFACE.md",
        "docs/CLI_SURFACE.md",
        "docs/COMMAND_CONTRACTS.md",
    ]

    for relative in expected:
        path = ROOT / relative
        assert path.exists(), relative
        assert path.read_text(encoding="utf-8").startswith("#")


def test_installation_docs_do_not_pin_stale_release_version():
    content = (ROOT / "docs" / "INSTALLATION.md").read_text(encoding="utf-8")

    assert "0.8.0" not in content
    assert "pyproject.toml" in content


def test_check_notebooks_script_reports_titles():
    result = run_script("scripts/check_notebooks.py")

    assert result.returncode == 0, result.stderr
    assert "Checked" in result.stdout
    assert "notebooks/01_registry_and_bibtex_workflow.ipynb" in result.stdout


def test_smoke_cli_workflow_quick_generates_report(tmp_path):
    out = tmp_path / "smoke.md"
    result = run_script("scripts/smoke_cli_workflow.py", "--quick", "--out", str(out))

    assert result.returncode == 0, result.stderr
    content = out.read_text(encoding="utf-8")
    assert "CLI Smoke Workflow v0.8" in content
    assert "Failures: 0" in content
    assert "validate registry" in content


def test_data_safety_audit_script_generates_report(tmp_path):
    out = tmp_path / "data_safety.md"
    result = run_script("scripts/data_safety_audit.py", "--out", str(out), "--strict")

    assert result.returncode == 0, result.stderr
    content = out.read_text(encoding="utf-8")
    assert "Data Safety Audit v0.10" in content
    assert "Errors: 0" in content


def test_data_safety_audit_module_flags_forbidden_artifacts_without_failing_on_warnings():
    result = audit_data_safety(ROOT)
    markdown = safety_audit_markdown(result)

    assert result.files_checked > 0
    assert not result.errors
    assert "Data Safety Audit v0.10" in markdown


def test_ci_runs_v0_8_release_checks():
    content = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert 'python-version: ["3.10", "3.11", "3.12"]' in content
    assert 'python -m pip install -e ".[dev]"' in content
    assert "python scripts/check_notebooks.py" in content
    assert "python scripts/smoke_cli_workflow.py --quick" in content
    assert "python scripts/clean_room_install_check.py --quick" in content
    assert "python scripts/data_safety_audit.py" in content
    assert "paperwb --help" in content
    assert "python -m build --sdist --wheel" in content
