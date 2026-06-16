from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from conftest import ROOT
from paper_workbench.rebuild import (
    build_rebuild_plan,
    default_rebuild_metadata_path,
    hash_file,
    hash_path_set,
    run_rebuild_metadata,
)
from paper_workbench.synthetic import generate_synthetic_project


def _make_project(tmp_path: Path):
    summary = generate_synthetic_project(
        name="scale_demo",
        root=tmp_path,
        papers=8,
        claims=12,
        themes=3,
        domain="zis",
    )
    project = tmp_path / "projects" / summary.project
    return summary, project


def _plan(project: Path, project_id: str = "scale_demo"):
    return build_rebuild_plan(
        project_id=project_id,
        root=project,
        registry_path=project / "registry.csv",
        bibtex_path=project / "bibtex" / "library.bib",
        notes_dir=project / "notes",
        themes_path=project / "themes.json",
        reports_dir=project / "reports",
    )


def _run_cli(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(
        [sys.executable, "-m", "paper_workbench.cli", *args],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_content_hashing_changes_when_file_changes(tmp_path: Path) -> None:
    file_path = tmp_path / "note.md"
    file_path.write_text("first\n", encoding="utf-8")
    first = hash_file(file_path)
    set_first = hash_path_set([tmp_path], root=tmp_path, suffixes={".md"})

    file_path.write_text("second\n", encoding="utf-8")

    assert hash_file(file_path) != first
    assert hash_path_set([tmp_path], root=tmp_path, suffixes={".md"}) != set_first


def test_rebuild_plan_detects_stale_inputs_and_metadata_refresh(tmp_path: Path) -> None:
    summary, project = _make_project(tmp_path)
    initial = _plan(project, summary.project)

    assert initial.stale_items
    assert {item.target for item in initial.stale_items} >= {"claims", "evidence_map", "search_index"}

    result = run_rebuild_metadata(initial)
    metadata_path = default_rebuild_metadata_path(project)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert metadata["schema"] == "paperwb-rebuild-metadata-v1"
    assert result.refreshed_targets
    assert "claims" in metadata["targets"]

    after = _plan(project, summary.project)
    stale = {item.target for item in after.stale_items}
    assert "claims" not in stale
    assert "search_index" in stale

    note = next((project / "notes").glob("*.md"))
    note.write_text(note.read_text(encoding="utf-8") + "\nLocal test edit.\n", encoding="utf-8")
    changed = _plan(project, summary.project)
    assert "claims" in {item.target for item in changed.stale_items}


def test_rebuild_force_refreshes_every_target(tmp_path: Path) -> None:
    summary, project = _make_project(tmp_path)
    plan = _plan(project, summary.project)

    result = run_rebuild_metadata(plan, force=True)

    assert set(result.refreshed_targets) == {"claims", "evidence_map", "search_index", "report_outputs", "manuscript_qa", "dashboard"}


def test_rebuild_cli_smoke_and_metadata_only_write(tmp_path: Path) -> None:
    summary, project = _make_project(tmp_path)

    run_result = _run_cli(tmp_path, "rebuild", "run", "--project", summary.project)
    assert run_result.returncode == 0, run_result.stderr
    assert "updated rebuild metadata only" in run_result.stdout.lower()
    assert (project / ".paperwb" / "rebuild_metadata.json").exists()
    assert not (project / ".paperwb" / "index.sqlite").exists()

    status_result = _run_cli(tmp_path, "rebuild", "status", "--project", summary.project)
    assert status_result.returncode == 0, status_result.stderr
    assert "# Rebuild Status v" in status_result.stdout
    assert "search_index" in status_result.stdout

    plan_path = project / "reports" / "rebuild_plan.md"
    plan_result = _run_cli(tmp_path, "rebuild", "plan", "--project", summary.project, "--out", str(plan_path))
    assert plan_result.returncode == 0, plan_result.stderr
    assert plan_path.exists()
    assert str(ROOT) not in plan_path.read_text(encoding="utf-8")


def test_cache_hygiene_ignore_patterns_cover_rebuild_and_indexes() -> None:
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    for pattern in ("**/.paperwb/", "rebuild_metadata.json", "*.sqlite", "*.db", "**/backups/", "audit.log", "stress_outputs/"):
        assert pattern in ignore


def test_performance_sanity_script_smoke(tmp_path: Path) -> None:
    out = tmp_path / "performance.md"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "performance_sanity.py"),
            "--papers",
            "6",
            "--claims",
            "9",
            "--themes",
            "2",
            "--out",
            str(out),
            "--force",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    content = out.read_text(encoding="utf-8")
    assert "Search-index records" in content
    assert "rebuild SQLite search index" in content


def test_stress_project_generation_script_smoke(tmp_path: Path) -> None:
    out = tmp_path / "stress.md"
    root = tmp_path / "stress_root"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "stress_project_generation.py"),
            "--root",
            str(root),
            "--project",
            "tiny_stress",
            "--papers",
            "6",
            "--claims",
            "9",
            "--themes",
            "2",
            "--out",
            str(out),
            "--force",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (root / "projects" / "tiny_stress" / "registry.csv").exists()
    assert "Synthetic data only" in out.read_text(encoding="utf-8")
