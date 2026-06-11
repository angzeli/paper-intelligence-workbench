from __future__ import annotations

from datetime import datetime, timezone
import subprocess
import sys

import pytest

from conftest import ROOT
from paper_workbench.registry import load_registry, save_registry
from paper_workbench.schema import Author, Paper
from paper_workbench.sync import (
    SyncSource,
    SyncTarget,
    apply_registry_sync_plan,
    build_note_sync_plan,
    build_registry_sync_plan,
    load_sync_plan_json,
    save_sync_plan_json,
    sync_apply_report,
    sync_plan_report,
)


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], cwd=ROOT, check=False, text=True, capture_output=True)


def _paper(
    paper_id: str,
    *,
    title: str = "Synthetic Sync Paper",
    doi: str = "",
    journal: str = "",
    bibtex_key: str = "",
    tags: list[str] | None = None,
) -> Paper:
    return Paper(
        paper_id=paper_id,
        title=title,
        authors=[Author(given="Synthetic", family="Author", raw_name="Synthetic Author")],
        year="2026",
        journal=journal,
        doi=doi,
        bibtex_key=bibtex_key,
        tags=tags or [],
        reading_status="unread",
    )


def test_registry_sync_plan_detects_create_fill_skip_and_conflict():
    existing = [
        _paper("known", title="Known Synthetic Study", doi="10.1300/sync.known", journal="", bibtex_key="known2026"),
    ]
    source = SyncSource("zotero-csv", "synthetic_zotero.csv")
    target = SyncTarget("registry", "registry.csv", project="demo")
    source_papers = [
        _paper("known_import", title="Known Synthetic Study", doi="https://doi.org/10.1300/sync.known", journal="Synthetic Journal", bibtex_key="known2026"),
        _paper("new_import", title="New Synthetic Sync Study", doi="10.1300/sync.new", journal="New Journal", bibtex_key="new2026"),
        _paper("conflict_import", title="Conflicting Synthetic Title", doi="10.1300/sync.known", journal="Synthetic Journal", bibtex_key="known2026"),
        _paper("known_exact", title="Known Synthetic Study", doi="10.1300/sync.known", journal="", bibtex_key="known2026"),
    ]

    plan = build_registry_sync_plan(
        existing_papers=existing,
        source_papers=source_papers,
        source=source,
        target=target,
        project="demo",
        now=datetime(2026, 6, 11, tzinfo=timezone.utc),
    )

    action_types = [action.action_type for action in plan.actions]
    conflict_types = [conflict.conflict_type for conflict in plan.conflicts]
    assert "fill_blank_field" in action_types
    assert "create_paper" in action_types
    assert "skip_unchanged" in action_types
    assert "same_doi_different_title" in conflict_types
    assert "Sync Plan" in sync_plan_report(plan)


def test_sync_apply_dry_run_and_force_apply_safe_actions():
    existing = [_paper("known", title="Known Synthetic Study", doi="10.1300/sync.known", journal="")]
    source = SyncSource("zotero-csv", "source.csv")
    target = SyncTarget("registry", "registry.csv", project="demo")
    plan = build_registry_sync_plan(
        existing_papers=existing,
        source_papers=[
            _paper("known_incoming", title="Known Synthetic Study", doi="10.1300/sync.known", journal="Filled Journal"),
            _paper("created", title="Created Synthetic Study", doi="10.1300/sync.created", journal="Created Journal"),
        ],
        source=source,
        target=target,
        project="demo",
        now=datetime(2026, 6, 11, tzinfo=timezone.utc),
    )

    dry_papers, dry_result = apply_registry_sync_plan(plan, existing, dry_run=True, force=False)
    assert dry_papers[0].journal == ""
    assert len(dry_papers) == 1
    assert len(dry_result.applied_actions) == 2

    applied_papers, result = apply_registry_sync_plan(plan, existing, dry_run=False, force=True)
    assert {paper.paper_id for paper in applied_papers} == {"known", "created"}
    assert next(paper for paper in applied_papers if paper.paper_id == "known").journal == "Filled Journal"
    assert "Sync Apply Report" in sync_apply_report(plan, result)


def test_sync_apply_refuses_high_risk_conflicts_without_force():
    existing = [_paper("known", title="Known Synthetic Study", doi="10.1300/sync.known")]
    source = SyncSource("bibtex", "source.bib")
    target = SyncTarget("registry", "registry.csv")
    plan = build_registry_sync_plan(
        existing_papers=existing,
        source_papers=[_paper("incoming", title="Different Title", doi="10.1300/sync.known")],
        source=source,
        target=target,
        now=datetime(2026, 6, 11, tzinfo=timezone.utc),
    )

    _dry, dry_result = apply_registry_sync_plan(plan, existing, dry_run=True, force=False)
    assert "high-risk conflict" in dry_result.warnings[0]
    with pytest.raises(PermissionError):
        apply_registry_sync_plan(plan, existing, dry_run=False, force=False)


def test_sync_plan_json_roundtrip(tmp_path):
    plan = build_registry_sync_plan(
        existing_papers=[],
        source_papers=[_paper("created", title="Created Synthetic Study", doi="10.1300/sync.created")],
        source=SyncSource("zotero-csv", "source.csv"),
        target=SyncTarget("registry", "registry.csv"),
        now=datetime(2026, 6, 11, tzinfo=timezone.utc),
    )
    path = save_sync_plan_json(plan, tmp_path / "plan.json")

    loaded = load_sync_plan_json(path)
    assert loaded.plan_id == plan.plan_id
    assert loaded.actions[0].paper_id == "created"


