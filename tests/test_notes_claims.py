from __future__ import annotations

import pytest

from paper_workbench.claims import collect_claims, save_claims_csv
from paper_workbench.notes import parse_note_file, write_note_template
from paper_workbench.registry import load_registry

from conftest import EXAMPLE_NOTES, EXAMPLE_REGISTRY


def test_note_parser_extracts_metadata_and_claim():
    note = parse_note_file(EXAMPLE_NOTES / "example_note_1.md")
    assert note.paper_id == "synth_charge_2024"
    assert note.citation_key == "syntheticCharge2024"
    assert note.claims[0].evidence_type == "experimental_result"
    assert note.claims[0].strength == "strong"
    assert note.claims[0].page == "4"


def test_note_parser_warns_for_missing_evidence_location():
    note = parse_note_file(EXAMPLE_NOTES / "example_note_2.md")
    assert any("missing evidence location" in warning for warning in note.warnings)
    assert note.claims[0].strength == "weak"


def test_note_template_generation_preserves_existing_file(tmp_path):
    paper = load_registry(EXAMPLE_REGISTRY)[0]
    target = tmp_path / "note.md"
    write_note_template(paper, output_path=target)
    with pytest.raises(FileExistsError):
        write_note_template(paper, output_path=target, force=False)


def test_claim_extraction_and_csv_output(tmp_path):
    claims = collect_claims(EXAMPLE_NOTES)
    assert len(claims) == 3
    target = tmp_path / "claims.csv"
    save_claims_csv(claims, target)
    assert "claim_id" in target.read_text(encoding="utf-8")
