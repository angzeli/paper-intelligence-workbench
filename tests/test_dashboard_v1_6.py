from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from conftest import ROOT
from paper_workbench.dashboard import build_dashboard, dashboard_markdown, next_actions_markdown, project_health_summary_markdown
from paper_workbench.schema import Author, BibTeXEntry, Claim, Paper, PaperNote, ProjectTheme, ValidationFinding


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], cwd=ROOT, check=False, text=True, capture_output=True)


def _paper(paper_id: str, *, included: str = "", status: str = "unread") -> Paper:
    return Paper(
        paper_id=paper_id,
        title=f"Synthetic {paper_id}",
        authors=[Author(given="Synthetic", family="Reader", raw_name="Synthetic Reader")],
        year="2026",
        journal="Synthetic Dashboard Journal",
        bibtex_key=f"{paper_id}2026",
        reading_status=status,
        included_in_lit_review=included,
        tags=["photocorrosion"],
    )


def test_dashboard_aggregation_and_next_actions() -> None:
    papers = [_paper("missing_note", included="true"), _paper("weak_note", status="read")]
    note = PaperNote(
        paper_id="weak_note",
        claims=[
            Claim(
                claim_id="weak_claim",
                paper_id="weak_note",
                claim_text="Synthetic weak evidence needs checking.",
                strength="weak",
                confidence="low",
                supports_theme="photocorrosion",
            )
        ],
    )
    dashboard = build_dashboard(
        project="demo",
        root="projects/demo",
        papers=papers,
        notes=[note],
        claims=note.claims,
        bibtex_entries=[BibTeXEntry(entry_type="article", key="weak_note2026")],
        themes=[ProjectTheme(theme_id="photocorrosion", name="Photocorrosion", tags=["photocorrosion"])],
        bibtex_findings=[ValidationFinding("error", "missing_title", "Synthetic missing title.", identifier="weak_note2026")],
        limit=10,
    )

    assert dashboard.paper_count == 2
    assert dashboard.note_count == 1
    assert dashboard.claim_count == 1
    assert len(dashboard.missing_note_papers) == 1
    assert len(dashboard.weak_claims) == 1
    assert len(dashboard.missing_evidence_claims) == 1
    assert {action.action_id for action in dashboard.next_actions} >= {
        "missing_note:missing_note",
        "missing_evidence:weak_claim",
        "bibtex:missing_title:weak_note2026",
    }


def test_dashboard_markdown_views_render_tables() -> None:
    dashboard = build_dashboard(
        project="demo",
        root="projects/demo",
        papers=[],
        notes=[],
        claims=[],
        bibtex_entries=[],
        themes=[],
        limit=5,
    )

    assert "# Terminal Dashboard v1.6" in dashboard_markdown(dashboard)
    assert "# Next Actions v1.6" in next_actions_markdown(dashboard.next_actions)
    assert "# Project Health Summary v1.6" in project_health_summary_markdown(dashboard)


def test_dashboard_cli_project_smoke(tmp_path: Path) -> None:
    report = tmp_path / "dashboard.md"

    terminal = run_cli("dashboard", "--project", "zis_photocatalysis", "--limit", "3")
    written = run_cli("dashboard", "--project", "zis_photocatalysis", "--limit", "3", "--out", str(report))

    assert terminal.returncode == 0
    assert "Paper Workbench Dashboard - zis_photocatalysis" in terminal.stdout
    assert "Top next actions:" in terminal.stdout
    assert written.returncode == 0
    assert "# Terminal Dashboard v1.6" in report.read_text(encoding="utf-8")


def test_dashboard_cli_next_actions_and_health_views(tmp_path: Path) -> None:
    actions = tmp_path / "next_actions.md"
    health = tmp_path / "health.md"

    action_result = run_cli("dashboard", "--project", "zis_photocatalysis", "--view", "next-actions", "--out", str(actions))
    health_result = run_cli(
        "dashboard",
        "--project",
        "zis_photocatalysis",
        "--view",
        "health",
        "--manuscript",
        "drafts/synthetic_unknown_citations.md",
        "--out",
        str(health),
    )

    assert action_result.returncode == 0
    assert health_result.returncode == 0
    assert "Next Actions v1.6" in actions.read_text(encoding="utf-8")
    health_text = health.read_text(encoding="utf-8")
    assert "Project Health Summary v1.6" in health_text
    assert "Manuscript QA" in health_text


def test_dashboard_cli_refuses_to_overwrite_report(tmp_path: Path) -> None:
    report = tmp_path / "dashboard.md"
    report.write_text("existing\n", encoding="utf-8")

    result = run_cli("dashboard", "--project", "zis_photocatalysis", "--out", str(report))

    assert result.returncode == 2
    assert "already exists" in result.stderr
    assert report.read_text(encoding="utf-8") == "existing\n"
