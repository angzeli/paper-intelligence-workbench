from __future__ import annotations


from paper_workbench.audit import citation_audit
from paper_workbench.bibtex import parse_bibtex_file, validate_bibtex
from paper_workbench.claims import collect_notes
from paper_workbench.doctor import workspace_health
from paper_workbench.registry import load_registry
from paper_workbench.reporting import (
    bibtex_audit_report,
    citation_audit_report,
    evidence_map_report,
    inventory_report,
    missing_evidence_report,
    reading_status_report,
    section_outline_report,
    theme_coverage_dashboard_report,
    weak_claims_report,
    workspace_health_report,
)
from paper_workbench.tags import load_themes

from conftest import ROOT, STRESS_ZIS_PROJECT


GOLDEN_DIR = ROOT / "tests" / "golden" / "stress_zis_photocatalysis"


def _project_inputs():
    papers = load_registry(STRESS_ZIS_PROJECT / "registry.csv")
    notes = collect_notes(STRESS_ZIS_PROJECT / "notes")
    claims = [claim for note in notes for claim in note.claims]
    entries = parse_bibtex_file(STRESS_ZIS_PROJECT / "bibtex" / "library.bib")
    themes = load_themes(STRESS_ZIS_PROJECT / "themes.json")
    return papers, notes, claims, entries, themes


def _normalize_report(content: str) -> str:
    text = content.replace(str(ROOT), "<ROOT>")
    text = text.replace("\r\n", "\n")
    return text.rstrip() + "\n"


def build_stress_zis_golden_reports() -> dict[str, str]:
    papers, notes, claims, entries, themes = _project_inputs()
    bib_findings = validate_bibtex(entries, papers)
    audit_findings = citation_audit(papers, notes, claims, entries, themes, root=STRESS_ZIS_PROJECT)
    health_findings = workspace_health(
        root=STRESS_ZIS_PROJECT,
        registry_path=STRESS_ZIS_PROJECT / "registry.csv",
        bibtex_path=STRESS_ZIS_PROJECT / "bibtex" / "library.bib",
        notes_dir=STRESS_ZIS_PROJECT / "notes",
        themes_path=STRESS_ZIS_PROJECT / "themes.json",
        reports_dir=STRESS_ZIS_PROJECT / "reports",
    )
    reports = {
        "inventory.md": inventory_report(papers),
        "reading_status.md": reading_status_report(papers),
        "bibtex_audit.md": bibtex_audit_report(entries, bib_findings),
        "citation_audit.md": citation_audit_report(audit_findings),
        "evidence_map.md": evidence_map_report(papers, claims, themes, notes),
        "theme_dashboard.md": theme_coverage_dashboard_report(papers, claims, themes, notes),
        "weak_claims.md": weak_claims_report(claims),
        "missing_evidence.md": missing_evidence_report(claims),
        "workspace_health.md": workspace_health_report(health_findings),
        "section_outline_photocorrosion.md": section_outline_report("photocorrosion", papers, claims, themes, notes),
    }
    return {name: _normalize_report(content) for name, content in reports.items()}


def test_stress_zis_reports_match_golden_snapshots():
    reports = build_stress_zis_golden_reports()
    missing = [name for name in reports if not (GOLDEN_DIR / name).exists()]
    assert not missing, f"Missing golden report snapshots: {missing}"
    for name, content in reports.items():
        expected = _normalize_report((GOLDEN_DIR / name).read_text(encoding="utf-8"))
        assert content == expected, f"Golden report changed: {name}"


def test_golden_reports_keep_stress_scale_visible():
    reports = build_stress_zis_golden_reports()
    assert "Total papers: 45" in reports["inventory.md"]
    assert "Entries parsed: 44" in reports["bibtex_audit.md"]
    assert "| photocorrosion | 10 | 28 | 0 | 0 | 28 | 3 | 1 | high |" in reports["theme_dashboard.md"]
    assert "Claims missing evidence locations: 13" in reports["missing_evidence.md"]
