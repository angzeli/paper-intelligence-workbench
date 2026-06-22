from __future__ import annotations

from paper_workbench.notes import parse_note
from paper_workbench.registry import add_paper, load_registry, validate_registry

from conftest import EXAMPLE_REGISTRY


def test_registry_v0_2_fields_load_from_example():
    papers = load_registry(EXAMPLE_REGISTRY)
    assert papers[0].source_type == "journal_article"
    assert papers[0].included_in_lit_review == "true"
    assert papers[0].reading_priority == "high"


def test_registry_v0_2_validation_rules(tmp_path):
    papers = []
    add_paper(
        papers,
        title="Malformed DOI Synthetic",
        authors="Alex Test",
        year="2026",
        doi="10.bad",
        reading_status="read",
        priority="urgent",
        source_type="unknown_source",
        relevance_score="7",
        included_in_lit_review="true",
        local_pdf_path="missing.pdf",
    )
    findings = validate_registry(papers, root=tmp_path, claims=[])
    codes = {finding.code for finding in findings}
    assert "invalid_priority" in codes
    assert "invalid_source_type" in codes
    assert "invalid_relevance_score" in codes
    assert "included_without_claims" in codes
    assert "read_paper_missing_notes_path" in codes
    assert "missing_local_pdf_path" in codes


def test_note_parser_tolerates_varied_claim_heading_and_personal_notes():
    markdown = """# Paper Note: Variant

## Metadata
- Paper ID: variant_1
- BibTeX key: variantKey
- Tags: ML methodology; evaluation
- Reading status: read

## One-sentence summary
Synthetic variant.

## Why this paper matters
It tests parser tolerance.

## Claims and evidence

### Evidence claim A
- Claim: The synthetic protocol records an evaluation rule.
- Evidence type: method_description
- Section / page: Appendix p. 8
- Quote or paraphrase: Synthetic paraphrase.
- Confidence: medium
- Strength: moderate
- Tags: ML methodology
- Supports theme: ML methodology
- User comment:

## Open questions
- Does this stay outside the claim?

## Personal reading notes
Extra manual notes are preserved.
"""
    note = parse_note(markdown)
    assert note.why_it_matters == "It tests parser tolerance."
    assert note.personal_reading_notes == "Extra manual notes are preserved."
    assert note.claims[0].supports_theme == "ML methodology"
    assert "Open questions" not in note.claims[0].supports_theme
