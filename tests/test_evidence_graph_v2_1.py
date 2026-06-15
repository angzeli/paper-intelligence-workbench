from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from conftest import ROOT
from paper_workbench import __version__
from paper_workbench.dogfood import create_dogfood_project
from paper_workbench.graph import (
    CLAIM,
    CONTAINS_CLAIM,
    PAPER,
    SUPPORTS_THEME,
    analyze_graph,
    build_evidence_graph,
    graph_summary_markdown,
    graph_to_dot,
    graph_to_json,
)
from paper_workbench.schema import Author, BibTeXEntry, Claim, Paper, PaperNote, ProjectTheme


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "paper_workbench.cli", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def _sample_graph():
    paper = Paper(
        paper_id="paper_a",
        title="Synthetic Evidence Paper",
        authors=[Author(given="Ada", family="Example", raw_name="Ada Example")],
        year="2026",
        bibtex_key="paperA2026",
        tags=["photocorrosion"],
        source_type="journal_article",
    )
    claim = Claim(
        claim_id="paper_a:c1",
        paper_id="paper_a",
        claim_text="Synthetic photocorrosion claim with a local section pointer.",
        evidence_type="experimental_result",
        section="Results",
        confidence="medium",
        strength="moderate",
        supports_theme="photocorrosion",
        tags=["photocorrosion"],
    )
    note = PaperNote(paper_id="paper_a", citation_key="paperA2026", claims=[claim], tags=["photocorrosion"])
    theme = ProjectTheme(theme_id="photocorrosion", name="Photocorrosion", tags=["photocorrosion"], min_papers=1, min_claims=1)
    return build_evidence_graph(
        project="demo",
        root=".",
        papers=[paper],
        bibtex_entries=[BibTeXEntry(entry_type="article", key="paperA2026", title="Synthetic Evidence Paper", year="2026")],
        notes=[note],
        themes=[theme],
    )


def test_graph_node_and_edge_creation() -> None:
    graph = _sample_graph()

    assert "paper:paper-a" in graph.nodes
    assert "claim:paper-ac1" in graph.nodes
    assert graph.nodes["paper:paper-a"].node_type == PAPER
    assert graph.nodes["claim:paper-ac1"].node_type == CLAIM
    assert any(edge.edge_type == CONTAINS_CLAIM for edge in graph.edges)
    assert any(edge.edge_type == SUPPORTS_THEME for edge in graph.edges)


def test_graph_analytics_detects_missing_links() -> None:
    paper = Paper(paper_id="orphan", title="Synthetic Orphan", authors=[], year="2026")
    note = PaperNote(paper_id="claimless")
    claim = Claim(claim_id="claimless:c1", paper_id="claimless", claim_text="Synthetic claim without theme or location.")
    graph = build_evidence_graph(
        project="demo",
        root=".",
        papers=[paper, Paper(paper_id="claimless", title="Synthetic Claimless", authors=[], year="2026")],
        bibtex_entries=[],
        notes=[PaperNote(paper_id="claimless", claims=[claim]), note],
        themes=[ProjectTheme(theme_id="empty-theme", name="Empty Theme", min_papers=1, min_claims=1)],
    )

    analytics = analyze_graph(graph)

    assert "orphan" in analytics.orphan_papers
    assert "claimless:c1" in analytics.claims_without_themes
    assert "claimless:c1" in analytics.claims_missing_evidence_locations
    assert "empty-theme" in analytics.isolated_themes


def test_graph_exports_json_and_dot() -> None:
    graph = _sample_graph()
    data = graph_to_json(graph)
    dot = graph_to_dot(graph)

    assert data["project"] == "demo"
    assert any(node["node_id"] == "paper:paper-a" for node in data["nodes"])
    assert any(edge["edge_type"] == "supports_theme" for edge in data["edges"])
    assert "digraph evidence_graph" in dot
    assert "paper:paper-a" in dot


def test_graph_summary_markdown_contains_boundaries() -> None:
    graph = _sample_graph()
    content = graph_summary_markdown(graph)

    assert f"Evidence Graph Summary v{__version__}" in content
    assert "v2.1" not in content
    assert "local evidence graph" in content
    assert "not a truth score" in content
    assert "Theme Connectivity" in content


def test_graph_cli_smoke_summary_and_exports(tmp_path: Path) -> None:
    summary = tmp_path / "graph_summary.md"
    json_out = tmp_path / "graph.json"
    dot_out = tmp_path / "graph.dot"

    help_result = run_cli("graph", "--help")
    build = run_cli("graph", "build", "--project", "zis_photocatalysis")
    summary_result = run_cli("graph", "summary", "--project", "zis_photocatalysis", "--out", str(summary))
    json_result = run_cli("graph", "export", "--project", "zis_photocatalysis", "--format", "json", "--out", str(json_out))
    dot_result = run_cli("graph", "export", "--project", "zis_photocatalysis", "--format", "dot", "--out", str(dot_out))

    assert help_result.returncode == 0
    assert "build" in help_result.stdout
    assert build.returncode == 0, build.stderr
    assert "Nodes:" in build.stdout
    assert summary_result.returncode == 0, summary_result.stderr
    assert json_result.returncode == 0, json_result.stderr
    assert dot_result.returncode == 0, dot_result.stderr
    summary_content = summary.read_text(encoding="utf-8")
    assert f"Evidence Graph Summary v{__version__}" in summary_content
    assert "v2.1" not in summary_content
    assert json.loads(json_out.read_text(encoding="utf-8"))["project"] == "zis_photocatalysis"
    assert "digraph evidence_graph" in dot_out.read_text(encoding="utf-8")


def test_empty_project_graph_behavior(tmp_path: Path) -> None:
    create_dogfood_project("generic", "empty_review", root=tmp_path)
    project = tmp_path / "projects" / "empty_review"

    result = run_cli(
        "graph",
        "build",
        "--registry",
        str(project / "registry.csv"),
        "--bibtex",
        str(project / "bibtex" / "library.bib"),
        "--notes-dir",
        str(project / "notes"),
        "--themes",
        str(project / "themes.json"),
    )

    assert result.returncode == 0, result.stderr
    assert "Built evidence graph for default" in result.stdout
    assert "Nodes:" in result.stdout
