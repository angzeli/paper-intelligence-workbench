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
    assert __version__ == "3.3"
    assert 'requires-python = ">=3.10"' in content
    assert "dependencies = []" in content
    assert 'paperwb = "paper_workbench.cli:main"' in content
    assert "test = [\"pytest>=8\"]" in content
    assert "ruff>=0.6" in content
    assert "mypy>=1.8" in content


def test_release_docs_site_and_matrices_exist():
    expected = [
        "docs/index.md",
        "docs/getting-started.md",
        "docs/workflows.md",
        "docs/cli-reference.md",
        "docs/reports.md",
        "docs/project-profiles.md",
        "docs/PROJECT_TEMPLATES.md",
        "docs/PHOTOCATALYSIS_TEMPLATE.md",
        "docs/FINANCE_TEMPLATE.md",
        "docs/ML_METHODS_TEMPLATE.md",
        "docs/DOGFOODING_WORKFLOW.md",
        "docs/local-search.md",
        "docs/import-export.md",
        "docs/authoring-workbench.md",
        "docs/local-files.md",
        "docs/safety-and-boundaries.md",
        "docs/WORKFLOW_RUNNER.md",
        "docs/REPORT_RECIPES.md",
        "docs/BUILT_IN_WORKFLOWS.md",
        "docs/WORKFLOW_SAFETY.md",
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
        "docs/STABLE_SURFACE_V2.md",
        "docs/EXPERIMENTAL_FEATURES_V2.md",
        "docs/DEPRECATION_POLICY.md",
        "docs/COMMAND_CONTRACTS_V2.md",
        "docs/SCHEMA_FREEZE_V2.md",
        "docs/MIGRATION_GUIDE_V2.md",
        "docs/BACKWARD_COMPATIBILITY_V2.md",
        "docs/GETTING_STARTED_V2.md",
        "docs/WORKFLOWS_V2.md",
        "docs/CLI_REFERENCE_V2.md",
        "docs/REPORTS_V2.md",
        "docs/DATA_SAFETY_V2.md",
        "docs/KNOWN_LIMITATIONS_V2.md",
        "docs/ROADMAP_V2.md",
        "docs/TEST_MATRIX_V2.md",
        "docs/GETTING_STARTED_V3.md",
        "docs/STABLE_SURFACE_V3.md",
        "docs/EXPERIMENTAL_FEATURES_V3.md",
        "docs/COMMAND_CONTRACTS_V3.md",
        "docs/SCHEMA_REFERENCE_V3.md",
        "docs/CLI_REFERENCE_V3.md",
        "docs/DATA_SAFETY_V3.md",
        "docs/ROADMAP_V3.md",
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
    assert f"CLI Smoke Workflow v{__version__}" in content
    assert "Failures: 0" in content
    assert "validate registry" in content
    assert "dashboard next actions" in content


def test_data_safety_audit_script_generates_report(tmp_path):
    out = tmp_path / "data_safety.md"
    result = run_script("scripts/data_safety_audit.py", "--out", str(out), "--strict")

    assert result.returncode == 0, result.stderr
    content = out.read_text(encoding="utf-8")
    assert f"Data Safety Audit v{__version__}" in content
    assert "Errors: 0" in content


def test_data_safety_audit_default_writes_to_ignored_scratch(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, text=True, capture_output=True)
    (tmp_path / "README.md").write_text("# Synthetic fixture\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "data_safety_audit.py"), "--strict"],
        cwd=tmp_path,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    scratch_report = tmp_path / "scratch" / "data_safety_audit.md"
    assert scratch_report.exists()
    assert not (tmp_path / "reports" / "data_safety_audit_v0_10.md").exists()
    assert f"Data Safety Audit v{__version__}" in scratch_report.read_text(encoding="utf-8")


def test_data_safety_audit_module_flags_forbidden_artifacts_without_failing_on_warnings():
    result = audit_data_safety(ROOT)
    markdown = safety_audit_markdown(result)

    assert result.files_checked > 0
    assert not result.errors
    assert f"Data Safety Audit v{__version__}" in markdown


def test_data_safety_flags_real_metadata_in_public_demo_registry(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, text=True, capture_output=True)
    registry = tmp_path / "public" / "demos" / "v2_0_dogfood_real" / "projects" / "demo" / "registry.csv"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        "paper_id,title,authors,year,journal,doi,bibtex_key,reading_status,included_in_lit_review,tags,notes_path,project,source_type,user_comment\n"
        "real_demo,Real Photocatalysis Article,Real Author,2024,Real Journal,,realKey,unread,yes,photocatalysis,notes/real_demo.md,demo,journal_article,\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, text=True, capture_output=True)

    result = audit_data_safety(tmp_path)

    assert any(finding.code == "public_demo_real_metadata" for finding in result.errors)


def test_performance_sanity_default_writes_to_scratch(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "performance_sanity.py"),
            "--papers",
            "4",
            "--claims",
            "6",
            "--themes",
            "2",
        ],
        cwd=tmp_path,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "scratch" / "performance_sanity.md").exists()
    assert not (tmp_path / "reports" / "performance_sanity_v0_3.md").exists()


def test_ci_runs_v0_8_release_checks():
    content = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert 'python-version: ["3.10", "3.11", "3.12"]' in content
    assert 'python -m pip install -e ".[dev]"' in content
    assert "python scripts/clean_room_install_check.py --quick" in content
    assert "paperwb --help" in content
    assert "python scripts/run_quality_gate.py release" in content

    gate = (ROOT / "scripts" / "run_quality_gate.py").read_text(encoding="utf-8")
    assert "scripts/check_notebooks.py" in gate
    assert "scripts/smoke_cli_workflow.py" in gate
    assert "scripts/data_safety_audit.py" in gate
    assert '"build", "--sdist", "--wheel"' in gate


def test_v2_stable_surface_uses_current_line_for_experimental_graph():
    content = (ROOT / "docs" / "STABLE_SURFACE_V2.md").read_text(encoding="utf-8")

    assert "experimental in v2.1" not in content
    assert "`graph`, `claim-review`, `contradictions`, `workflow`, and `review-packet`" in content
