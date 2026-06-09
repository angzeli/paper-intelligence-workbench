"""End-to-end synthetic literature-review workflow.

Run from the repository root:

    python examples/end_to_end_workflow.py

The script uses a temporary workspace and synthetic data only.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from paper_workbench.bibtex import parse_bibtex_file, validate_bibtex
from paper_workbench.claims import collect_claims, collect_notes
from paper_workbench.doctor import workspace_health
from paper_workbench.exports import export_claims_csv
from paper_workbench.init import init_workspace
from paper_workbench.notes import write_note_template
from paper_workbench.projects import create_project_profile
from paper_workbench.registry import load_registry, validate_registry
from paper_workbench.reporting import citation_audit_report, evidence_map_report, section_outline_report, workspace_health_report
from paper_workbench.audit import citation_audit
from paper_workbench.tags import load_themes


def main() -> int:
    source_project = ROOT / "projects" / "zis_photocatalysis"
    with tempfile.TemporaryDirectory(prefix="paperwb_e2e_") as tmp:
        workspace = Path(tmp)
        init_workspace(workspace)
        profile = create_project_profile("demo_review", root=workspace)

        shutil.copyfile(source_project / "registry.csv", profile.registry_path)
        shutil.copyfile(source_project / "bibtex" / "library.bib", profile.bibtex_path)
        shutil.copyfile(source_project / "themes.json", profile.themes_path)
        shutil.copytree(source_project / "notes", profile.notes_dir, dirs_exist_ok=True)

        papers = load_registry(profile.registry_path)
        entries = parse_bibtex_file(profile.bibtex_path)
        notes = collect_notes(profile.notes_dir)
        claims = collect_claims(profile.notes_dir)
        themes = load_themes(profile.themes_path)

        template_path = write_note_template(papers[0], notes_dir=Path(profile.notes_dir), output_path=workspace / "template_preview.md", force=True)
        registry_findings = validate_registry(papers, root=profile.root, claims=claims)
        bibtex_findings = validate_bibtex(entries, papers)
        audit_findings = citation_audit(papers, notes, claims, entries, themes, root=profile.root)
        health_findings = workspace_health(
            root=profile.root,
            registry_path=profile.registry_path,
            bibtex_path=profile.bibtex_path,
            notes_dir=profile.notes_dir,
            themes_path=profile.themes_path,
            reports_dir=profile.reports_dir,
            profile=profile,
        )

        reports = Path(profile.reports_dir)
        reports.mkdir(parents=True, exist_ok=True)
        (reports / "evidence_map.md").write_text(evidence_map_report(papers, claims, themes, notes), encoding="utf-8")
        (reports / "citation_audit.md").write_text(citation_audit_report(audit_findings), encoding="utf-8")
        (reports / "section_outline.md").write_text(section_outline_report("photocorrosion", papers, claims, themes, notes), encoding="utf-8")
        (reports / "workspace_health.md").write_text(workspace_health_report(health_findings), encoding="utf-8")
        export_claims_csv(claims, reports / "claims.csv")

        print("workspace", workspace)
        print("project", profile.name)
        print("papers", len(papers))
        print("claims", len(claims))
        print("registry_findings", len(registry_findings))
        print("bibtex_findings", len(bibtex_findings))
        print("audit_findings", len(audit_findings))
        print("template", template_path.name)
        print("reports", sorted(path.name for path in reports.iterdir()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
