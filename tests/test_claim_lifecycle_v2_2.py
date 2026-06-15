from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from conftest import ROOT
from paper_workbench.authoring import writing_packet_report
from paper_workbench.claim_lifecycle import (
    ClaimLifecycleRecord,
    add_claim_to_contradiction_group,
    build_claim_review_queue,
    claim_review_queue_report,
    contradictions_report,
    create_contradiction_group,
    lifecycle_status_for_claim,
    load_claim_lifecycle,
    mark_claim_status,
    save_claim_lifecycle,
)
from paper_workbench.dashboard import build_dashboard
from paper_workbench.drafts import audit_draft, parse_markdown_draft
from paper_workbench.graph import analyze_graph, build_evidence_graph, graph_to_json
from paper_workbench.registry import save_registry
from paper_workbench.schema import Author, BibTeXEntry, Claim, Paper, PaperNote, ProjectTheme


def run_cli(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(
        [sys.executable, "-m", "paper_workbench.cli", *args],
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
        env=env,
    )


def _paper() -> Paper:
    return Paper(
        paper_id="paper_a",
        title="Synthetic Claim Lifecycle Paper",
        authors=[Author(given="Ada", family="Example", raw_name="Ada Example")],
        year="2026",
        bibtex_key="paperA2026",
        reading_status="skimmed",
        tags=["photocorrosion"],
    )


def _claim(*, section: str = "", strength: str = "strong", confidence: str = "high") -> Claim:
    return Claim(
        claim_id="paper_a:c1",
        paper_id="paper_a",
        claim_text="Synthetic photocorrosion stability improves under tracked control conditions.",
        evidence_type="experimental_result",
        section=section,
        confidence=confidence,
        strength=strength,
        supports_theme="photocorrosion",
        tags=["photocorrosion"],
    )


def _theme() -> ProjectTheme:
    return ProjectTheme(theme_id="photocorrosion", name="Photocorrosion", tags=["photocorrosion"], min_papers=1, min_claims=1)


def test_claim_status_defaults_and_queue_prioritization() -> None:
    claim = _claim(section="")

    assert lifecycle_status_for_claim(claim, {}) == "needs_evidence_location"

    queue = build_claim_review_queue([claim], [_paper()], [_theme()], {}, limit=5)

    assert queue[0].claim_id == "paper_a:c1"
    assert queue[0].priority == "high"
    assert "evidence location" in "; ".join(queue[0].reasons)
    assert "Claim Review Queue v2.2" in claim_review_queue_report(queue, project="demo")


def test_mark_verified_and_deprecated_sidecar_round_trip(tmp_path: Path) -> None:
    claims = [_claim(section="Results")]
    records: dict[str, ClaimLifecycleRecord] = {}

    verified = mark_claim_status(records, claims, "paper_a:c1", status="verified", verification_date="2026-06-15")
    assert verified.claim_status == "verified"
    assert verified.review_status == "reviewed"
    assert verified.verification_date == "2026-06-15"

    deprecated = mark_claim_status(records, claims, "paper_a:c1", status="deprecated", reason="Synthetic superseded claim.")
    assert deprecated.claim_status == "deprecated"
    assert deprecated.deprecated_reason == "Synthetic superseded claim."

    path = save_claim_lifecycle(tmp_path / "claim_lifecycle.json", records)
    loaded = load_claim_lifecycle(path)
    assert loaded["paper_a:c1"].claim_status == "deprecated"


def test_contradiction_group_report_and_lifecycle_status() -> None:
    claims = [_claim(section="Results")]
    groups = {}
    group = create_contradiction_group(groups, theme="photocorrosion", description="Synthetic tension.")
    add_claim_to_contradiction_group(groups, claims, group.group_id, "paper_a:c1")

    content = contradictions_report(groups, claims, [_theme()], project="demo")

    assert group.group_id in content
    assert "user-managed review aids" in content
    assert "paper_a:c1" in content


def test_writing_packet_includes_lifecycle_warnings_when_records_supplied() -> None:
    claim = _claim(section="")
    packet = writing_packet_report(
        "photocorrosion",
        [_paper()],
        [PaperNote(paper_id="paper_a", claims=[claim])],
        [claim],
        [BibTeXEntry(entry_type="article", key="paperA2026")],
        [_theme()],
        project="demo",
        claim_lifecycle={},
    )

    assert "Claim Lifecycle Warnings" in packet
    assert "needs_evidence_location" in packet


def test_draft_audit_flags_deprecated_matched_claim(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "# Synthetic Draft\n\nSynthetic photocorrosion stability improves under tracked control conditions [@paperA2026].\n",
        encoding="utf-8",
    )
    document = parse_markdown_draft(draft)
    claim = _claim(section="Results")
    report = audit_draft(
        document,
        [_paper()],
        [PaperNote(paper_id="paper_a", claims=[claim])],
        [claim],
        [BibTeXEntry(entry_type="article", key="paperA2026")],
        [_theme()],
        project="demo",
        claim_lifecycle={"paper_a:c1": ClaimLifecycleRecord(claim_id="paper_a:c1", claim_status="deprecated")},
    )

    assert "matched_claim_deprecated" in {finding.code for finding in report.findings}


def test_dashboard_and_graph_accept_claim_lifecycle_metadata() -> None:
    claim = _claim(section="")
    queue = build_claim_review_queue([claim], [_paper()], [_theme()], {}, limit=5)
    dashboard = build_dashboard(
        project="demo",
        root=".",
        papers=[_paper()],
        notes=[PaperNote(paper_id="paper_a", claims=[claim])],
        claims=[claim],
        bibtex_entries=[],
        themes=[_theme()],
        claim_review_queue=queue,
    )
    graph = build_evidence_graph(
        project="demo",
        root=".",
        papers=[_paper()],
        bibtex_entries=[],
        notes=[PaperNote(paper_id="paper_a", claims=[claim])],
        themes=[_theme()],
        claim_lifecycle={"paper_a:c1": ClaimLifecycleRecord(claim_id="paper_a:c1", claim_status="deprecated")},
    )

    assert any(action.action_id == "claim_review:paper_a:c1" for action in dashboard.next_actions)
    assert analyze_graph(graph).deprecated_claims == ["paper_a:c1"]
    claim_nodes = [node for node in graph_to_json(graph)["nodes"] if node["node_type"] == "claim"]
    assert claim_nodes[0]["metadata"]["claim_status"] == "deprecated"


def test_claim_review_and_contradictions_cli_smoke(tmp_path: Path) -> None:
    data = tmp_path / "data"
    notes_dir = data / "notes"
    examples = data / "examples"
    notes_dir.mkdir(parents=True)
    examples.mkdir(parents=True)
    registry = data / "registries" / "papers.csv"
    save_registry([_paper()], registry)
    (notes_dir / "paper_a.md").write_text(
        """# Paper Note: Synthetic

## Metadata
- Paper ID: paper_a
- BibTeX key: paperA2026
- Tags: photocorrosion
- Reading status: skimmed

## Claims and evidence

### Claim 1
- Claim: Synthetic photocorrosion stability improves under tracked control conditions.
- Evidence type: experimental_result
- Section / page:
- Confidence: high
- Tags: photocorrosion
- Strength: strong
- Supports theme: photocorrosion
""",
        encoding="utf-8",
    )
    (examples / "themes.json").write_text(
        json.dumps({"themes": [{"theme_id": "photocorrosion", "name": "Photocorrosion", "tags": ["photocorrosion"], "min_papers": 1, "min_claims": 1}]}),
        encoding="utf-8",
    )

    help_result = run_cli(tmp_path, "claim-review", "--help")
    queue = run_cli(tmp_path, "claim-review", "queue")
    mark = run_cli(tmp_path, "claim-review", "mark", "paper_a:c1", "--status", "verified", "--verification-date", "2026-06-15")
    verified = run_cli(tmp_path, "claim-review", "verified")
    create = run_cli(tmp_path, "contradictions", "create", "--theme", "photocorrosion", "--group-id", "synthetic_group")
    add = run_cli(tmp_path, "contradictions", "add", "synthetic_group", "paper_a:c1")
    report = run_cli(tmp_path, "contradictions", "report")

    assert help_result.returncode == 0
    assert "queue" in help_result.stdout
    assert queue.returncode == 0, queue.stderr
    assert "paper_a:c1" in queue.stdout
    assert mark.returncode == 0, mark.stderr
    assert verified.returncode == 0
    assert "paper_a:c1" in verified.stdout
    assert create.returncode == 0, create.stderr
    assert add.returncode == 0, add.stderr
    assert report.returncode == 0, report.stderr
    assert "synthetic_group" in report.stdout
