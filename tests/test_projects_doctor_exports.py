from __future__ import annotations

from paper_workbench.claims import collect_claims, collect_notes
from paper_workbench.doctor import workspace_health
from paper_workbench.exports import export_claims_json, export_reading_list, export_registry_json
from paper_workbench.projects import create_project_profile, list_project_profiles, load_project_profile
from paper_workbench.registry import load_registry
from paper_workbench.reporting import section_outline_report, workspace_health_report
from paper_workbench.tags import load_themes

from conftest import ROOT, ZIS_PROJECT


def test_project_profile_creation_and_resolution(tmp_path):
    profile = create_project_profile("demo_project", root=tmp_path, description="Synthetic temp profile")
    assert profile.name == "demo_project"
    assert (tmp_path / "projects" / "demo_project" / "registry.csv").exists()
    reloaded = load_project_profile("demo_project", root=tmp_path)
    assert reloaded.registry_path == profile.registry_path
    assert list_project_profiles(tmp_path)[0].name == "demo_project"


def test_project_profile_fixture_paths_resolve():
    profile = load_project_profile("zis_photocatalysis", root=ROOT)
    assert profile.name == "zis_photocatalysis"
    assert profile.registry_path.endswith("projects/zis_photocatalysis/registry.csv")


def test_workspace_health_reports_project_gaps():
    profile = load_project_profile("zis_photocatalysis", root=ROOT)
    findings = workspace_health(
        root=profile.root,
        registry_path=profile.registry_path,
        bibtex_path=profile.bibtex_path,
        notes_dir=profile.notes_dir,
        themes_path=profile.themes_path,
        reports_dir=profile.reports_dir,
        profile=profile,
    )
    codes = {finding.code for finding in findings}
    assert "claim_missing_evidence_location" in codes
    assert "theme_under_supported" in codes or "theme_too_few_papers" in codes
    assert "Workspace Health Report" in workspace_health_report(findings)


def test_exports_write_json_and_reading_list(tmp_path):
    papers = load_registry(ZIS_PROJECT / "registry.csv")
    claims = collect_claims(ZIS_PROJECT / "notes")
    registry_json = export_registry_json(papers, tmp_path / "registry.json")
    claims_json = export_claims_json(claims, tmp_path / "claims.json")
    reading_list = export_reading_list(papers, tmp_path / "reading.md", tag="photocorrosion")
    assert registry_json.exists()
    assert claims_json.exists()
    assert "zis_stability_2024" in reading_list.read_text(encoding="utf-8")


def test_section_outline_uses_tracked_evidence_only():
    papers = load_registry(ZIS_PROJECT / "registry.csv")
    notes = collect_notes(ZIS_PROJECT / "notes")
    claims = collect_claims(ZIS_PROJECT / "notes")
    themes = load_themes(ZIS_PROJECT / "themes.json")
    outline = section_outline_report("photocorrosion", papers, claims, themes, notes)
    assert "evidence outline, not a drafted" in outline
    assert "zisStability2024" in outline
    assert "Too Weak to Use Confidently" in outline
