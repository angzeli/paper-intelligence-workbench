from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from conftest import ROOT
from paper_workbench.dogfood import create_dogfood_project
from paper_workbench.workflow import (
    builtin_recipes,
    list_workflow_recipes,
    load_workflow_recipe,
    run_workflow,
    validate_workflow_recipe_file,
    workflow_run_report,
    write_workflow_run_report,
)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "paper_workbench.cli", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def test_builtin_workflow_recipes_are_available() -> None:
    recipes = builtin_recipes()

    assert {"daily_check", "weekly_review", "pre_writing_check", "release_candidate_check"} <= set(recipes)
    assert recipes["daily_check"].steps
    assert recipes["pre_backup_check"].dry_run_default is True


def test_invalid_recipe_rejects_unknown_step_and_shell_fields(tmp_path: Path) -> None:
    recipe_path = tmp_path / "bad_workflow.json"
    recipe_path.write_text(
        json.dumps(
            {
                "recipe_id": "bad",
                "name": "Bad",
                "steps": [
                    {
                        "step_id": "danger",
                        "step_type": "shell",
                        "command": "touch should_not_exist",
                        "params": {"shell": "touch should_not_exist"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    recipe, findings = validate_workflow_recipe_file(recipe_path)

    assert recipe.recipe_id == "bad"
    assert {finding.code for finding in findings} >= {"unknown_step_type", "forbidden_execution_field"}
    assert not (tmp_path / "should_not_exist").exists()


def test_load_workflow_recipe_raises_for_invalid_recipe(tmp_path: Path) -> None:
    recipe_path = tmp_path / "bad_workflow.json"
    recipe_path.write_text(
        '{"recipe_id": "bad", "steps": [{"step_id": "bad", "step_type": "unknown"}]}\n',
        encoding="utf-8",
    )

    try:
        load_workflow_recipe(recipe_path)
    except ValueError as exc:
        assert "unknown_step_type" in str(exc) or "Unknown step_type" in str(exc)
    else:
        raise AssertionError("invalid workflow recipe should raise")


def test_workflow_dry_run_does_not_write_step_outputs(tmp_path: Path) -> None:
    create_dogfood_project("generic", "demo_review", root=tmp_path)
    recipe = builtin_recipes()["daily_check"]

    run = run_workflow(recipe, project="demo_review", root=tmp_path, dry_run=True)

    assert run.dry_run is True
    assert len(run.results) == len(recipe.steps)
    assert any(result.status == "planned" for result in run.results)
    project = tmp_path / "projects" / "demo_review"
    assert not (project / "reports" / "workflow_daily_check_dashboard.md").exists()


def test_workflow_run_report_generation(tmp_path: Path) -> None:
    create_dogfood_project("generic", "demo_review", root=tmp_path)
    run = run_workflow(builtin_recipes()["daily_check"], project="demo_review", root=tmp_path, dry_run=True)
    report_path = write_workflow_run_report(run, tmp_path / "workflow_run.md")
    content = workflow_run_report(run)

    assert report_path.exists()
    assert "Workflow Run" in content
    assert "does not execute shell commands" in content
    assert "daily_check" in content


def test_project_specific_recipe_loading(tmp_path: Path) -> None:
    create_dogfood_project("generic", "demo_review", root=tmp_path)
    workflows_dir = tmp_path / "projects" / "demo_review" / "workflows"
    workflows_dir.mkdir()
    (workflows_dir / "local_daily.json").write_text(
        json.dumps(
            {
                "recipe_id": "local_daily",
                "name": "Local Daily",
                "dry_run_default": True,
                "steps": [{"step_id": "validate", "step_type": "validate_registry"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    recipes = list_workflow_recipes("demo_review", root=tmp_path)

    assert "local_daily" in {recipe.recipe_id for recipe in recipes}


def test_workflow_cli_smoke(tmp_path: Path) -> None:
    create_dogfood_project("generic", "demo_review", root=tmp_path)
    report = tmp_path / "workflow_report.md"
    recipe = tmp_path / "recipe.json"
    recipe.write_text(
        json.dumps(
            {
                "recipe_id": "tiny",
                "name": "Tiny",
                "dry_run_default": True,
                "steps": [{"step_id": "validate", "step_type": "validate_registry"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    help_result = run_cli("workflow", "--help")
    list_result = run_cli("workflow", "list", "--project", "demo_review", "--root", str(tmp_path))
    show_result = run_cli("workflow", "show", "daily_check")
    validate_result = run_cli("workflow", "validate", str(recipe), "--strict")
    conflicting_result = run_cli(
        "workflow",
        "run",
        "daily_check",
        "--project",
        "demo_review",
        "--root",
        str(tmp_path),
        "--dry-run",
        "--run-writes",
    )
    run_result = run_cli(
        "workflow",
        "run",
        "daily_check",
        "--project",
        "demo_review",
        "--root",
        str(tmp_path),
        "--dry-run",
        "--out",
        str(report),
        "--force",
    )

    assert help_result.returncode == 0
    assert "{list,show,run,validate}" in help_result.stdout
    assert list_result.returncode == 0
    assert "daily_check" in list_result.stdout
    assert show_result.returncode == 0
    assert "Workflow Recipe" in show_result.stdout
    assert validate_result.returncode == 0, validate_result.stderr
    assert "No validation findings" in validate_result.stdout
    assert conflicting_result.returncode != 0
    assert "use either --dry-run or --run-writes" in conflicting_result.stderr
    assert run_result.returncode == 0, run_result.stderr
    assert report.exists()
    assert "Dry run: `true`" in report.read_text(encoding="utf-8")
