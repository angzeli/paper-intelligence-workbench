from __future__ import annotations

import subprocess
import sys

from conftest import ROOT
from paper_workbench import __version__


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "paper_workbench.cli", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_v2_release_candidate_version_metadata() -> None:
    assert __version__ == "2.4"
    assert 'version = "2.4"' in (ROOT / "pyproject.toml").read_text(encoding="utf-8")


def test_v2_surface_docs_exist_and_classify_core_commands() -> None:
    docs = {
        "docs/STABLE_SURFACE_V2.md": ["`init`", "`project`", "`validate-registry`", "Registry CSV"],
        "docs/EXPERIMENTAL_FEATURES_V2.md": ["SQLite indexed search", "Sync apply", "Draft/manuscript QA", "Workflow runner", "Review packets"],
        "docs/DEPRECATION_POLICY.md": ["no deprecated CLI command groups"],
        "docs/COMMAND_CONTRACTS_V2.md": ["`backup`", "`migrate`", "`dashboard`", "Exit Codes"],
        "docs/SCHEMA_FREEZE_V2.md": ["Registry CSV", "Structured Note Markdown", "Project Profile"],
        "docs/MIGRATION_GUIDE_V2.md": ["dry-run", "copies", "does not delete"],
        "docs/BACKWARD_COMPATIBILITY_V2.md": ["Legacy `data/`", "Project profiles"],
        "docs/DATA_SAFETY_V2.md": ["No cloud APIs", "No LLM APIs", "No publisher scraping"],
        "docs/KNOWN_LIMITATIONS_V2.md": ["heuristic", "SQLite index files are rebuildable caches"],
    }
    for relative, fragments in docs.items():
        content = (ROOT / relative).read_text(encoding="utf-8")
        assert content.startswith("#"), relative
        for fragment in fragments:
            assert fragment in content, (relative, fragment)


def test_v2_release_reports_are_current_and_sanitized() -> None:
    reports = [
        "reports/release_notes_v2_0_rc.md",
        "reports/release_readiness_v2_0_rc.md",
        "reports/migration_readiness_v2_0_rc.md",
        "reports/report_inventory_v2_0_rc.md",
        "reports/report_cleanup_recommendations_v2_0_rc.md",
        "reports/index_v2_0_rc.md",
        "reports/test_suite_summary_v2_0_rc.md",
        "reports/notebook_validation_v2_0_rc.md",
        "reports/example_workflow_validation_v2_0_rc.md",
        "reports/data_safety_v2_0_rc.md",
        "reports/external_user_simulation_v2_0_rc.md",
        "reports/final_release_verdict_v2_0_rc.md",
        "reports/post_v2_0_roadmap.md",
    ]
    for relative in reports:
        content = (ROOT / relative).read_text(encoding="utf-8")
        assert content.startswith("#"), relative
        assert str(ROOT) not in content
        assert "/private/tmp/" not in content

    index = (ROOT / "reports" / "index.md").read_text(encoding="utf-8")
    assert "## Current v2.4 Release Reports" in index
    current_section = index.split("## Current v2.4 Release Reports", 1)[1]
    current_section = current_section.split("## Next Patch Plan", 1)[0]
    current_section = current_section.split("## Historical Versioned Reports", 1)[0]
    assert "[release_readiness_v2_4.md]" in current_section
    assert "[reviewer_comments_v2_4.md]" in current_section
    assert "[response_to_review_v2_4.md]" in current_section
    historical_section = index.split("## Historical Versioned Reports", 1)[1]
    assert "[release_readiness_v2_2.md]" in historical_section
    assert "[release_readiness_v2_1.md]" in historical_section
    assert "[release_readiness_v2_0_rc.md]" not in current_section
    assert "[final_release_verdict_v2_0_rc.md]" not in current_section


def test_v2_stable_command_help_contracts() -> None:
    commands = [
        ("init", "--help"),
        ("project", "--help"),
        ("template", "--help"),
        ("dogfood", "--help"),
        ("validate-registry", "--help"),
        ("validate-bib", "--help"),
        ("note-template", "--help"),
        ("claims", "--help"),
        ("report", "--help"),
        ("doctor", "--help"),
        ("dashboard", "--help"),
        ("workflow", "--help"),
    ]
    for command in commands:
        result = run_cli(*command)
        assert result.returncode == 0, (command, result.stderr)
        assert "Traceback" not in result.stderr
