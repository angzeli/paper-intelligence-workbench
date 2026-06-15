"""Synthetic evidence graph workflow example.

Run from the repository root:

    python examples/evidence_graph_workflow.py

The script uses the bundled synthetic project only. It does not read PDFs,
scrape publishers, use cloud APIs, or infer claims.
"""

from __future__ import annotations

from pathlib import Path

from paper_workbench.bibtex import parse_bibtex_file
from paper_workbench.claims import collect_notes
from paper_workbench.graph import (
    analyze_graph,
    graph_summary_markdown,
    graph_to_dot,
    graph_to_json_text,
    orphan_nodes_markdown,
    theme_connectivity_markdown,
)
from paper_workbench.graph import build_evidence_graph
from paper_workbench.io import write_text
from paper_workbench.registry import load_registry
from paper_workbench.tags import load_themes


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects" / "zis_photocatalysis"
SCRATCH = ROOT / "scratch" / "evidence_graph_demo"


def main() -> int:
    papers = load_registry(PROJECT / "registry.csv")
    notes = collect_notes(PROJECT / "notes")
    entries = parse_bibtex_file(PROJECT / "bibtex" / "library.bib")
    themes = load_themes(PROJECT / "themes.json")

    graph = build_evidence_graph(
        project="zis_photocatalysis",
        root=PROJECT,
        papers=papers,
        bibtex_entries=entries,
        notes=notes,
        themes=themes,
    )
    analytics = analyze_graph(graph)

    SCRATCH.mkdir(parents=True, exist_ok=True)
    write_text(SCRATCH / "evidence_graph_summary.md", graph_summary_markdown(graph, analytics), force=True)
    write_text(SCRATCH / "orphan_nodes.md", orphan_nodes_markdown(graph, analytics), force=True)
    write_text(SCRATCH / "theme_connectivity.md", theme_connectivity_markdown(graph, analytics), force=True)
    write_text(SCRATCH / "evidence_graph.json", graph_to_json_text(graph), force=True)
    write_text(SCRATCH / "evidence_graph.dot", graph_to_dot(graph), force=True)

    print(f"Graph nodes: {len(graph.nodes)}")
    print(f"Graph edges: {len(graph.edges)}")
    print(f"Orphan papers: {len(analytics.orphan_papers)}")
    print(f"Reports written under {SCRATCH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
