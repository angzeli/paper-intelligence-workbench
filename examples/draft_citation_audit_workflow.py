"""Synthetic draft citation-audit workflow.

Run from the repository root:

    python examples/draft_citation_audit_workflow.py

The script uses checked-in synthetic data only and writes reports to scratch/.
"""

from __future__ import annotations

from pathlib import Path

from paper_workbench.bibtex import parse_bibtex_file
from paper_workbench.claims import collect_notes
from paper_workbench.drafts import (
    audit_draft,
    citation_coverage_report,
    draft_audit_markdown,
    paragraph_evidence_matrix_report,
    parse_markdown_draft,
    revision_checklist_report,
)
from paper_workbench.io import write_text
from paper_workbench.registry import load_registry
from paper_workbench.tags import load_themes


ROOT = Path(".")
PROJECT = ROOT / "projects" / "zis_photocatalysis"
DRAFT = ROOT / "drafts" / "synthetic_photocorrosion_section.md"
OUT_DIR = ROOT / "scratch" / "draft_citation_audit_workflow"


def main() -> int:
    papers = load_registry(PROJECT / "registry.csv")
    notes = collect_notes(PROJECT / "notes")
    claims = [claim for note in notes for claim in note.claims]
    entries = parse_bibtex_file(PROJECT / "bibtex" / "library.bib")
    themes = load_themes(PROJECT / "themes.json")
    document = parse_markdown_draft(DRAFT)
    report = audit_draft(document, papers, notes, claims, entries, themes, project="zis_photocatalysis")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_text(OUT_DIR / "draft_audit.md", draft_audit_markdown(report), force=True)
    write_text(OUT_DIR / "citation_coverage.md", citation_coverage_report(report), force=True)
    write_text(OUT_DIR / "paragraph_evidence_matrix.md", paragraph_evidence_matrix_report(report), force=True)
    write_text(OUT_DIR / "revision_checklist.md", revision_checklist_report(report), force=True)

    print(f"Draft paragraphs: {len(document.paragraphs)}")
    print(f"Citation keys: {len(report.citation_coverage)}")
    print(f"Audit findings: {len(report.findings)}")
    print(f"Wrote reports to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
