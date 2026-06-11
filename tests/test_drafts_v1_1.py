from __future__ import annotations

import subprocess
import sys

from conftest import EXAMPLE_BIBTEX, EXAMPLE_NOTES, EXAMPLE_REGISTRY, EXAMPLE_THEMES, ROOT, ZIS_PROJECT
from paper_workbench.bibtex import parse_bibtex_file
from paper_workbench.claims import collect_notes
from paper_workbench.drafts import (
    audit_draft,
    draft_audit_markdown,
    extract_citations,
    paragraph_evidence_matrix_report,
    parse_markdown_draft,
    revision_checklist_report,
)
from paper_workbench.registry import load_registry
from paper_workbench.tags import load_themes


DRAFTS = ROOT / "drafts"


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], cwd=ROOT, check=False, text=True, capture_output=True)


def load_project_inputs(project_path=ZIS_PROJECT):
    papers = load_registry(project_path / "registry.csv")
    notes = collect_notes(project_path / "notes")
    claims = [claim for note in notes for claim in note.claims]
    entries = parse_bibtex_file(project_path / "bibtex" / "library.bib")
    themes = load_themes(project_path / "themes.json")
    return papers, notes, claims, entries, themes


def test_extract_citations_supports_markdown_and_latex_patterns():
    text = "Mix [@smith2024; @lee2023] with \\citep{zhao2022,kim2021} and @solo2020."
    keys = [citation.key for citation in extract_citations(text)]
    assert keys == ["smith2024", "lee2023", "zhao2022", "kim2021", "solo2020"]


def test_extract_citations_preserves_mixed_syntax_source_order():
    text = "First @alpha2024, then \\cite{beta2025,gamma2026}, then [@delta2027]."
    keys = [citation.key for citation in extract_citations(text)]
    assert keys == ["alpha2024", "beta2025", "gamma2026", "delta2027"]


def test_parse_markdown_draft_extracts_sections_paragraphs_and_citations():
    document = parse_markdown_draft(DRAFTS / "synthetic_charge_separation_section.md")
    assert document.title == "Synthetic Charge Separation Draft Section"
    assert len(document.sections) == 2
    assert len(document.paragraphs) == 4
    assert document.paragraphs[1].citation_keys == ["zisCharge2025"]
    assert document.paragraphs[3].citation_keys == ["zisCharge2025", "zisStability2024"]


def test_draft_audit_flags_unknown_weak_review_and_uncited_theme_claims():
    document = parse_markdown_draft(DRAFTS / "synthetic_photocorrosion_section.md")
    report = audit_draft(document, *load_project_inputs(), project="zis_photocatalysis")
    codes = {finding.code for finding in report.findings}

    assert "citation_key_not_in_bibtex" in codes
    assert "citation_key_not_in_registry" in codes
    assert "cited_paper_only_weak_claims" in codes
    assert "paragraph_only_review_statement_evidence" in codes
    assert "strong_wording_with_weak_evidence" in codes
    assert "possible_unsupported_claim" in codes

    rendered = draft_audit_markdown(report)
    assert "does not rewrite the draft" in rendered
    assert "unknownPhotocorrosion2026" in rendered
    assert "strong wording" in rendered


def test_paragraph_evidence_matching_links_strong_local_claim():
    document = parse_markdown_draft(DRAFTS / "synthetic_charge_separation_section.md")
    report = audit_draft(document, *load_project_inputs(), project="zis_photocatalysis")
    matched = [match for paragraph in report.document.paragraphs for match in paragraph.linked_evidence_matches]

    assert any(match.claim_id == "zis_charge_2025:c1" and match.strength == "strong" for match in matched)
    matrix = paragraph_evidence_matrix_report(report)
    assert "heuristic evidence audit" in matrix
    assert "zis_charge_2025:c1" in matrix


def test_legacy_example_draft_detects_cited_paper_without_note_and_unlinked_bibtex():
    document = parse_markdown_draft(DRAFTS / "synthetic_weakly_cited_section.md")
    papers = load_registry(EXAMPLE_REGISTRY)
    notes = collect_notes(EXAMPLE_NOTES)
    claims = [claim for note in notes for claim in note.claims]
    entries = parse_bibtex_file(EXAMPLE_BIBTEX)
    themes = load_themes(EXAMPLE_THEMES)
    report = audit_draft(document, papers, notes, claims, entries, themes, project="default")
    codes = {finding.code for finding in report.findings}

    assert "cited_paper_without_note" in codes
    assert "cited_paper_low_reading_status" in codes
    assert "citation_key_not_in_registry" in codes
    checklist = revision_checklist_report(report)
    assert "syntheticAdsorb2022" in checklist
    assert "extraUnlinked2020" in checklist


def test_draft_cli_commands_generate_reports(tmp_path):
    draft = "drafts/synthetic_photocorrosion_section.md"
    outputs = {
        "parse": tmp_path / "parse.md",
        "citations": tmp_path / "citations.md",
        "audit": tmp_path / "audit.md",
        "checklist": tmp_path / "checklist.md",
        "evidence-matrix": tmp_path / "matrix.md",
    }

    parse = run_cli("draft", "parse", draft, "--out", str(outputs["parse"]))
    assert parse.returncode == 0, parse.stderr
    assert "Draft Parse Report" in outputs["parse"].read_text(encoding="utf-8")

    for command in ("citations", "audit", "checklist", "evidence-matrix"):
        result = run_cli("draft", command, draft, "--project", "zis_photocatalysis", "--out", str(outputs[command]))
        assert result.returncode == 0, result.stderr
        assert outputs[command].exists()

    assert "Draft Citation And Evidence Audit" in outputs["audit"].read_text(encoding="utf-8")
    assert "Draft Revision Checklist" in outputs["checklist"].read_text(encoding="utf-8")
    assert "Paragraph Evidence Matrix" in outputs["evidence-matrix"].read_text(encoding="utf-8")


def test_draft_cli_refuses_overwrite_without_force(tmp_path):
    out = tmp_path / "audit.md"
    out.write_text("existing\n", encoding="utf-8")
    result = run_cli("draft", "audit", "drafts/synthetic_charge_separation_section.md", "--project", "zis_photocatalysis", "--out", str(out))
    assert result.returncode == 2
    assert out.read_text(encoding="utf-8") == "existing\n"
    assert "already exists" in result.stderr
    assert "Traceback" not in result.stderr
