"""Demonstrate v0.9 workspace integrity, backup, migration, and audit logs.

This script uses a temporary synthetic workspace. It does not use real paper
metadata, real PDFs, cloud services, or absolute hardcoded paths.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from paper_workbench.registry import save_registry
from paper_workbench.schema import Author, Paper


def run(root: Path, *args: str) -> None:
    result = subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], cwd=root, text=True, capture_output=True, check=False)
    print("$ paperwb", " ".join(args))
    print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    if result.returncode:
        raise SystemExit(result.returncode)


def seed_workspace(root: Path) -> None:
    registry = root / "data" / "registries" / "papers.csv"
    bibtex = root / "data" / "bibtex" / "library.bib"
    notes = root / "data" / "notes"
    themes = root / "data" / "examples" / "themes.json"
    reports = root / "reports"
    notes.mkdir(parents=True)
    bibtex.parent.mkdir(parents=True)
    themes.parent.mkdir(parents=True)
    reports.mkdir(parents=True)
    save_registry(
        [
            Paper(
                paper_id="synthetic_safety_2026",
                title="Synthetic Workspace Safety for Literature Reviews",
                authors=[Author(given="Sam", family="Synthetic", raw_name="Sam Synthetic")],
                year="2026",
                bibtex_key="Synthetic2026Safety",
                reading_status="read",
                notes_path="data/notes/synthetic_safety_2026.md",
            )
        ],
        registry,
    )
    bibtex.write_text("@article{Synthetic2026Safety,title={Synthetic Workspace Safety for Literature Reviews},author={Synthetic, Sam},year={2026},journal={Synthetic Methods}}\n", encoding="utf-8")
    (notes / "synthetic_safety_2026.md").write_text(
        "# Paper Note: Synthetic Workspace Safety for Literature Reviews\n\n"
        "## Metadata\n- Paper ID: synthetic_safety_2026\n- BibTeX key: Synthetic2026Safety\n- Reading status: read\n- Tags: safety\n\n"
        "## Claims and evidence\n\n### Claim 1\n- Claim: Synthetic backups make restore planning observable.\n- Evidence type: method_description\n- Section / page: Section 1\n- Quote or paraphrase: Synthetic local workflow.\n- Confidence: high\n- Strength: strong\n- Tags: safety\n- Supports theme: safety\n",
        encoding="utf-8",
    )
    themes.write_text('{"themes":[{"theme_id":"safety","name":"Safety","tags":["safety"],"min_claims":1,"min_papers":1}]}\n', encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="paperwb_safety_demo_") as directory:
        root = Path(directory)
        seed_workspace(root)
        run(root, "integrity", "check", "--out", "reports/workspace_integrity_v0_9.md", "--force")
        run(root, "backup", "create", "--notes", "Synthetic safety demo")
        backup_id = sorted((root / "backups").iterdir())[0].name
        run(root, "backup", "inspect", backup_id)
        run(root, "backup", "restore", backup_id, "--dry-run", "--out", "reports/restore_dry_run_v0_9.md", "--force-report")
        run(root, "migrate", "plan", "--from", "legacy", "--to-project", "migrated_demo", "--out", "reports/migration_plan_v0_9.md", "--force")
        run(root, "migrate", "run", "--from", "legacy", "--to-project", "migrated_demo", "--dry-run")
        run(root, "audit-log", "show", "--markdown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
