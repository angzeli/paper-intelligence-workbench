"""Demonstrate creating a synthetic project from a built-in template.

The script uses a temporary workspace and does not write into checked-in
projects/. It requires no network access and includes no real paper metadata.
"""

from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def run_step(workspace: Path, *args: str) -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    command = [sys.executable, "-m", "paper_workbench.cli", *args]
    result = subprocess.run(command, cwd=workspace, env=env, text=True, capture_output=True, check=False)
    print("$", " ".join(["paperwb", *args]))
    print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="paperwb_template_demo_") as tmp_name:
        workspace = Path(tmp_name)
        print(f"Temporary workspace: {workspace}")
        run_step(workspace, "template", "list")
        run_step(workspace, "template", "inspect", "photocatalysis")
        run_step(workspace, "template", "create", "photocatalysis", "--project", "demo_photocatalysis")
        project = workspace / "projects" / "demo_photocatalysis"
        print("Generated files:")
        for path in sorted(project.rglob("*")):
            if path.is_file():
                print("-", path.relative_to(workspace))
        run_step(workspace, "doctor", "--project", "demo_photocatalysis")
        run_step(workspace, "dashboard", "--project", "demo_photocatalysis", "--no-audit-log")
        run_step(
            workspace,
            "report",
            "evidence-map",
            "--project",
            "demo_photocatalysis",
            "--out",
            "projects/demo_photocatalysis/reports/evidence_map.md",
            "--force",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
