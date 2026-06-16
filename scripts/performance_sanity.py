from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from paper_workbench.audit import citation_audit
from paper_workbench.bibtex import parse_bibtex_file, validate_bibtex
from paper_workbench.claims import collect_notes
from paper_workbench.doctor import workspace_health
from paper_workbench.index import build_index_records, index_status, rebuild_index
from paper_workbench.io import write_text
from paper_workbench.registry import load_registry, validate_registry
from paper_workbench.reporting import evidence_map_report
from paper_workbench.synthetic import generate_synthetic_project
from paper_workbench.tags import load_themes


def _timed(label: str, timings: list[tuple[str, float]], func):
    start = perf_counter()
    result = func()
    timings.append((label, perf_counter() - start))
    return result


def build_report(papers: int, claims: int, themes: int) -> str:
    timings: list[tuple[str, float]] = []
    with tempfile.TemporaryDirectory(prefix="paperwb_perf_") as tmp:
        root = Path(tmp)
        summary = _timed(
            "generate synthetic project",
            timings,
            lambda: generate_synthetic_project(
                name="performance_sanity",
                root=root,
                papers=papers,
                claims=claims,
                themes=themes,
                domain="zis",
            ),
        )
        project = root / "projects" / summary.project
        registry_path = project / "registry.csv"
        bibtex_path = project / "bibtex" / "library.bib"
        notes_dir = project / "notes"
        themes_path = project / "themes.json"
        reports_dir = project / "reports"
        loaded_papers = _timed("load registry", timings, lambda: load_registry(registry_path))
        notes = _timed("parse notes and claims", timings, lambda: collect_notes(notes_dir))
        parsed_claims = [claim for note in notes for claim in note.claims]
        entries = _timed("parse BibTeX", timings, lambda: parse_bibtex_file(bibtex_path))
        theme_defs = _timed("load themes", timings, lambda: load_themes(themes_path))
        registry_findings = _timed("validate registry", timings, lambda: validate_registry(loaded_papers, root=project, claims=parsed_claims))
        bibtex_findings = _timed("validate BibTeX", timings, lambda: validate_bibtex(entries, loaded_papers))
        audit_findings = _timed(
            "citation audit",
            timings,
            lambda: citation_audit(loaded_papers, notes, parsed_claims, entries, theme_defs, root=project),
        )
        health_findings = _timed(
            "workspace doctor",
            timings,
            lambda: workspace_health(
                root=project,
                registry_path=registry_path,
                bibtex_path=bibtex_path,
                notes_dir=notes_dir,
                themes_path=themes_path,
                reports_dir=reports_dir,
            ),
        )
        index_records = _timed(
            "build search-index records",
            timings,
            lambda: build_index_records(
                project_id=summary.project,
                registry_path=registry_path,
                bibtex_path=bibtex_path,
                notes_dir=notes_dir,
                themes_path=themes_path,
            ),
        )
        index_path = project / ".paperwb" / "index.sqlite"
        index_rebuild_status = _timed(
            "rebuild SQLite search index",
            timings,
            lambda: rebuild_index(index_path, index_records, project_id=summary.project),
        )
        index_check = _timed(
            "check search-index status",
            timings,
            lambda: index_status(index_path, project_id=summary.project, current_records=index_records),
        )
        evidence_map = _timed("build evidence map", timings, lambda: evidence_map_report(loaded_papers, parsed_claims, theme_defs, notes))

    lines = [
        "# Performance Sanity Report",
        "",
        "This is a lightweight sanity check, not a strict benchmark.",
        "",
        "## Synthetic Workload",
        "",
        f"- Requested papers: {papers}",
        f"- Requested claims: {claims}",
        f"- Requested themes: {themes}",
        f"- Parsed papers: {len(loaded_papers)}",
        f"- Parsed notes: {len(notes)}",
            f"- Parsed claims: {len(parsed_claims)}",
            f"- Parsed BibTeX entries: {len(entries)}",
            f"- Search-index records: {len(index_records)}",
            "",
            "## Timings",
        "",
        "| Step | Seconds |",
        "| --- | ---: |",
    ]
    for label, seconds in timings:
        lines.append(f"| {label} | {seconds:.4f} |")
    lines.extend(
        [
            "",
            "## Validation Signal",
            "",
            f"- Registry findings: {len(registry_findings)}",
            f"- BibTeX findings: {len(bibtex_findings)}",
            f"- Citation-audit findings: {len(audit_findings)}",
            f"- Workspace-health findings: {len(health_findings)}",
            f"- Search-index warnings: {len(index_check.warnings)}",
            f"- Search-index records stored: {index_rebuild_status.total_records}",
            f"- Evidence-map size: {len(evidence_map)} characters",
            "",
            "## Result",
            "",
            "The workload completed locally without cloud services, LLM APIs, publisher scraping, or PDF assets.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a lightweight paperwb performance sanity check.")
    parser.add_argument("--papers", type=int, default=100, help="Number of synthetic papers to generate.")
    parser.add_argument("--claims", type=int, default=220, help="Number of synthetic claims to generate.")
    parser.add_argument("--themes", type=int, default=6, help="Number of synthetic themes to generate.")
    parser.add_argument("--out", default="scratch/performance_sanity.md", help="Markdown report path.")
    parser.add_argument("--force", action="store_true", help="Overwrite the output report if it already exists.")
    args = parser.parse_args()
    report = build_report(args.papers, args.claims, args.themes)
    target = write_text(args.out, report, force=args.force)
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