def _note(paper_id: str, *, claim: str = "Synthetic claim.", followup: str = "Check page.") -> str:
    return f"""# Paper Note: {paper_id}

## Metadata
- Paper ID: {paper_id}
- BibTeX key: {paper_id}2026
- Tags: sync
- Reading status: read

## Claims and evidence

### Claim 1
- Claim: {claim}
- Evidence type: experimental_result
- Section / page: Section 2
- Quote or paraphrase: Synthetic paraphrase.
- Confidence: high
- Tags: sync
- User comment:
- Strength: strong
- Supports theme: sync

## Follow-up actions
- {followup}

## Personal reading notes
Synthetic personal note.
"""


def test_note_sync_detects_exported_note_conflicts(tmp_path):
    local = tmp_path / "notes"
    exported = tmp_path / "vault" / "papers"
    local.mkdir(parents=True)
    exported.mkdir(parents=True)
    (local / "paper_a.md").write_text(_note("paper_a", claim="Local synthetic claim."), encoding="utf-8")
    (exported / "paper_a.md").write_text(_note("paper_a", claim="Exported synthetic claim.", followup="Different follow-up."), encoding="utf-8")

    plan = build_note_sync_plan(
        local_notes_dir=local,
        exported_notes_dir=exported,
        source=SyncSource("obsidian-vault", str(exported)),
        target=SyncTarget("notes", str(local)),
        now=datetime(2026, 6, 11, tzinfo=timezone.utc),
    )

    conflict_types = {conflict.conflict_type for conflict in plan.conflicts}
    fields = {conflict.field for conflict in plan.conflicts}
    assert conflict_types == {"local_note_differs_from_exported_note"}
    assert {"claim_texts", "follow_up_actions"} <= fields


def test_sync_cli_plan_apply_and_conflicts(tmp_path):
    registry = tmp_path / "registry.csv"
    source = tmp_path / "zotero.csv"
    save_registry([_paper("known", title="Known Synthetic Study", doi="10.1300/sync.known", journal="")], registry)
    source.write_text(
        "Title,Author,Publication Year,Publication Title,DOI,Url,Item Type,Tags\n"
        "Known Synthetic Study,Synthetic Author,2026,Filled Journal,10.1300/sync.known,,Journal Article,sync\n"
        "New Synthetic Sync Study,Synthetic Author,2026,New Journal,10.1300/sync.new,,Journal Article,sync\n",
        encoding="utf-8",
    )
    plan_md = tmp_path / "sync_plan.md"
    plan_json = tmp_path / "sync_plan.json"

    planned = run_cli("sync", "plan", "--source", str(source), "--source-type", "zotero-csv", "--registry", str(registry), "--reports-dir", str(tmp_path), "--out", str(plan_md), "--json-out", str(plan_json))
    assert planned.returncode == 0, planned.stderr
    assert plan_json.exists()
    assert "Actions:" in planned.stdout

    dry_report = tmp_path / "dry_run.md"
    dry = run_cli("sync", "apply", str(plan_json), "--registry", str(registry), "--dry-run", "--out", str(dry_report))
    assert dry.returncode == 0, dry.stderr
    assert load_registry(registry)[0].journal == ""
    assert "Dry run: true" in dry_report.read_text(encoding="utf-8")

    applied = run_cli("sync", "apply", str(plan_json), "--registry", str(registry), "--force", "--no-backup", "--out", str(tmp_path / "apply.md"))
    assert applied.returncode == 0, applied.stderr
    papers = load_registry(registry)
    assert {paper.paper_id for paper in papers} == {"known", "author_2026_new_synthetic_sync"}
    assert next(paper for paper in papers if paper.paper_id == "known").journal == "Filled Journal"

    conflicts = run_cli("sync", "conflicts", str(plan_json))
    assert conflicts.returncode == 0, conflicts.stderr
    assert "Sync Conflicts" in conflicts.stdout


def test_sync_cli_plan_obsidian_reports_note_conflict(tmp_path):
    notes = tmp_path / "notes"
    vault_notes = tmp_path / "vault" / "papers"
    notes.mkdir(parents=True)
    vault_notes.mkdir(parents=True)
    (notes / "paper_a.md").write_text(_note("paper_a", claim="Local claim."), encoding="utf-8")
    (vault_notes / "paper_a.md").write_text(_note("paper_a", claim="Vault claim."), encoding="utf-8")
    out = tmp_path / "obsidian_roundtrip.md"
    json_out = tmp_path / "obsidian_roundtrip.json"

    result = run_cli(
        "sync",
        "plan-obsidian",
        "--vault",
        str(tmp_path / "vault"),
        "--notes-dir",
        str(notes),
        "--out",
        str(out),
        "--json-out",
        str(json_out),
    )

    assert result.returncode == 0, result.stderr
    assert "Conflicts:" in result.stdout
    assert "local_note_differs_from_exported_note" in out.read_text(encoding="utf-8")
    assert json_out.exists()
