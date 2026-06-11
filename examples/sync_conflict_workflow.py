"""Synthetic v1.3 sync and conflict-resolution workflow.

Run from the repository root:

    python examples/sync_conflict_workflow.py

The script writes only to a temporary directory and uses synthetic metadata.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from paper_workbench.registry import load_registry, save_registry
from paper_workbench.schema import Author, Paper
from paper_workbench.sync import (
    SyncSource,
    SyncTarget,
    apply_registry_sync_plan,
    build_registry_sync_plan,
    save_sync_plan_json,
    sync_apply_report,
    sync_plan_report,
    write_registry_apply_result,
)


def synthetic_paper(paper_id: str, title: str, doi: str, journal: str = "") -> Paper:
    return Paper(
        paper_id=paper_id,
        title=title,
        authors=[Author(given="Synthetic", family="Author", raw_name="Synthetic Author")],
        year="2026",
        doi=doi,
        journal=journal,
        reading_status="unread",
    )


def main() -> None:
    with TemporaryDirectory(prefix="paperwb_sync_demo_") as tmp:
        root = Path(tmp)
        registry = root / "registry.csv"
        reports = root / "reports"
        reports.mkdir()

        existing = [synthetic_paper("known", "Known Synthetic Study", "10.1300/sync.known")]
        incoming = [
            synthetic_paper("known_import", "Known Synthetic Study", "10.1300/sync.known", journal="Filled Journal"),
            synthetic_paper("new_import", "New Synthetic Sync Study", "10.1300/sync.new", journal="New Journal"),
            synthetic_paper("conflict_import", "Conflicting Synthetic Title", "10.1300/sync.known"),
        ]
        save_registry(existing, registry)

        plan = build_registry_sync_plan(
            existing_papers=load_registry(registry),
            source_papers=incoming,
            source=SyncSource(source_type="synthetic", path="synthetic_source"),
            target=SyncTarget(target_type="registry", path=str(registry)),
            project="synthetic_demo",
            now=datetime(2026, 6, 11, tzinfo=timezone.utc),
        )
        plan_report = reports / "sync_plan.md"
        plan_json = reports / "sync_plan.json"
        plan_report.write_text(sync_plan_report(plan), encoding="utf-8")
        save_sync_plan_json(plan, plan_json)

        _dry_papers, dry_result = apply_registry_sync_plan(plan, load_registry(registry), dry_run=True)
        (reports / "sync_apply_dry_run.md").write_text(sync_apply_report(plan, dry_result), encoding="utf-8")

        safe_plan = build_registry_sync_plan(
            existing_papers=load_registry(registry),
            source_papers=incoming[:2],
            source=SyncSource(source_type="synthetic", path="synthetic_source"),
            target=SyncTarget(target_type="registry", path=str(registry)),
            project="synthetic_demo",
            now=datetime(2026, 6, 11, tzinfo=timezone.utc),
        )
        updated, apply_result = apply_registry_sync_plan(safe_plan, load_registry(registry), dry_run=False, force=True)
        write_registry_apply_result(updated, registry)
        (reports / "sync_apply_safe.md").write_text(sync_apply_report(safe_plan, apply_result), encoding="utf-8")

        print(f"Synthetic sync demo wrote reports to {reports}")
        print("Key takeaways:")
        print("- Plans are generated before writes.")
        print("- High-risk conflicts are manual review items.")
        print("- Safe apply creates missing rows and fills blank fields only.")


if __name__ == "__main__":
    main()

