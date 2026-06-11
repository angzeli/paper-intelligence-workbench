from __future__ import annotations

import subprocess
import sys

from conftest import ROOT, ZIS_PROJECT
from paper_workbench.bibtex import parse_bibtex_file
from paper_workbench.claims import collect_notes
from paper_workbench.drafts import extract_citations
from paper_workbench.manuscript import (
    audit_manuscript,
    build_claim_traceability,
    claim_traceability_report,
    manuscript_context_table_report,
    manuscript_qa_report,
    manuscript_readiness_verdict,
)
from paper_workbench.registry import load_registry
from paper_workbench.tags import load_themes


DRAFTS = ROOT / "drafts"


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], cwd=ROOT, check=False, text=True, capture_output=True)


def load_project_inputs():
    papers = load_registry(ZIS_PROJECT / "registry.csv")
    notes = collect_notes(ZIS_PROJECT / "notes")
    claims = [claim for note in notes for claim in note.claims]
    entries = parse_bibtex_file(ZIS_PROJECT / "bibtex" / "library.bib")
    themes = load_themes(ZIS_PROJECT / "themes.json")
    return papers, notes, claims, entries, themes


def test_manuscript_citation_parser_supports_markdown_latex_and_multiple_keys():
    text = "A [@alpha2024; @beta2025] B \\citealp{gamma2026,delta2027} C \\autocite{epsilon2028} D \\parencite{zeta2029}."
    keys = [citation.key for citation in extract_citations(text)]
    assert keys == ["alpha2024", "beta2025", "gamma2026", "delta2027", "epsilon2028", "zeta2029"]


def test_manuscript_qa_flags_unknown_and_overconfident_drafts():
    papers, notes, claims, entries, themes = load_project_inputs()
    unknown = audit_manuscript(DRAFTS / "synthetic_unknown_citations.md", papers, notes, claims, entries, themes, project="zis_photocatalysis")
    unknown_codes = {finding.code for finding in unknown.audit.findings}
    assert "citation_key_not_in_bibtex" in unknown_codes
    assert "citation_key_not_in_registry" in unknown_codes
    assert unknown.verdict == "needs citation cleanup"

    overconfident = audit_manuscript(DRAFTS / "synthetic_overconfident_section.md", papers, notes, claims, entries, themes, project="zis_photocatalysis")
    overconfident_codes = {finding.code for finding in overconfident.audit.findings}
    assert "strong_wording_with_weak_evidence" in overconfident_codes
    assert "paragraph_only_review_statement_evidence" in overconfident_codes
    assert manuscript_readiness_verdict(overconfident.audit) == "needs evidence strengthening"


def test_manuscript_context_table_and_traceability_reports():
    papers, notes, claims, entries, themes = load_project_inputs()
    result = audit_manuscript(DRAFTS / "synthetic_good_section.md", papers, notes, claims, entries, themes, project="zis_photocatalysis")
    context = manuscript_context_table_report(result)
    assert "Citation Context Table" in context
    assert "zisCharge2025" in context
    assert "zis_charge_2025:c1" in context
    assert "Results p. 3" in context

    rows = build_claim_traceability(result.audit, claims, papers, themes, theme="charge separation")
    trace = claim_traceability_report(rows, draft_path=result.draft_path, project=result.project, theme="charge separation")
    assert "Claim-to-Draft Traceability" in trace
    assert "zis_charge_2025:c1" in trace
    assert "p002" in trace


def test_manuscript_qa_report_includes_verdict_and_revision_checklist():
    papers, notes, claims, entries, themes = load_project_inputs()
    result = audit_manuscript(DRAFTS / "synthetic_review_only_support.md", papers, notes, claims, entries, themes, project="zis_photocatalysis")
    report = manuscript_qa_report(result)
    assert "Manuscript Citation QA Report" in report
    assert "Final readiness verdict:" in report
    assert "Revision Checklist" in report
    assert "review_statement" in report


def test_manuscript_cli_commands_generate_reports(tmp_path):
    draft = "drafts/synthetic_overconfident_section.md"
    outputs = {
        "parse": tmp_path / "parse.md",
        "citations": tmp_path / "citations.md",
        "qa": tmp_path / "qa.md",
        "checklist": tmp_path / "checklist.md",
        "context-table": tmp_path / "context.md",
        "trace-claims": tmp_path / "trace.md",
        "evidence-matrix": tmp_path / "matrix.md",
    }

    parse = run_cli("manuscript", "parse", draft, "--out", str(outputs["parse"]))
    assert parse.returncode == 0, parse.stderr
    assert "Manuscript Parse Report" in outputs["parse"].read_text(encoding="utf-8")

    for command in ("citations", "qa", "checklist", "context-table", "evidence-matrix"):
        result = run_cli("manuscript", command, draft, "--project", "zis_photocatalysis", "--out", str(outputs[command]))
        assert result.returncode == 0, result.stderr
        assert outputs[command].exists()

    trace = run_cli("manuscript", "trace-claims", draft, "--project", "zis_photocatalysis", "--theme", "photocorrosion", "--out", str(outputs["trace-claims"]))
    assert trace.returncode == 0, trace.stderr
    assert "Manuscript Citation QA Report" in outputs["qa"].read_text(encoding="utf-8")
    assert "Citation Context Table" in outputs["context-table"].read_text(encoding="utf-8")
    assert "Claim-to-Draft Traceability" in outputs["trace-claims"].read_text(encoding="utf-8")


def test_manuscript_cli_refuses_overwrite_without_force(tmp_path):
    out = tmp_path / "qa.md"
    out.write_text("existing\n", encoding="utf-8")
    result = run_cli("manuscript", "qa", "drafts/synthetic_good_section.md", "--project", "zis_photocatalysis", "--out", str(out))
    assert result.returncode == 2
    assert out.read_text(encoding="utf-8") == "existing\n"
    assert "already exists" in result.stderr
