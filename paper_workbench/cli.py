"""Command-line interface for paper-intelligence-workbench."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .audit import citation_audit
from .bibtex import parse_bibtex_file, validate_bibtex
from .claims import collect_claims, collect_notes, save_claims_csv
from .doctor import workspace_health
from .exports import export_claims_csv, export_claims_json, export_reading_list, export_registry_csv, export_registry_json, export_theme_claims
from .init import init_workspace
from .io import write_text
from .notes import write_note_template
from .paths import default_bibtex_path, default_notes_dir, default_registry_path, default_reports_dir, default_themes_path
from .projects import create_project_profile, list_project_profiles, profile_summary, resolve_project_profile
from .registry import add_paper, create_empty_registry, display_authors, filter_papers, load_registry, save_registry, save_registry_json, validate_registry
from .reporting import (
    bibtex_audit_report,
    citation_audit_report,
    claims_grouped_by_theme_report,
    evidence_map_report,
    inventory_report,
    missing_evidence_report,
    missing_notes_report,
    papers_by_tag_report,
    reading_status_report,
    section_outline_report,
    theme_coverage_dashboard_report,
    weak_claims_report,
    workspace_health_report,
    write_report,
)
from .search import results_markdown, search_claims, search_note_files, search_papers
from .synthetic import generate_synthetic_project
from .tags import load_themes, normalize_tag


def _path(value: str | Path) -> Path:
    return Path(value).expanduser()


def _load_registry(path: str | Path, *, create_if_missing: bool = False) -> list:
    target = _path(path)
    if not target.exists():
        if not create_if_missing:
            raise FileNotFoundError(f"Registry not found: {target}")
        create_empty_registry(target)
    return load_registry(target)


PATH_DEFAULTS = {
    "registry": str(default_registry_path()),
    "bibtex": str(default_bibtex_path()),
    "notes_dir": str(default_notes_dir()),
    "themes": str(default_themes_path()),
    "reports_dir": str(default_reports_dir()),
}


def _reject_project_path_overrides(args: argparse.Namespace, fields: tuple[str, ...]) -> None:
    if not getattr(args, "project", ""):
        return
    for field in fields:
        if not hasattr(args, field):
            continue
        value = getattr(args, field)
        if value and str(value) != PATH_DEFAULTS[field]:
            option = f"--{field.replace('_', '-')}"
            raise ValueError(f"--project cannot be combined with {option}; project profile paths are used instead.")


def _theme_exists(theme_query: str, themes) -> bool:
    wanted = normalize_tag(theme_query)
    return any(theme.theme_id == wanted or normalize_tag(theme.name) == wanted for theme in themes)


def _registry_validation_root(path: str | Path) -> Path:
    target = Path(path)
    if target.name == "registry.csv" and target.parent.parent.name == "projects":
        return target.parent
    if target.parent.name == "registries" and target.parent.parent.name == "data":
        return target.parent.parent.parent
    return Path(".")


def _paths_from_args(args: argparse.Namespace) -> dict[str, Path | None]:
    profile = resolve_project_profile(getattr(args, "project", None))
    if profile is not None:
        return {
            "profile": profile,
            "root": Path(profile.root),
            "registry": Path(profile.registry_path),
            "bibtex": Path(profile.bibtex_path),
            "notes_dir": Path(profile.notes_dir),
            "themes": Path(profile.themes_path),
            "reports_dir": Path(profile.reports_dir),
        }
    return {
        "profile": None,
        "root": Path("."),
        "registry": Path(getattr(args, "registry", default_registry_path())),
        "bibtex": Path(getattr(args, "bibtex", default_bibtex_path())),
        "notes_dir": Path(getattr(args, "notes_dir", default_notes_dir())),
        "themes": Path(getattr(args, "themes", default_themes_path())),
        "reports_dir": Path(getattr(args, "reports_dir", default_reports_dir())),
    }


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
    findings = validate_registry(papers, root=_registry_validation_root(args.registry))
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
        path = write_text(args.report, bibtex_audit_report(entries, findings), force=args.force)
        print(f"Wrote report to {path}")
    return 1 if args.strict and any(finding.severity == "error" for finding in findings) else 0


def cmd_add_paper(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry",))
    paths = _paths_from_args(args)
    registry_path = _path(paths["registry"])
    papers = _load_registry(registry_path, create_if_missing=True)
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
        project=args.project or "",
        source_type=args.source_type,
        relevance_score=args.relevance_score,
        reading_priority=args.reading_priority,
        included_in_lit_review=args.included,
        exclude_reason=args.exclude_reason,
        user_comment=args.comment,
        paper_id=args.paper_id,
    )
    save_registry(papers, registry_path)
    print(f"Added {paper.paper_id}: {paper.title}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry",))
    paths = _paths_from_args(args)
    papers = _load_registry(paths["registry"])
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
    _reject_project_path_overrides(args, ("registry", "notes_dir"))
    paths = _paths_from_args(args)
    papers = _load_registry(paths["registry"])
    paper = next((item for item in papers if item.paper_id == args.paper_id), None)
    if paper is None:
        print(f"Unknown paper_id: {args.paper_id}", file=sys.stderr)
        return 2
    path = write_note_template(paper, notes_dir=paths["notes_dir"], output_path=args.output, force=args.force)
    print(f"Wrote note template to {path}")
    return 0


def cmd_claims(args: argparse.Namespace) -> int:
    if getattr(args, "project", "") and args.notes_path:
        raise ValueError("--project cannot be combined with notes_path; project profile notes are used instead.")
    paths = _paths_from_args(args)
    notes_path = Path(args.notes_path) if args.notes_path else paths["notes_dir"]
    claims = collect_claims(notes_path)
    if args.output:
        save_claims_csv(claims, args.output)
        print(f"Wrote {len(claims)} claims to {args.output}")
    else:
        for claim in claims:
            print(f"{claim.claim_id}\t{claim.paper_id}\t{claim.strength}\t{claim.claim_text}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry", "notes_dir"))
    paths = _paths_from_args(args)
    selected = args.claims or args.notes
    results = []
    if not selected:
        papers = _load_registry(paths["registry"])
        results.extend(search_papers(papers, args.query, exact=args.exact))
        if Path(paths["notes_dir"]).exists():
            results.extend(search_note_files(paths["notes_dir"], args.query, exact=args.exact))
            results.extend(search_claims(collect_claims(paths["notes_dir"]), args.query, exact=args.exact))
    else:
        if args.notes:
            results.extend(search_note_files(paths["notes_dir"], args.query, exact=args.exact))
        if args.claims:
            results.extend(search_claims(collect_claims(paths["notes_dir"]), args.query, exact=args.exact))
    if args.markdown:
        print(results_markdown(results, args.query), end="")
        return 0
    for result in results:
        path = f"\t{result['path']}" if result.get("path") else ""
        print(f"{result['kind']}\t{result['id']}\t{result['title']}{path}")
    if not results:
        print("No matches.")
    return 0


def _report_inputs(args: argparse.Namespace):
    paths = _paths_from_args(args)
    papers = _load_registry(paths["registry"])
    notes = collect_notes(paths["notes_dir"]) if Path(paths["notes_dir"]).exists() else []
    claims = []
    for note in notes:
        claims.extend(note.claims)
    entries = parse_bibtex_file(paths["bibtex"]) if Path(paths["bibtex"]).exists() else []
    themes = load_themes(paths["themes"]) if Path(paths["themes"]).exists() else []
    return papers, notes, claims, entries, themes, paths


def cmd_report(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry", "bibtex", "notes_dir", "themes", "reports_dir"))
    papers, notes, claims, entries, themes, paths = _report_inputs(args)
    reports_dir = _path(paths["reports_dir"])
    bib_findings = validate_bibtex(entries, papers) if entries else []
    audit_findings = citation_audit(papers, notes, claims, entries, themes, root=paths["root"])
    health_findings = workspace_health(
        root=paths["root"],
        registry_path=paths["registry"],
        bibtex_path=paths["bibtex"],
        notes_dir=paths["notes_dir"],
        themes_path=paths["themes"],
        reports_dir=paths["reports_dir"],
        profile=paths["profile"],
    )
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
        "missing-evidence": lambda: missing_evidence_report(claims),
        "workspace-health": lambda: workspace_health_report(health_findings),
        "section-outline": lambda: section_outline_report(args.theme or "", papers, claims, themes, notes),
    }
    selected = [name for name in builders if name != "section-outline"] if args.report_type == "all" else [args.report_type]
    for name in selected:
        if name == "section-outline" and not args.theme:
            print("--theme is required for section-outline", file=sys.stderr)
            return 2
        if name == "section-outline" and not _theme_exists(args.theme, themes):
            print(f"Unknown theme: {args.theme}", file=sys.stderr)
            return 2
        content = builders[name]()
        if args.out and len(selected) == 1:
            path = write_text(args.out, content, force=args.force)
        else:
            path = write_report(name.replace("-", "_"), content, reports_dir, force=args.force)
        print(f"Wrote {path}")
    return 0


def cmd_checklist(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry", "bibtex", "notes_dir", "themes"))
    papers, notes, claims, entries, themes, paths = _report_inputs(args)
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


def cmd_project_init(args: argparse.Namespace) -> int:
    profile = create_project_profile(args.name, description=args.description, force=args.force)
    print(f"Created project {profile.name}")
    print(profile_summary(profile))
    return 0


def cmd_project_list(args: argparse.Namespace) -> int:
    profiles = list_project_profiles()
    if not profiles:
        print("No projects found.")
        return 0
    for profile in profiles:
        print(profile_summary(profile))
    return 0


def cmd_project_validate(args: argparse.Namespace) -> int:
    profile = resolve_project_profile(args.name)
    findings = workspace_health(
        root=profile.root,
        registry_path=profile.registry_path,
        bibtex_path=profile.bibtex_path,
        notes_dir=profile.notes_dir,
        themes_path=profile.themes_path,
        reports_dir=profile.reports_dir,
        profile=profile,
    )
    _print_findings(findings)
    return 1 if args.strict and any(finding.severity == "error" for finding in findings) else 0


def cmd_doctor(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry", "bibtex", "notes_dir", "themes", "reports_dir"))
    paths = _paths_from_args(args)
    findings = workspace_health(
        root=paths["root"],
        registry_path=paths["registry"],
        bibtex_path=paths["bibtex"],
        notes_dir=paths["notes_dir"],
        themes_path=paths["themes"],
        reports_dir=paths["reports_dir"],
        profile=paths["profile"],
    )
    _print_findings(findings)
    if args.out:
        path = write_text(args.out, workspace_health_report(findings), force=args.force)
        print(f"Wrote {path}")
    return 1 if args.strict and any(finding.severity == "error" for finding in findings) else 0


def cmd_export(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry", "bibtex", "notes_dir", "themes", "reports_dir"))
    papers, notes, claims, entries, themes, paths = _report_inputs(args)
    if not args.out:
        print("--out is required for export", file=sys.stderr)
        return 2
    if args.export_type == "registry-csv":
        path = export_registry_csv(papers, args.out, force=args.force)
    elif args.export_type == "registry-json":
        path = export_registry_json(papers, args.out, force=args.force)
    elif args.export_type == "claims":
        path = export_claims_csv(claims, args.out, force=args.force)
    elif args.export_type == "claims-json":
        path = export_claims_json(claims, args.out, force=args.force)
    elif args.export_type == "reading-list":
        path = export_reading_list(papers, args.out, tag=args.tag or "", status=args.status or "", force=args.force)
    elif args.export_type == "unread":
        path = export_reading_list(papers, args.out, status="unread", force=args.force)
    elif args.export_type == "theme-claims":
        if not args.theme:
            print("--theme is required for theme-claims", file=sys.stderr)
            return 2
        path = export_theme_claims(claims, args.out, theme=args.theme, force=args.force)
    else:
        print(f"Unknown export type: {args.export_type}", file=sys.stderr)
        return 2
    print(f"Wrote {path}")
    return 0


def cmd_synthetic_generate(args: argparse.Namespace) -> int:
    summary = generate_synthetic_project(
        name=args.project,
        root=args.root,
        papers=args.papers,
        claims=args.claims,
        themes=args.themes,
        domain=args.domain,
        force=args.force,
    )
    print(f"Generated synthetic project {summary.project}")
    print(f"  root: {summary.root}")
    print(f"  papers: {summary.papers}")
    print(f"  notes: {summary.notes}")
    print(f"  claims: {summary.claims}")
    print(f"  themes: {summary.themes}")
    print(f"  bibtex entries: {summary.bibtex_entries}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="paperwb", description="Local-first academic paper registry, notes, claims, BibTeX, and audit workbench.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create the local workbench folder structure.")
    init_parser.add_argument("--root", default=".", help="Workspace root to initialize.")
    init_parser.set_defaults(func=cmd_init)

    project_parser = subparsers.add_parser("project", help="Manage project profiles.")
    project_sub = project_parser.add_subparsers(dest="project_command", required=True)
    project_init = project_sub.add_parser("init", help="Create a project profile under projects/.")
    project_init.add_argument("name", help="Project profile name.")
    project_init.add_argument("--description", default="", help="Optional project description.")
    project_init.add_argument("--force", action="store_true", help="Allow reusing an existing project folder.")
    project_init.set_defaults(func=cmd_project_init)
    project_list = project_sub.add_parser("list", help="List project profiles.")
    project_list.set_defaults(func=cmd_project_list)
    project_validate = project_sub.add_parser("validate", help="Run workspace health checks for a project.")
    project_validate.add_argument("name", help="Project profile name.")
    project_validate.add_argument("--strict", action="store_true", help="Return non-zero when errors are found.")
    project_validate.set_defaults(func=cmd_project_validate)

    validate_registry_parser = subparsers.add_parser("validate-registry", help="Validate a CSV paper registry.")
    validate_registry_parser.add_argument("registry", help="Registry CSV path.")
    validate_registry_parser.add_argument("--json", help="Optional JSON export path.")
    validate_registry_parser.add_argument("--strict", action="store_true", help="Return non-zero when errors are found.")
    validate_registry_parser.set_defaults(func=cmd_validate_registry)

    validate_bib_parser = subparsers.add_parser("validate-bib", help="Validate a BibTeX library.")
    validate_bib_parser.add_argument("bibtex", help="BibTeX file path.")
    validate_bib_parser.add_argument("--registry", default="", help="Optional registry CSV path for link checks.")
    validate_bib_parser.add_argument("--report", help="Optional Markdown report path.")
    validate_bib_parser.add_argument("--force", action="store_true", help="Overwrite an existing report path.")
    validate_bib_parser.add_argument("--strict", action="store_true", help="Return non-zero when errors are found.")
    validate_bib_parser.set_defaults(func=cmd_validate_bib)

    add_parser = subparsers.add_parser("add-paper", help="Add a paper row to the registry.")
    add_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
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
    add_parser.add_argument("--source-type", default="", help="Source type such as journal_article, book, thesis, or other.")
    add_parser.add_argument("--relevance-score", default="", help="Optional numeric relevance score from 0 to 5.")
    add_parser.add_argument("--reading-priority", default="", help="Reading priority: low, medium, high, or critical.")
    add_parser.add_argument("--included", default="", help="Whether this paper is included in the literature review.")
    add_parser.add_argument("--exclude-reason", default="", help="Reason this paper is excluded, when applicable.")
    add_parser.add_argument("--comment", default="", help="User comment.")
    add_parser.set_defaults(func=cmd_add_paper)

    list_parser = subparsers.add_parser("list", help="List registry papers with optional filters.")
    list_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
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
    note_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
    note_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    note_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
    note_parser.add_argument("--output", help="Optional output path.")
    note_parser.add_argument("--force", action="store_true", help="Overwrite an existing note file.")
    note_parser.set_defaults(func=cmd_note_template)

    claims_parser = subparsers.add_parser("claims", help="Extract claims from structured notes.")
    claims_parser.add_argument("notes_path", nargs="?", help="Notes directory or Markdown note file. Defaults to project/default notes.")
    claims_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
    claims_parser.add_argument("--output", help="Optional output CSV path.")
    claims_parser.set_defaults(func=cmd_claims)

    search_parser = subparsers.add_parser("search", help="Search registry, notes, or claims with simple substring matching.")
    search_parser.add_argument("query", help="Search query.")
    search_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
    search_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    search_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
    search_parser.add_argument("--claims", action="store_true", help="Search extracted claims only.")
    search_parser.add_argument("--notes", action="store_true", help="Search note bodies only.")
    search_parser.add_argument("--exact", action="store_true", help="Require the exact phrase instead of matching all query terms.")
    search_parser.add_argument("--markdown", action="store_true", help="Print Markdown table output.")
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
            "missing-evidence",
            "workspace-health",
            "section-outline",
            "all",
        ],
    )
    report_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
    report_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    report_parser.add_argument("--bibtex", default=str(default_bibtex_path()), help="BibTeX file path.")
    report_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
    report_parser.add_argument("--themes", default=str(default_themes_path()), help="Themes JSON path.")
    report_parser.add_argument("--reports-dir", default=str(default_reports_dir()), help="Reports output directory.")
    report_parser.add_argument("--theme", default="", help="Theme name or ID for theme-specific reports.")
    report_parser.add_argument("--out", help="Write a single report to this exact output path.")
    report_parser.add_argument("--force", action="store_true", help="Overwrite an existing report file.")
    report_parser.set_defaults(func=cmd_report)

    checklist_parser = subparsers.add_parser("checklist", help="Generate a theme review checklist.")
    checklist_parser.add_argument("--theme", required=True, help="Theme name or ID.")
    checklist_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
    checklist_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    checklist_parser.add_argument("--bibtex", default=str(default_bibtex_path()), help="BibTeX file path.")
    checklist_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
    checklist_parser.add_argument("--themes", default=str(default_themes_path()), help="Themes JSON path.")
    checklist_parser.set_defaults(func=cmd_checklist)

    doctor_parser = subparsers.add_parser("doctor", help="Run workspace health diagnostics.")
    doctor_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
    doctor_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    doctor_parser.add_argument("--bibtex", default=str(default_bibtex_path()), help="BibTeX file path.")
    doctor_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
    doctor_parser.add_argument("--themes", default=str(default_themes_path()), help="Themes JSON path.")
    doctor_parser.add_argument("--reports-dir", default=str(default_reports_dir()), help="Reports output directory.")
    doctor_parser.add_argument("--out", help="Optional Markdown workspace-health report path.")
    doctor_parser.add_argument("--force", action="store_true", help="Overwrite an existing workspace-health report path.")
    doctor_parser.add_argument("--strict", action="store_true", help="Return non-zero when errors are found.")
    doctor_parser.set_defaults(func=cmd_doctor)

    export_parser = subparsers.add_parser("export", help="Export local data to CSV, JSON, or Markdown.")
    export_parser.add_argument(
        "export_type",
        choices=["registry-csv", "registry-json", "claims", "claims-json", "reading-list", "unread", "theme-claims"],
    )
    export_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
    export_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    export_parser.add_argument("--bibtex", default=str(default_bibtex_path()), help="BibTeX file path.")
    export_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
    export_parser.add_argument("--themes", default=str(default_themes_path()), help="Themes JSON path.")
    export_parser.add_argument("--reports-dir", default=str(default_reports_dir()), help="Reports output directory.")
    export_parser.add_argument("--out", required=True, help="Output path.")
    export_parser.add_argument("--tag", default="", help="Optional tag filter for reading-list.")
    export_parser.add_argument("--status", default="", help="Optional reading-status filter for reading-list.")
    export_parser.add_argument("--theme", default="", help="Theme for theme-claims export.")
    export_parser.add_argument("--force", action="store_true", help="Overwrite an existing export file.")
    export_parser.set_defaults(func=cmd_export)

    synthetic_parser = subparsers.add_parser("synthetic", help="Generate deterministic synthetic stress corpora.")
    synthetic_sub = synthetic_parser.add_subparsers(dest="synthetic_command", required=True)
    synthetic_generate = synthetic_sub.add_parser("generate", help="Create a synthetic project profile for stress testing.")
    synthetic_generate.add_argument("--project", required=True, help="Synthetic project profile name to create.")
    synthetic_generate.add_argument("--root", default=".", help="Workspace root.")
    synthetic_generate.add_argument("--papers", type=int, default=40, help="Number of synthetic papers.")
    synthetic_generate.add_argument("--claims", type=int, default=80, help="Number of synthetic claims across generated notes.")
    synthetic_generate.add_argument("--themes", type=int, default=5, help="Number of synthetic themes.")
    synthetic_generate.add_argument("--domain", default="zis", choices=["zis", "finance", "ml"], help="Synthetic domain vocabulary.")
    synthetic_generate.add_argument("--force", action="store_true", help="Overwrite an existing synthetic project profile.")
    synthetic_generate.set_defaults(func=cmd_synthetic_generate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, FileExistsError, IsADirectoryError, NotADirectoryError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
