"""Command-line interface for paper-intelligence-workbench."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .audit import citation_audit
from .bibtex import parse_bibtex_file, validate_bibtex
from .claims import collect_claims, collect_notes, save_claims_csv
from .init import init_workspace
from .notes import write_note_template
from .paths import default_bibtex_path, default_notes_dir, default_registry_path, default_reports_dir, default_themes_path
from .registry import add_paper, create_empty_registry, display_authors, filter_papers, load_registry, save_registry, save_registry_json, validate_registry
from .reporting import (
    bibtex_audit_report,
    citation_audit_report,
    claims_grouped_by_theme_report,
    evidence_map_report,
    inventory_report,
    missing_notes_report,
    papers_by_tag_report,
    reading_status_report,
    theme_coverage_dashboard_report,
    weak_claims_report,
    write_report,
)
from .search import search_claims, search_note_files, search_papers
from .tags import load_themes


def _path(value: str | Path) -> Path:
    return Path(value).expanduser()


def _load_registry(path: str | Path) -> list:
    target = _path(path)
    if not target.exists():
        create_empty_registry(target)
    return load_registry(target)


def _print_findings(findings) -> None:
    if not findings:
        print("No findings.")
        return
    for finding in findings:
        identifier = getattr(finding, "identifier", "") or getattr(finding, "paper_id", "") or getattr(finding, "claim_id", "") or getattr(finding, "theme", "")
        suffix = f" [{identifier}]" if identifier else ""
        suggestion = f" Suggestion: {finding.suggestion}" if getattr(finding, "suggestion", "") else ""
        print(f"{finding.severity.upper()} {finding.code}{suffix}: {finding.message}{suggestion}")


def cmd_init(args: argparse.Namespace) -> int:
    created = init_workspace(args.root)
    print(f"Initialized workspace at {_path(args.root).resolve()}")
    if created:
        print("Created:")
        for directory in created:
            print(f"  {directory}")
    else:
        print("No folders needed to be created.")
    return 0


def cmd_validate_registry(args: argparse.Namespace) -> int:
    papers = load_registry(args.registry)
    findings = validate_registry(papers)
    _print_findings(findings)
    if args.json:
        save_registry_json(papers, args.json)
        print(f"Wrote JSON registry to {args.json}")
    return 1 if args.strict and any(finding.severity == "error" for finding in findings) else 0


def cmd_validate_bib(args: argparse.Namespace) -> int:
    entries = parse_bibtex_file(args.bibtex)
    papers = load_registry(args.registry) if args.registry and Path(args.registry).exists() else None
    findings = validate_bibtex(entries, papers)
    _print_findings(findings)
    if args.report:
        path = write_report("bibtex_audit", bibtex_audit_report(entries, findings), Path(args.report).parent)
        if path != Path(args.report):
            Path(args.report).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Wrote report to {args.report}")
    return 1 if args.strict and any(finding.severity == "error" for finding in findings) else 0


def cmd_add_paper(args: argparse.Namespace) -> int:
    registry_path = _path(args.registry)
    papers = _load_registry(registry_path)
    paper = add_paper(
        papers,
        title=args.title,
        authors=args.authors,
        year=args.year,
        journal=args.journal,
        doi=args.doi,
        url=args.url,
        local_pdf_path=args.local_pdf_path,
        bibtex_key=args.bibtex_key,
        tags=args.tags,
        reading_status=args.status,
        notes_path=args.notes_path,
        priority=args.priority,
        user_comment=args.comment,
        paper_id=args.paper_id,
    )
    save_registry(papers, registry_path)
    print(f"Added {paper.paper_id}: {paper.title}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    papers = _load_registry(args.registry)
    papers = filter_papers(
        papers,
        tag=args.tag or "",
        year=args.year or "",
        journal=args.journal or "",
        status=args.status or "",
        priority=args.priority or "",
        author=args.author or "",
    )
    if not papers:
        print("No papers found.")
        return 0
    for paper in papers:
        print(f"{paper.paper_id}\t{paper.year}\t{paper.reading_status}\t{paper.title}\t{display_authors(paper.authors)}")
    return 0


def cmd_note_template(args: argparse.Namespace) -> int:
    papers = _load_registry(args.registry)
    paper = next((item for item in papers if item.paper_id == args.paper_id), None)
    if paper is None:
        print(f"Unknown paper_id: {args.paper_id}", file=sys.stderr)
        return 2
    path = write_note_template(paper, notes_dir=args.notes_dir, output_path=args.output, force=args.force)
    print(f"Wrote note template to {path}")
    return 0


def cmd_claims(args: argparse.Namespace) -> int:
    claims = collect_claims(args.notes_path)
    if args.output:
        save_claims_csv(claims, args.output)
        print(f"Wrote {len(claims)} claims to {args.output}")
    else:
        for claim in claims:
            print(f"{claim.claim_id}\t{claim.paper_id}\t{claim.strength}\t{claim.claim_text}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    selected = args.claims or args.notes
    results = []
    if not selected:
        papers = _load_registry(args.registry)
        results.extend(search_papers(papers, args.query))
        if Path(args.notes_dir).exists():
            results.extend(search_note_files(args.notes_dir, args.query))
            results.extend(search_claims(collect_claims(args.notes_dir), args.query))
    else:
        if args.notes:
            results.extend(search_note_files(args.notes_dir, args.query))
        if args.claims:
            results.extend(search_claims(collect_claims(args.notes_dir), args.query))
    for result in results:
        path = f"\t{result['path']}" if result.get("path") else ""
        print(f"{result['kind']}\t{result['id']}\t{result['title']}{path}")
    if not results:
        print("No matches.")
    return 0


def _report_inputs(args: argparse.Namespace):
    papers = _load_registry(args.registry)
    notes = collect_notes(args.notes_dir) if Path(args.notes_dir).exists() else []
    claims = []
    for note in notes:
        claims.extend(note.claims)
    entries = parse_bibtex_file(args.bibtex) if Path(args.bibtex).exists() else []
    themes = load_themes(args.themes) if Path(args.themes).exists() else []
    return papers, notes, claims, entries, themes


def cmd_report(args: argparse.Namespace) -> int:
    reports_dir = _path(args.reports_dir)
    papers, notes, claims, entries, themes = _report_inputs(args)
    bib_findings = validate_bibtex(entries, papers) if entries else []
    audit_findings = citation_audit(papers, notes, claims, entries, themes, root=Path("."))
    builders = {
        "inventory": lambda: inventory_report(papers),
        "reading-status": lambda: reading_status_report(papers),
        "papers-by-tag": lambda: papers_by_tag_report(papers),
        "bibtex-audit": lambda: bibtex_audit_report(entries, bib_findings),
        "claims-by-theme": lambda: claims_grouped_by_theme_report(claims, themes),
        "evidence-map": lambda: evidence_map_report(papers, claims, themes, notes),
        "citation-audit": lambda: citation_audit_report(audit_findings),
        "missing-notes": lambda: missing_notes_report(papers, notes),
        "weak-claims": lambda: weak_claims_report(claims),
        "theme-dashboard": lambda: theme_coverage_dashboard_report(papers, claims, themes, notes),
    }
    selected = list(builders) if args.report_type == "all" else [args.report_type]
    for name in selected:
        path = write_report(name.replace("-", "_"), builders[name](), reports_dir)
        print(f"Wrote {path}")
    return 0


def cmd_checklist(args: argparse.Namespace) -> int:
    papers, notes, claims, entries, themes = _report_inputs(args)
    theme_id = args.theme.lower().replace(" ", "-").replace("_", "-")
    relevant = [theme for theme in themes if theme.theme_id == theme_id or theme.name.lower() == args.theme.lower()]
    if not relevant:
        print(f"Unknown theme: {args.theme}", file=sys.stderr)
        return 2
    theme = relevant[0]
    mapped_claims = [claim for claim in claims if theme.theme_id in claim.supports_theme.lower().replace(" ", "-") or theme.theme_id in claim.tags]
    note_ids = {note.paper_id for note in notes}
    print(f"# Review Checklist: {theme.name}")
    print()
    for paper in papers:
        if theme.theme_id in paper.tags or any(claim.paper_id == paper.paper_id for claim in mapped_claims):
            status = "notes" if paper.paper_id in note_ids else "missing notes"
            print(f"- [ ] {paper.paper_id}: {paper.title} ({status})")
            for claim in [claim for claim in mapped_claims if claim.paper_id == paper.paper_id]:
                evidence = claim.section or claim.page or "missing evidence location"
                print(f"  - [ ] {claim.strength}: {claim.claim_text} [{evidence}]")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="paperwb", description="Local-first academic paper registry, notes, claims, BibTeX, and audit workbench.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create the local workbench folder structure.")
    init_parser.add_argument("--root", default=".", help="Workspace root to initialize.")
    init_parser.set_defaults(func=cmd_init)

    validate_registry_parser = subparsers.add_parser("validate-registry", help="Validate a CSV paper registry.")
    validate_registry_parser.add_argument("registry", help="Registry CSV path.")
    validate_registry_parser.add_argument("--json", help="Optional JSON export path.")
    validate_registry_parser.add_argument("--strict", action="store_true", help="Return non-zero when errors are found.")
    validate_registry_parser.set_defaults(func=cmd_validate_registry)

    validate_bib_parser = subparsers.add_parser("validate-bib", help="Validate a BibTeX library.")
    validate_bib_parser.add_argument("bibtex", help="BibTeX file path.")
    validate_bib_parser.add_argument("--registry", default="", help="Optional registry CSV path for link checks.")
    validate_bib_parser.add_argument("--report", help="Optional Markdown report path.")
    validate_bib_parser.add_argument("--strict", action="store_true", help="Return non-zero when errors are found.")
    validate_bib_parser.set_defaults(func=cmd_validate_bib)

    add_parser = subparsers.add_parser("add-paper", help="Add a paper row to the registry.")
    add_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    add_parser.add_argument("--paper-id", default="", help="Optional explicit paper ID.")
    add_parser.add_argument("--title", required=True, help="Paper title.")
    add_parser.add_argument("--authors", default="", help="Authors separated by ';' or BibTeX 'and'.")
    add_parser.add_argument("--year", default="", help="Publication year.")
    add_parser.add_argument("--journal", default="", help="Journal, venue, or source.")
    add_parser.add_argument("--doi", default="", help="DOI.")
    add_parser.add_argument("--url", default="", help="URL.")
    add_parser.add_argument("--local-pdf-path", default="", help="Workspace-relative local PDF path.")
    add_parser.add_argument("--bibtex-key", default="", help="BibTeX citation key.")
    add_parser.add_argument("--tags", default="", help="Tags separated by ';', ',', or '|'.")
    add_parser.add_argument("--status", default="unread", help="Reading status.")
    add_parser.add_argument("--notes-path", default="", help="Workspace-relative notes path.")
    add_parser.add_argument("--priority", default="", help="User-defined priority.")
    add_parser.add_argument("--comment", default="", help="User comment.")
    add_parser.set_defaults(func=cmd_add_paper)

    list_parser = subparsers.add_parser("list", help="List registry papers with optional filters.")
    list_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    list_parser.add_argument("--tag", help="Filter by tag.")
    list_parser.add_argument("--status", help="Filter by reading status.")
    list_parser.add_argument("--year", help="Filter by year.")
    list_parser.add_argument("--journal", help="Filter by journal substring.")
    list_parser.add_argument("--priority", help="Filter by priority.")
    list_parser.add_argument("--author", help="Filter by author substring.")
    list_parser.set_defaults(func=cmd_list)

    note_parser = subparsers.add_parser("note-template", help="Generate a structured Markdown note template for a paper.")
    note_parser.add_argument("paper_id", help="Paper ID from the registry.")
    note_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    note_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
    note_parser.add_argument("--output", help="Optional output path.")
    note_parser.add_argument("--force", action="store_true", help="Overwrite an existing note file.")
    note_parser.set_defaults(func=cmd_note_template)

    claims_parser = subparsers.add_parser("claims", help="Extract claims from structured notes.")
    claims_parser.add_argument("notes_path", help="Notes directory or Markdown note file.")
    claims_parser.add_argument("--output", help="Optional output CSV path.")
    claims_parser.set_defaults(func=cmd_claims)

    search_parser = subparsers.add_parser("search", help="Search registry, notes, or claims with simple substring matching.")
    search_parser.add_argument("query", help="Search query.")
    search_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    search_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
    search_parser.add_argument("--claims", action="store_true", help="Search extracted claims only.")
    search_parser.add_argument("--notes", action="store_true", help="Search note bodies only.")
    search_parser.set_defaults(func=cmd_search)

    report_parser = subparsers.add_parser("report", help="Generate Markdown reports.")
    report_parser.add_argument(
        "report_type",
        choices=[
            "inventory",
            "reading-status",
            "papers-by-tag",
            "bibtex-audit",
            "claims-by-theme",
            "evidence-map",
            "citation-audit",
            "missing-notes",
            "weak-claims",
            "theme-dashboard",
            "all",
        ],
    )
    report_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    report_parser.add_argument("--bibtex", default=str(default_bibtex_path()), help="BibTeX file path.")
    report_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
    report_parser.add_argument("--themes", default=str(default_themes_path()), help="Themes JSON path.")
    report_parser.add_argument("--reports-dir", default=str(default_reports_dir()), help="Reports output directory.")
    report_parser.set_defaults(func=cmd_report)

    checklist_parser = subparsers.add_parser("checklist", help="Generate a theme review checklist.")
    checklist_parser.add_argument("--theme", required=True, help="Theme name or ID.")
    checklist_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    checklist_parser.add_argument("--bibtex", default=str(default_bibtex_path()), help="BibTeX file path.")
    checklist_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
    checklist_parser.add_argument("--themes", default=str(default_themes_path()), help="Themes JSON path.")
    checklist_parser.set_defaults(func=cmd_checklist)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
