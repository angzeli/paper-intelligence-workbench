"""Synthetic manuscript QA workflow.

Run from the repository root:

    python examples/manuscript_qa_workflow.py

The script uses only synthetic project data and writes reports under scratch/.
"""

from __future__ import annotations

from pathlib import Path

from paper_workbench.bibtex import parse_bibtex_file
from paper_workbench.claims import collect_notes
from paper_workbench.io import write_text
from paper_workbench.manuscript import (
    audit_manuscript,
    build_claim_traceability,
    claim_traceability_report,
    manuscript_context_table_report,
    manuscript_qa_report,
    manuscript_revision_checklist_report,
)
from paper_workbench.registry import load_registry
from paper_workbench.tags import load_themes


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects" / "zis_photocatalysis"
DRAFT = ROOT / "drafts" / "synthetic_overconfident_section.md"
OUT = ROOT / "scratch" / "manuscript_qa_workflow"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    papers = load_registry(PROJECT / "registry.csv")
    notes = collect_notes(PROJECT / "notes")
    claims = [claim for note in notes for claim in note.claims]
    entries = parse_bibtex_file(PROJECT / "bibtex" / "library.bib")
    themes = load_themes(PROJECT / "themes.json")

    result = audit_manuscript(DRAFT, papers, notes, claims, entries, themes, project="zis_photocatalysis")
    trace_rows = build_claim_traceability(result.audit, claims, papers, themes, theme="photocorrosion")

    write_text(OUT / "manuscript_qa.md", manuscript_qa_report(result), force=True)
    write_text(OUT / "citation_context_table.md", manuscript_context_table_report(result), force=True)
    write_text(OUT / "claim_traceability.md", claim_traceability_report(trace_rows, draft_path=result.draft_path, project=result.project, theme="photocorrosion"), force=True)
    write_text(OUT / "revision_checklist.md", manuscript_revision_checklist_report(result), force=True)

    print(f"Wrote synthetic manuscript QA reports to {OUT}")
    print(f"Verdict: {result.verdict}")


if __name__ == "__main__":
    main()
