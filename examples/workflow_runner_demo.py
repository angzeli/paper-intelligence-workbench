"""Demonstrate the v2.3 workflow runner on synthetic project data.

Run from the repository root:

    python examples/workflow_runner_demo.py

The script writes only under scratch/ and uses checked-in synthetic fixtures.
"""

from __future__ import annotations

from pathlib import Path

from paper_workbench.workflow import (
    builtin_recipes,
    run_workflow,
    workflow_recipe_summary,
    write_workflow_run_report,
)


def main() -> None:
    scratch = Path("scratch")
    scratch.mkdir(exist_ok=True)

    print("Available built-in workflows:")
    for recipe in builtin_recipes().values():
        print("-", workflow_recipe_summary(recipe))

    recipe = builtin_recipes()["daily_check"]
    run = run_workflow(recipe, project="zis_photocatalysis", dry_run=True)
    report = write_workflow_run_report(run, scratch / "workflow_runner_demo_daily_check.md", force=True)

    print(f"\nWrote dry-run workflow report: {report}")
    print(f"Steps: {len(run.results)}")
    print(f"Errors: {len(run.errors)}")
    print(f"Warnings: {len(run.warnings)}")


if __name__ == "__main__":
    main()
