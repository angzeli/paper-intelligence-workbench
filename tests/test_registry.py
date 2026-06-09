from __future__ import annotations

from paper_workbench.registry import (
    add_paper,
    detect_duplicate_doi,
    detect_duplicate_title,
    load_registry,
    save_registry,
    validate_registry,
)

from conftest import EXAMPLE_REGISTRY


def test_registry_loads_example_papers():
    papers = load_registry(EXAMPLE_REGISTRY)
    assert len(papers) == 5
    assert papers[0].paper_id == "synth_charge_2024"
    assert papers[0].tags == ["charge-separation", "thin-film-fabrication", "catalyst-stability"]


def test_registry_round_trip_csv(tmp_path):
    papers = load_registry(EXAMPLE_REGISTRY)
    target = tmp_path / "papers.csv"
    save_registry(papers, target)
    reloaded = load_registry(target)
    assert [paper.paper_id for paper in reloaded] == [paper.paper_id for paper in papers]


def test_registry_validation_and_duplicate_detection():
    papers = load_registry(EXAMPLE_REGISTRY)
    findings = validate_registry(papers)
    codes = {finding.code for finding in findings}
    assert "duplicate_doi" in codes
    assert "missing_bibtex_key" in codes
    assert "10.0000/synthetic.charge.2024" in detect_duplicate_doi(papers)


def test_duplicate_title_detection():
    papers = load_registry(EXAMPLE_REGISTRY)
    duplicates = detect_duplicate_title(papers)
    assert "synthetic charge separation in layered photocatalyst films" in duplicates


def test_add_paper_generates_stable_id():
    papers = []
    paper = add_paper(papers, title="Local Synthetic Reading Note", authors="Dana Test", year="2026", tags="ML methodology")
    assert paper.paper_id.startswith("test_2026_local")
    assert paper.reading_status == "unread"
    assert paper.tags == ["ml-methodology"]
