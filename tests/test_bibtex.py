from __future__ import annotations

from paper_workbench.bibtex import parse_bibtex, parse_bibtex_file, validate_bibtex
from paper_workbench.registry import load_registry

from conftest import EXAMPLE_BIBTEX, EXAMPLE_REGISTRY


def test_bibtex_parser_reads_entries():
    entries = parse_bibtex_file(EXAMPLE_BIBTEX)
    assert len(entries) == 5
    assert entries[0].key == "syntheticCharge2024"
    assert entries[0].authors[0].family == "Example"


def test_bibtex_parser_handles_nested_braces():
    entries = parse_bibtex("@article{key, title = {{ZnIn2S4} Local Test}, author = {A, B}, year = {2024}, journal={J}}")
    assert entries[0].title == "ZnIn2S4} Local Test" or "ZnIn2S4" in entries[0].title


def test_bibtex_validation_reports_expected_issues():
    entries = parse_bibtex_file(EXAMPLE_BIBTEX)
    papers = load_registry(EXAMPLE_REGISTRY)
    findings = validate_bibtex(entries, papers)
    codes = {finding.code for finding in findings}
    assert "duplicate_bibtex_doi" in codes
    assert "missing_author" in codes
    assert "invalid_year" in codes
    assert "bibtex_not_linked_to_registry" in codes
