from __future__ import annotations

import subprocess
import sys

from paper_workbench.audit import citation_audit
from paper_workbench.bibtex import parse_bibtex_file
from paper_workbench.claims import collect_claims, collect_notes
from paper_workbench.registry import load_registry
from paper_workbench.reporting import evidence_map_report, inventory_report, weak_claims_report
from paper_workbench.search import search_claims, search_note_files, search_papers
from paper_workbench.schema import Claim, ProjectTheme
from paper_workbench.tags import count_claim_tags, group_claims_by_theme, load_themes, normalize_tag

from conftest import EXAMPLE_BIBTEX, EXAMPLE_NOTES, EXAMPLE_REGISTRY, EXAMPLE_THEMES, ROOT


def test_tag_normalization_and_theme_mapping():
    assert normalize_tag("Charge Separation") == "charge-separation"
    claims = collect_claims(EXAMPLE_NOTES)
    themes = load_themes(EXAMPLE_THEMES)
    grouped = group_claims_by_theme(claims, themes)
    assert "charge-separation" in grouped
    assert count_claim_tags(claims)["photocorrosion"] == 1


def test_search_registry_claims_and_notes():
    papers = load_registry(EXAMPLE_REGISTRY)
    claims = collect_claims(EXAMPLE_NOTES)
    assert search_papers(papers, "charge separation")
    assert search_claims(claims, "rubric")
    assert search_note_files(EXAMPLE_NOTES, "photocorrosion")


def test_cli_search_report_uses_relative_paths_for_project_outputs(tmp_path):
    out = tmp_path / "search.md"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "paper_workbench.cli",
            "search",
            "photocorrosion",
            "--project",
            "zis_photocatalysis",
            "--out",
            str(out),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    content = out.read_text(encoding="utf-8")
    assert "/Users/" not in content
    assert "/private/" not in content
    assert "notes/zis_stability_2024.md" in content


def test_report_generation_contains_expected_sections():
    papers = load_registry(EXAMPLE_REGISTRY)
    claims = collect_claims(EXAMPLE_NOTES)
    themes = load_themes(EXAMPLE_THEMES)
    assert "# Paper Inventory Report" in inventory_report(papers)
    evidence_map = evidence_map_report(papers, claims, themes)
    assert "Literature Review Evidence Map" in evidence_map
    assert "charge separation" in evidence_map
    assert "Weak Claims Report" in weak_claims_report(claims)


def test_evidence_map_shows_undefined_theme_claims():
    claim = Claim(
        claim_id="synthetic:c1",
        paper_id="synthetic",
        claim_text="Synthetic claim with a typoed theme.",
        supports_theme="Typo Theme",
    )
    theme = ProjectTheme(theme_id="known-theme", name="Known Theme")
    report = evidence_map_report([], [claim], [theme])
    assert "Undefined Theme: typo-theme" in report
    assert "Synthetic claim with a typoed theme." in report


def test_citation_audit_finds_expected_gaps():
    papers = load_registry(EXAMPLE_REGISTRY)
    notes = collect_notes(EXAMPLE_NOTES)
    claims = collect_claims(EXAMPLE_NOTES)
    entries = parse_bibtex_file(EXAMPLE_BIBTEX)
    themes = load_themes(EXAMPLE_THEMES)
    findings = citation_audit(papers, notes, claims, entries, themes)
    codes = {finding.code for finding in findings}
    assert "paper_without_notes" in codes
    assert "claim_missing_evidence_location" in codes
    assert "theme_under_supported" in codes
