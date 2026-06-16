from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from conftest import ROOT
from paper_workbench import __version__


def run_cli(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "paper_workbench.cli", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def test_v3_release_candidate_version_metadata() -> None:
    assert __version__ == "3.0.0rc1"
    assert 'version = "3.0.0rc1"' in (ROOT / "pyproject.toml").read_text(encoding="utf-8")


def test_v3_surface_docs_exist_and_classify_release_surfaces() -> None:
    docs = {
        "docs/STABLE_SURFACE_V3.md": ["`dogfood`", "`validate-registry`", "Registry CSV", "Stable Safety Guarantees"],
        "docs/EXPERIMENTAL_FEATURES_V3.md": ["Workflow runner", "Evidence graph", "Incremental rebuilds"],
        "docs/DEPRECATED_FEATURES_V3.md": ["does not deprecate any public CLI command group"],
        "docs/COMMAND_CONTRACTS_V3.md": ["`backup`", "`workflow`", "`dashboard`", "Exit Codes"],
        "docs/SCHEMA_REFERENCE_V3.md": ["Registry CSV", "Structured Note Markdown", "Project Profile Layout"],
        "docs/GETTING_STARTED_V3.md": ["clean_demo", "dogfood create photocatalysis", "No cloud APIs"],
        "docs/FIRST_REAL_PROJECT_V3.md": ["10-15 papers", "plan-from-files", "does not copy PDFs"],
        "docs/DATA_SAFETY_V3.md": ["No cloud APIs", "No LLM APIs", "Files That Should Not Be Committed"],
        "docs/KNOWN_LIMITATIONS_V3.md": ["heuristic", "scientific truth"],
        "docs/ROADMAP_V3.md": ["Before v3.0.0", "Not In Scope"],
    }
    for relative, fragments in docs.items():
        content = (ROOT / relative).read_text(encoding="utf-8")
        assert content.startswith("#"), relative
        for fragment in fragments:
            assert fragment in content, (relative, fragment)


def test_v3_stable_command_help_contracts() -> None:
    commands = [
        ("init", "--help"),
        ("project", "--help"),
        ("template", "--help"),
        ("dogfood", "--help"),
        ("validate-registry", "--help"),
        ("validate-bib", "--help"),
        ("add-paper", "--help"),
        ("list", "--help"),
        ("note-template", "--help"),
        ("claims", "--help"),
        ("report", "--help"),
        ("checklist", "--help"),
        ("doctor", "--help"),
        ("dashboard", "--help"),
    ]
    for command in commands:
        result = run_cli(*command)
        assert result.returncode == 0, (command, result.stderr)
        assert "Traceback" not in result.stderr


def test_v3_stable_clean_demo_happy_paths(tmp_path: Path) -> None:
    claims_out = tmp_path / "claims.csv"
    evidence_out = tmp_path / "evidence_map.md"
    dashboard_out = tmp_path / "dashboard.md"

    commands = [
        ("validate-registry", "projects/clean_demo/registry.csv", "--strict"),
        ("validate-bib", "projects/clean_demo/bibtex/library.bib", "--registry", "projects/clean_demo/registry.csv", "--strict"),
        ("list", "--project", "clean_demo"),
        ("claims", "projects/clean_demo/notes", "--output", str(claims_out), "--force"),
        ("report", "evidence-map", "--project", "clean_demo", "--out", str(evidence_out), "--force"),
        ("dashboard", "--project", "clean_demo", "--out", str(dashboard_out), "--force", "--no-audit-log"),
        ("doctor", "--project", "clean_demo"),
    ]
    for command in commands:
        result = run_cli(*command)
        assert result.returncode == 0, (command, result.stderr, result.stdout)
        assert "Traceback" not in result.stderr

    assert claims_out.exists()
    assert evidence_out.exists()
    assert dashboard_out.exists()


def test_v3_common_failure_paths_are_user_facing() -> None:
    missing_registry = run_cli("validate-registry", "missing_registry.csv", "--strict")
    missing_project = run_cli("project", "validate", "missing_project")

    assert missing_registry.returncode != 0
    assert "Traceback" not in missing_registry.stderr
    assert "Traceback" not in missing_registry.stdout
    assert missing_project.returncode != 0
    assert "Traceback" not in missing_project.stderr
    assert "Traceback" not in missing_project.stdout


def test_v3_dogfood_project_creation_is_non_destructive(tmp_path: Path) -> None:
    create = run_cli("dogfood", "create", "photocatalysis", "--project", "v3_demo", "--root", str(tmp_path))
    duplicate = run_cli("dogfood", "create", "photocatalysis", "--project", "v3_demo", "--root", str(tmp_path))
    status = run_cli("dogfood", "status", "--project", "v3_demo", "--root", str(tmp_path))
    checklist = run_cli("dogfood", "checklist", "--project", "v3_demo", "--root", str(tmp_path))

    assert create.returncode == 0, create.stderr
    assert duplicate.returncode != 0
    assert "exists" in duplicate.stderr.lower() or "exists" in duplicate.stdout.lower()
    assert status.returncode == 0
    assert "No papers yet" in status.stdout
    assert checklist.returncode == 0
    assert "Do not copy PDFs into Git" in checklist.stdout
    assert (tmp_path / "projects" / "v3_demo" / "registry.csv").exists()
    assert not list((tmp_path / "projects" / "v3_demo").rglob("*.pdf"))


def test_v3_workflow_release_candidate_dry_run_has_no_errors(tmp_path: Path) -> None:
    report = tmp_path / "workflow_rc.md"
    result = run_cli(
        "workflow",
        "run",
        "release_candidate_check",
        "--project",
        "clean_demo",
        "--dry-run",
        "--out",
        str(report),
        "--force",
    )

    assert result.returncode == 0, result.stderr
    assert "Errors: 0" in result.stdout
    content = report.read_text(encoding="utf-8")
    assert report.exists()
    assert "failed" not in content.lower()
