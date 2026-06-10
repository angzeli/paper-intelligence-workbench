from __future__ import annotations

from paper_workbench.bibtex import parse_bibtex_file, validate_bibtex
from paper_workbench.claims import collect_notes
from paper_workbench.notes import parse_note_file

from conftest import FIXTURES


def test_note_edge_fixture_parses_conservatively():
    note = parse_note_file(FIXTURES / "notes" / "edge_case_note.md")
    assert note.paper_id == "edge_case_paper"
    assert len(note.claims) == 2
    assert note.claims[0].page == "12"
    assert "catalyst-stability" in note.claims[0].tags
    assert note.claims[1].section == ""
    assert any("Claim B is missing evidence location" in warning for warning in note.warnings)
    assert any("Claim 3 is missing claim text" in warning for warning in note.warnings)
    assert "personal notes" in note.personal_reading_notes.lower()


def test_note_edge_fixture_collects_orphan_note():
    notes = collect_notes(FIXTURES / "notes")
    ids = {note.paper_id for note in notes}
    assert {"edge_case_paper", "edge_orphan_without_registry"}.issubset(ids)


def test_bibtex_edge_fixture_reports_expected_findings():
    entries = parse_bibtex_file(FIXTURES / "bibtex" / "edge_cases.bib")
    assert len(entries) == 7
    assert entries[0].journal == "Synthetic Edge Journal"
    findings = validate_bibtex(entries)
    codes = {finding.code for finding in findings}
    assert "duplicate_bibtex_key" in codes
    assert "duplicate_bibtex_doi" in codes
    assert "missing_title" in codes
    assert "title_capitalization" in codes
    assert "bibtex_parse_warning" in codes
    assert "inconsistent_field_name" in codes
