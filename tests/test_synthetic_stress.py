from __future__ import annotations

import pytest

from paper_workbench.claims import collect_claims, collect_notes
from paper_workbench.audit import citation_audit
from paper_workbench.bibtex import parse_bibtex_file, validate_bibtex
from paper_workbench.doctor import workspace_health
from paper_workbench.projects import load_project_profile
from paper_workbench.registry import load_registry, validate_registry
from paper_workbench.synthetic import generate_synthetic_project
from paper_workbench.tags import load_themes

from conftest import ROOT, STRESS_FINANCE_PROJECT, STRESS_ML_PROJECT, STRESS_ZIS_PROJECT


def test_synthetic_generator_creates_temp_project_and_refuses_overwrite(tmp_path):
    summary = generate_synthetic_project(name="synthetic_temp", root=tmp_path, papers=12, claims=24, themes=4, domain="ml")
    project = tmp_path / "projects" / "synthetic_temp"
    assert summary.papers == 12
    assert summary.claims == 25
    assert (project / "registry.csv").exists()
    assert (project / "bibtex" / "library.bib").exists()
    assert (project / "notes" / "orphan_synthetic_note.md").exists()
    assert len(collect_claims(project / "notes")) == 25
    with pytest.raises(FileExistsError):
        generate_synthetic_project(name="synthetic_temp", root=tmp_path, papers=3, claims=3, themes=2)


def test_checked_in_stress_corpus_size():
    projects = [STRESS_ZIS_PROJECT, STRESS_FINANCE_PROJECT, STRESS_ML_PROJECT]
    total_papers = sum(len(load_registry(project / "registry.csv")) for project in projects)
    total_notes = sum(len(collect_notes(project / "notes")) for project in projects)
    total_claims = sum(len(collect_claims(project / "notes")) for project in projects)
    total_themes = sum(len(load_themes(project / "themes.json")) for project in projects)
    assert total_papers >= 100
    assert total_notes >= 90
    assert total_claims >= 200
    assert total_themes >= 15


def test_stress_registry_contains_intentional_validation_findings():
    profile = load_project_profile("stress_zis_photocatalysis", root=ROOT)
    papers = load_registry(profile.registry_path)
    claims = collect_claims(profile.notes_dir)
    findings = validate_registry(papers, root=profile.root, claims=claims)
    codes = {finding.code for finding in findings}
    assert "duplicate_doi" in codes
    assert "duplicate_title" in codes
    assert "duplicate_bibtex_key" in codes
    assert "missing_local_pdf_path" in codes
    assert "included_without_claims" in codes


def test_stress_bibtex_contains_intentional_validation_findings():
    profile = load_project_profile("stress_zis_photocatalysis", root=ROOT)
    papers = load_registry(profile.registry_path)
    entries = parse_bibtex_file(profile.bibtex_path)
    findings = validate_bibtex(entries, papers)
    codes = {finding.code for finding in findings}
    assert len(entries) >= 40
    assert "duplicate_bibtex_key" in codes
    assert "duplicate_bibtex_doi" in codes
    assert "missing_author" in codes
    assert "invalid_year" in codes
    assert "bibtex_not_linked_to_registry" in codes


def test_citation_audit_order_is_stable_for_multi_tagged_stress_papers():
    profile = load_project_profile("stress_zis_photocatalysis", root=ROOT)
    papers = load_registry(profile.registry_path)
    notes = collect_notes(profile.notes_dir)
    claims = [claim for note in notes for claim in note.claims]
    entries = parse_bibtex_file(profile.bibtex_path)
    themes = load_themes(profile.themes_path)
    first = [finding.message for finding in citation_audit(papers, notes, claims, entries, themes, root=profile.root)]
    second = [finding.message for finding in citation_audit(papers, notes, claims, entries, themes, root=profile.root)]
    assert first == second


def test_workspace_health_order_is_stable_for_stress_project():
    profile = load_project_profile("stress_zis_photocatalysis", root=ROOT)
    kwargs = {
        "root": profile.root,
        "registry_path": profile.registry_path,
        "bibtex_path": profile.bibtex_path,
        "notes_dir": profile.notes_dir,
        "themes_path": profile.themes_path,
        "reports_dir": profile.reports_dir,
        "profile": profile,
    }
    first = [finding.message for finding in workspace_health(**kwargs)]
    second = [finding.message for finding in workspace_health(**kwargs)]
    assert first == second


def test_generated_stress_project_claim_distribution_is_parseable(tmp_path):
    summary = generate_synthetic_project(name="stress_distribution", root=tmp_path, papers=16, claims=48, themes=5, domain="zis")
    project = tmp_path / "projects" / summary.project
    claims = collect_claims(project / "notes")
    missing_location = [claim for claim in claims if not (claim.section or claim.page)]
    weak = [claim for claim in claims if claim.strength in {"weak", "speculative"}]
    undefined_theme = [claim for claim in claims if "undefined" in claim.supports_theme]
    assert len(claims) == 49
    assert missing_location
    assert weak
    assert undefined_theme
