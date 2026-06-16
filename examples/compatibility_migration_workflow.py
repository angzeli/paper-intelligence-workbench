"""Synthetic compatibility and migration workflow demo.

Run from the repository root:

    python examples/compatibility_migration_workflow.py
"""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile

from paper_workbench.compatibility import compatibility_report, inspect_workspace
from paper_workbench.migration import migration_plan_report, run_legacy_migration


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "workspaces" / "v0_1_legacy_data"


def main() -> None:
    inspection = inspect_workspace(FIXTURE)
    print(compatibility_report(inspection))

    with tempfile.TemporaryDirectory(prefix="paperwb-compat-") as tmp:
        workspace = Path(tmp) / "legacy_workspace"
        shutil.copytree(FIXTURE, workspace)
        plan, _backup = run_legacy_migration(root=workspace, to_project="demo_migrated", dry_run=True)
        print(migration_plan_report(plan))


if __name__ == "__main__":
    main()
