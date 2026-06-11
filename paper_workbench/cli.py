"""Command-line interface for paper-intelligence-workbench."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import tempfile

from .auditlog import append_audit_event, audit_log_markdown, clear_audit_log, default_audit_log_path, load_audit_events
from .authoring import (
    build_claim_bank,
    build_citation_bank,
    build_evidence_matrix,
    build_paragraph_plan,
    build_subsection_readiness,
    citation_bank_report,
    claim_bank_report,
    evidence_matrix_report as authoring_evidence_matrix_report,
    paragraph_plan_report,
    subsection_readiness_report,
    write_evidence_matrix_csv,
    write_evidence_matrix_json,
    writing_packet_report,
)
from .audit import citation_audit
from .backups import (
    backup_manifest_report,
    create_backup,
    find_backup,
    list_backups,
    load_backup_manifest,
    plan_restore,
    restore_backup,
    restore_plan_report,
)
from .bibtex import parse_bibtex_file, validate_bibtex
from .claims import collect_claims, collect_notes, save_claims_csv
from .doctor import workspace_health
from .exports import (
    export_bundle,
    export_claims_csv,
    export_claims_json,
    export_obsidian_vault,
    export_project_summary,
    export_reading_list,
    export_registry_csv,
    export_registry_json,
    export_report_index,
    export_theme_claims,
)
from .files import (
    DEFAULT_WORKSPACE_SCAN_DIRS,
    SCAN_DIRS,
    default_file_registry_path,
    duplicate_files_report,
    link_file_to_paper,
    load_file_registry,
    local_files_audit_report,
    merge_file_registry_records,
    missing_files_report,
    save_file_registry,
    scan_local_files,
    sha256_file,
    text_sidecars_report,
    unlink_file_from_paper,
)
from .importers import import_bibtex, import_generic_csv, import_report, import_ris, import_zotero_csv
from .index import (
    build_index_records,
    clear_index,
    default_index_path,
    display_path,
    index_status,
    index_status_markdown,
    rebuild_index,
    search_index,
    search_results_markdown as indexed_results_markdown,
    source_counts,
)
from .errors import format_error_message
from .init import init_workspace
from .integrity import check_workspace_integrity, workspace_integrity_report
from .io import write_text
from .migration import migration_plan_report, plan_legacy_migration, run_legacy_migration
from .notes import write_note_template
from .paths import default_bibtex_path, default_notes_dir, default_registry_path, default_reports_dir, default_themes_path
from .projects import create_project_profile, list_project_profiles, profile_summary, resolve_project_profile
from .registry import add_paper, create_empty_registry, display_authors, filter_papers, load_registry, save_registry, save_registry_json, validate_registry, validate_registry_headers
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
            raise FileNotFoundError(
                format_error_message(
                    what="Registry not found.",
                    where=str(target),
                    why="This command needs a registry CSV before it can load papers or generate reports.",
                    next_step="Run `paperwb init`, pass --registry with an existing CSV, or use --project for a configured project.",
                )
            )
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
        "registry": Path(getattr(args, "registry", "") or default_registry_path()),
        "bibtex": Path(getattr(args, "bibtex", "") or default_bibtex_path()),
        "notes_dir": Path(getattr(args, "notes_dir", "") or default_notes_dir()),
        "themes": Path(getattr(args, "themes", "") or default_themes_path()),
        "reports_dir": Path(getattr(args, "reports_dir", "") or default_reports_dir()),
    }


def _project_id_from_paths(paths: dict[str, Path | None]) -> str:
    profile = paths.get("profile")
    return profile.name if profile else "default"


def _preflight_output_paths(paths: list[str | Path], *, force: bool) -> None:
    """Fail before writing when any requested output would be unsafe."""
    seen: dict[Path, Path] = {}
    for raw_path in paths:
        path = Path(raw_path)
        resolved = path.resolve(strict=False)
        if resolved in seen:
            raise FileExistsError(f"multiple outputs target the same path: {path}")
        seen[resolved] = path
        if path.exists() and not force:
            raise FileExistsError(f"{path} already exists")


def _record_audit_event(
    paths: dict[str, Path | None],
    *,
    command: str,
    action: str,
    affected_paths: list[str | Path],
    dry_run: bool = False,
    success: bool = True,
    warnings: list[str] | tuple[str, ...] = (),
    summary: str = "",
) -> None:
    append_audit_event(
        root=paths["root"] or ".",
        command=command,
        action=action,
        project=_project_id_from_paths(paths),
        affected_paths=affected_paths,
        dry_run=dry_run,
        success=success,
        warnings=warnings,
        summary=summary,
    )


def _default_text_dir(paths: dict[str, Path | None]) -> Path:
    if paths.get("profile"):
        return Path(paths["root"]) / "text"
    return Path(paths["root"]) / "data" / "text"


def _index_path_from_args(args: argparse.Namespace, paths: dict[str, Path | None]) -> Path:
    return Path(args.index) if getattr(args, "index", "") else default_index_path(paths["root"])


def _text_dir_from_args(args: argparse.Namespace, paths: dict[str, Path | None]) -> Path:
    return Path(args.text_dir) if getattr(args, "text_dir", "") else _default_text_dir(paths)


def _file_registry_path_from_args(args: argparse.Namespace, paths: dict[str, Path | None]) -> Path:
    if getattr(args, "file_registry", ""):
        return Path(args.file_registry)
    return default_file_registry_path(paths["root"], project=bool(paths.get("profile")))


def _index_records_from_args(args: argparse.Namespace, paths: dict[str, Path | None]):
    return build_index_records(
        project_id=_project_id_from_paths(paths),
        registry_path=paths["registry"],
        bibtex_path=paths["bibtex"],
        notes_dir=paths["notes_dir"],
        themes_path=paths["themes"],
        text_dir=_text_dir_from_args(args, paths),
        include_text=getattr(args, "include_text", False),
    )


def _index_rebuild_hint(args: argparse.Namespace) -> str:
    parts = ["paperwb", "index", "rebuild"]
    project = getattr(args, "project", "")
    if project:
        parts.extend(["--project", project])
    if getattr(args, "text", False):
        parts.append("--include-text")
    return " ".join(parts)


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
    findings = validate_registry_headers(args.registry) + validate_registry(papers, root=_registry_validation_root(args.registry))
    _print_findings(findings)
    if args.json:
        save_registry_json(papers, args.json, force=args.force)
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
    _record_audit_event(
        paths,
        command="add-paper",
        action="registry_add_paper",
        affected_paths=[registry_path],
        summary=f"Added paper {paper.paper_id}",
    )
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
    _record_audit_event(paths, command="note-template", action="write_note_template", affected_paths=[path], summary=f"Wrote note template for {paper.paper_id}")
    print(f"Wrote note template to {path}")
    return 0


def cmd_claims(args: argparse.Namespace) -> int:
    if getattr(args, "project", "") and args.notes_path:
        raise ValueError("--project cannot be combined with notes_path; project profile notes are used instead.")
    paths = _paths_from_args(args)
    notes_path = Path(args.notes_path) if args.notes_path else paths["notes_dir"]
    if not notes_path.exists():
        raise FileNotFoundError(
            format_error_message(
                what="Notes path not found.",
                where=str(notes_path),
                why="Claim extraction needs an existing Markdown note file or notes directory.",
                next_step="Check the path, run `paperwb init`, or use `--project NAME` for a configured project.",
            )
        )
    claims = collect_claims(notes_path)
    if args.output:
        save_claims_csv(claims, args.output, force=args.force, root=paths["root"])
        _record_audit_event(paths, command="claims", action="export_claims_csv", affected_paths=[args.output], summary=f"Exported {len(claims)} claims")
        print(f"Wrote {len(claims)} claims to {args.output}")
    else:
        for claim in claims:
            print(f"{claim.claim_id}\t{claim.paper_id}\t{claim.strength}\t{claim.claim_text}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry", "notes_dir"))
    paths = _paths_from_args(args)
    if args.indexed:
        source_types: set[str] = set()
        if args.claims:
            source_types.add("claim")
        if args.notes:
            source_types.add("note")
        if args.text:
            source_types.add("text")
        try:
            results = search_index(
                _index_path_from_args(args, paths),
                args.query,
                project_id=_project_id_from_paths(paths),
                source_types=source_types or None,
                exact=args.exact,
                limit=args.limit,
            )
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                format_error_message(
                    what="Search index not found.",
                    where=str(_index_path_from_args(args, paths)),
                    why="Indexed search reads a local SQLite cache that has not been built yet.",
                    next_step=f"Run `{_index_rebuild_hint(args)}` before using indexed search.",
                )
            ) from exc
        markdown = indexed_results_markdown(results, args.query, base_path=paths["root"])
        if args.out:
            path = write_text(args.out, markdown, force=args.force)
            print(f"Wrote {path}")
            return 0
        if args.markdown:
            print(markdown, end="")
            return 0
        for result in results:
            path = f"\t{display_path(result.path, base_path=paths['root'])}" if result.path else ""
            print(f"{result.source_type}\t{result.paper_id}\t{result.score}\t{result.title}{path}")
        if not results:
            print("No matches.")
        return 0
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
        markdown = results_markdown(results, args.query)
        if args.out:
            path = write_text(args.out, markdown, force=args.force)
            print(f"Wrote {path}")
        else:
            print(markdown, end="")
        return 0
    if args.out:
        path = write_text(args.out, results_markdown(results, args.query), force=args.force)
        print(f"Wrote {path}")
        return 0
    for result in results:
        path = f"\t{result['path']}" if result.get("path") else ""
        print(f"{result['kind']}\t{result['id']}\t{result['title']}{path}")
    if not results:
        print("No matches.")
    return 0


def cmd_index_rebuild(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry", "bibtex", "notes_dir", "themes"))
    paths = _paths_from_args(args)
    records = _index_records_from_args(args, paths)
    status = rebuild_index(_index_path_from_args(args, paths), records, project_id=_project_id_from_paths(paths))
    counts = source_counts(records)
    print(f"Rebuilt index at {display_path(status.index_path, base_path=paths['root'])}")
    print(f"Project: {status.project_id}")
    print(f"Records: {len(records)}")
    print(f"FTS5 enabled: {str(status.fts_enabled).lower()}")
    for source_type, count in sorted(counts.items()):
        print(f"  {source_type}: {count}")
    if args.out:
        path = write_text(args.out, index_status_markdown(status, base_path=paths["root"]), force=args.force)
        _record_audit_event(paths, command="index rebuild", action="write_index_status_report", affected_paths=[args.out], summary="Wrote index status report")
        print(f"Wrote {path}")
    _record_audit_event(paths, command="index rebuild", action="rebuild_index", affected_paths=[_index_path_from_args(args, paths)], summary=f"Rebuilt {len(records)} index records")
    return 0


def cmd_index_status(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry", "bibtex", "notes_dir", "themes"))
    paths = _paths_from_args(args)
    current_records = _index_records_from_args(args, paths) if args.check_files else None
    status = index_status(_index_path_from_args(args, paths), project_id=_project_id_from_paths(paths), current_records=current_records)
    markdown = index_status_markdown(status, base_path=paths["root"])
    if args.out:
        path = write_text(args.out, markdown, force=args.force)
        print(f"Wrote {path}")
    else:
        print(markdown, end="")
    return 1 if args.strict and status.warnings else 0


def cmd_index_clear(args: argparse.Namespace) -> int:
    paths = _paths_from_args(args)
    index_path = _index_path_from_args(args, paths)
    project_id = _project_id_from_paths(paths)
    clear_index(index_path, project_id=project_id)
    _record_audit_event(paths, command="index clear", action="clear_index", affected_paths=[index_path], summary=f"Cleared index records for {project_id}")
    print(f"Cleared index records for {project_id} at {index_path}")
    return 0


def _file_scan_from_args(args: argparse.Namespace):
    _reject_project_path_overrides(args, ("registry",))
    paths = _paths_from_args(args)
    default_scan_dirs = SCAN_DIRS if paths.get("profile") else DEFAULT_WORKSPACE_SCAN_DIRS
    scan_dirs = tuple(args.scan_dir) if getattr(args, "scan_dir", None) else default_scan_dirs
    result = scan_local_files(
        root=paths["root"],
        registry_path=paths["registry"],
        file_registry_path=_file_registry_path_from_args(args, paths),
        scan_dirs=scan_dirs,
        large_file_bytes=args.large_file_bytes,
    )
    return result, paths


def cmd_files_scan(args: argparse.Namespace) -> int:
    result, _paths = _file_scan_from_args(args)
    if args.write_registry:
        existing_records = load_file_registry(result.file_registry_path)
        merged_records = merge_file_registry_records(result.records, existing_records)
        path = save_file_registry(merged_records, result.file_registry_path, force=args.force)
        preserved = len(merged_records) - len(result.records)
        _record_audit_event(_paths, command="files scan", action="write_file_registry", affected_paths=[result.file_registry_path], warnings=result.warnings, summary=f"Wrote {len(merged_records)} file registry records")
        print(f"Wrote file registry to {path}")
        if preserved:
            print(f"Preserved {preserved} existing file registry record(s) not present in the current scan.")
    for record in result.records:
        print(f"{record.paper_id or '[unlinked]'}\t{record.file_type}\t{record.size_bytes}\t{record.linked_registry_status}\t{record.relative_path}")
    if not result.records:
        print("No supported local files found.")
    for warning in result.warnings:
        print(f"Warning: {warning}")
    return 0


def cmd_files_status(args: argparse.Namespace) -> int:
    result, _paths = _file_scan_from_args(args)
    registry_records = load_file_registry(result.file_registry_path)
    print(f"Root: {result.root}")
    print(f"File registry: {result.file_registry_path}")
    print(f"File registry records: {len(registry_records)}")
    print(f"Files found: {len(result.records)}")
    print(f"Unlinked files: {len(result.unlinked_files)}")
    print(f"Missing registry file references: {len(result.missing_registry_files)}")
    print(f"Duplicate registry file paths: {len(result.duplicate_registry_paths)}")
    print(f"Duplicate file hashes: {len(result.duplicate_hashes)}")
    print(f"File registry missing files: {len(result.file_registry_missing_files)}")
    print(f"File registry records outside scan folders: {len(result.file_registry_unscanned_records)}")
    print(f"File registry hash mismatches: {len(result.file_registry_hash_mismatches)}")
    print(f"Text sidecars: {len(result.sidecars)}")
    print(f"Warnings: {len(result.warnings)}")
    for warning in result.warnings:
        print(f"Warning: {warning}")
    return 0


def cmd_files_audit(args: argparse.Namespace) -> int:
    result, paths = _file_scan_from_args(args)
    reports_dir = Path(args.reports_dir) if args.reports_dir else Path(paths["reports_dir"])
    outputs = {
        "local_files_audit_v0_7.md": local_files_audit_report(result),
        "duplicate_files_v0_7.md": duplicate_files_report(result),
        "missing_files_v0_7.md": missing_files_report(result),
        "text_sidecars_v0_7.md": text_sidecars_report(result),
    }
    _preflight_output_paths([reports_dir / filename for filename in outputs], force=args.force)
    written: list[Path] = []
    for filename, content in outputs.items():
        path = write_text(reports_dir / filename, content, force=args.force)
        written.append(path)
    for path in written:
        print(f"Wrote {path}")
    _record_audit_event(paths, command="files audit", action="write_file_audit_reports", affected_paths=written, warnings=result.warnings, summary=f"Wrote {len(written)} local-file audit reports")
    return 0


def cmd_files_link(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry",))
    paths = _paths_from_args(args)
    record = link_file_to_paper(
        paper_id=args.paper_id,
        file_path=args.path,
        root=paths["root"],
        registry_path=paths["registry"],
        file_registry_path=_file_registry_path_from_args(args, paths),
        force=args.force,
        notes=args.notes,
    )
    _record_audit_event(paths, command="files link", action="link_local_file", affected_paths=[record.relative_path, _file_registry_path_from_args(args, paths), paths["registry"]], summary=f"Linked {record.paper_id} to {record.relative_path}")
    print(f"Linked {record.paper_id} to {record.relative_path} ({record.file_type}, sha256={record.sha256[:12]})")
    return 0


def cmd_files_unlink(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry",))
    paths = _paths_from_args(args)
    removed = unlink_file_from_paper(
        paper_id=args.paper_id,
        root=paths["root"],
        registry_path=paths["registry"],
        file_registry_path=_file_registry_path_from_args(args, paths),
        clear_pdf=not args.keep_pdf_path,
    )
    _record_audit_event(paths, command="files unlink", action="unlink_local_file", affected_paths=[_file_registry_path_from_args(args, paths), paths["registry"]], summary=f"Unlinked {removed} file registry records for {args.paper_id}")
    print(f"Unlinked {removed} file registry record(s) for {args.paper_id}")
    return 0


def cmd_files_hash(args: argparse.Namespace) -> int:
    path = Path(args.path)
    digest = sha256_file(path)
    print(f"{digest}\t{path.stat().st_size}\t{path}")
    return 0


def cmd_files_sidecars(args: argparse.Namespace) -> int:
    result, _paths = _file_scan_from_args(args)
    if args.out:
        path = write_text(args.out, text_sidecars_report(result), force=args.force)
        print(f"Wrote {path}")
        return 0
    for record in result.sidecars:
        print(f"{record.paper_id or '[unmatched]'}\t{record.linked_registry_status}\t{record.size_bytes}\t{record.relative_path}")
    if not result.sidecars:
        print("No text sidecars found.")
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
        "inventory": lambda: inventory_report(papers, root=paths["root"], claims=claims),
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
        "evidence-matrix": lambda: authoring_evidence_matrix_report(
            build_evidence_matrix(args.theme or "", papers, claims, themes, notes, project=_project_id_from_paths(paths))
        ),
        "claim-bank": lambda: claim_bank_report(build_claim_bank(args.theme or "", claims, themes, project=_project_id_from_paths(paths))),
        "citation-bank": lambda: citation_bank_report(
            build_citation_bank(args.theme or "", papers, claims, themes, notes, entries, project=_project_id_from_paths(paths)),
            claims,
        ),
        "paragraph-plan": lambda: paragraph_plan_report(build_paragraph_plan(args.theme or "", papers, claims, themes, notes, project=_project_id_from_paths(paths))),
        "subsection-readiness": lambda: subsection_readiness_report(
            build_subsection_readiness(args.theme or "", papers, notes, claims, entries, themes, project=_project_id_from_paths(paths))
        ),
    }
    theme_report_types = {"section-outline", "evidence-matrix", "claim-bank", "citation-bank", "paragraph-plan", "subsection-readiness"}
    selected = [name for name in builders if name not in theme_report_types] if args.report_type == "all" else [args.report_type]
    for name in selected:
        if name in theme_report_types and not args.theme:
            print(f"--theme is required for {name}", file=sys.stderr)
            return 2
        if name in theme_report_types and not _theme_exists(args.theme, themes):
            print(f"Unknown theme: {args.theme}", file=sys.stderr)
            return 2
        if name != "evidence-matrix" and (getattr(args, "csv_out", "") or getattr(args, "json_out", "")):
            print("--csv-out and --json-out are only supported for evidence-matrix", file=sys.stderr)
            return 2
        if name == "evidence-matrix":
            matrix_output_paths: list[str | Path] = [
                args.out if args.out and len(selected) == 1 else reports_dir / "evidence_matrix.md"
            ]
            if args.csv_out:
                matrix_output_paths.append(args.csv_out)
            if args.json_out:
                matrix_output_paths.append(args.json_out)
            _preflight_output_paths(matrix_output_paths, force=args.force)
        content = builders[name]()
        if args.out and len(selected) == 1:
            path = write_text(args.out, content, force=args.force)
        else:
            path = write_report(name.replace("-", "_"), content, reports_dir, force=args.force)
        print(f"Wrote {path}")
        _record_audit_event(paths, command="report", action=f"write_report:{name}", affected_paths=[path], summary=f"Wrote {name} report")
        if name == "evidence-matrix":
            matrix = build_evidence_matrix(args.theme or "", papers, claims, themes, notes, project=_project_id_from_paths(paths))
            if args.csv_out:
                csv_path = write_evidence_matrix_csv(matrix, args.csv_out, force=args.force)
                print(f"Wrote {csv_path}")
                _record_audit_event(paths, command="report", action="write_evidence_matrix_csv", affected_paths=[csv_path], summary="Wrote evidence matrix CSV")
            if args.json_out:
                json_path = write_evidence_matrix_json(matrix, args.json_out, force=args.force)
                print(f"Wrote {json_path}")
                _record_audit_event(paths, command="report", action="write_evidence_matrix_json", affected_paths=[json_path], summary="Wrote evidence matrix JSON")
    return 0


def cmd_writing_packet(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry", "bibtex", "notes_dir", "themes"))
    papers, notes, claims, entries, themes, paths = _report_inputs(args)
    if not _theme_exists(args.theme, themes):
        print(f"Unknown theme: {args.theme}", file=sys.stderr)
        return 2
    content = writing_packet_report(args.theme, papers, notes, claims, entries, themes, project=_project_id_from_paths(paths))
    output = args.out or (Path(paths["reports_dir"]) / f"{normalize_tag(args.theme)}_writing_packet.md")
    path = write_text(output, content, force=args.force)
    _record_audit_event(paths, command="writing-packet", action="write_writing_packet", affected_paths=[path], summary=f"Wrote writing packet for {args.theme}")
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
    _record_audit_event(
        {"root": Path(profile.root), "profile": profile},
        command="project init",
        action="create_project_profile",
        affected_paths=[profile.root, profile.registry_path, profile.bibtex_path, profile.themes_path],
        summary=f"Created project {profile.name}",
    )
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
        _record_audit_event(paths, command="doctor", action="write_workspace_health_report", affected_paths=[path], summary="Wrote workspace health report")
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
        path = export_claims_csv(claims, args.out, force=args.force, root=paths["root"])
    elif args.export_type == "claims-json":
        path = export_claims_json(claims, args.out, force=args.force)
    elif args.export_type == "reading-list":
        if args.included and args.excluded:
            raise ValueError("--included and --excluded cannot be combined")
        path = export_reading_list(
            papers,
            args.out,
            tag=args.tag or "",
            status=args.status or "",
            theme=args.theme or "",
            themes=themes,
            included=True if args.included else None,
            excluded=args.excluded,
            high_priority=args.high_priority,
            missing_notes=args.missing_notes,
            notes=notes,
            output_format=args.format,
            force=args.force,
        )
    elif args.export_type == "unread":
        path = export_reading_list(papers, args.out, status="unread", output_format=args.format, force=args.force)
    elif args.export_type == "theme-claims":
        if not args.theme:
            print("--theme is required for theme-claims", file=sys.stderr)
            return 2
        path = export_theme_claims(claims, args.out, theme=args.theme, force=args.force)
    elif args.export_type == "obsidian":
        path = export_obsidian_vault(papers, notes, claims, themes, args.out, force=args.force)
    elif args.export_type == "bundle":
        path = export_bundle(
            registry_path=paths["registry"],
            bibtex_path=paths["bibtex"],
            notes_dir=paths["notes_dir"],
            themes_path=paths["themes"],
            reports_dir=paths["reports_dir"],
            text_dir=_default_text_dir(paths),
            out=args.out,
            project=paths["profile"].name if paths["profile"] else "",
            include_pdfs=args.include_pdfs,
            papers=papers,
            root=paths["root"],
            force=args.force,
        )
    elif args.export_type == "project-summary":
        path = export_project_summary(papers, claims, themes, args.out, force=args.force)
    elif args.export_type == "report-index":
        path = export_report_index(paths["reports_dir"], args.out, force=args.force)
    else:
        print(f"Unknown export type: {args.export_type}", file=sys.stderr)
        return 2
    _record_audit_event(paths, command="export", action=f"export:{args.export_type}", affected_paths=[path], summary=f"Exported {args.export_type}")
    print(f"Wrote {path}")
    return 0


def _default_import_report(paths: dict[str, Path | None], import_type: str) -> Path:
    return Path(paths["reports_dir"]) / f"import_{import_type.replace('-', '_')}.md"


def _preflight_file_output(path: Path, *, force: bool) -> Path:
    if path.exists() and path.is_dir():
        raise IsADirectoryError(path)
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _reserve_temp_path(target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent, delete=False) as handle:
        return Path(handle.name)


def _cleanup_temp_paths(paths: list[Path]) -> None:
    for path in paths:
        try:
            if path.exists():
                path.unlink()
        except OSError:
            pass


def _finish_import(args: argparse.Namespace, result, paths: dict[str, Path | None], import_type: str) -> int:
    report_path = _preflight_file_output(Path(args.report) if args.report else _default_import_report(paths, import_type), force=args.force)
    report_tmp = _reserve_temp_path(report_path)
    registry_tmp: Path | None = None
    try:
        write_text(report_tmp, import_report(result), force=True)
        if not result.dry_run:
            registry_path = _preflight_file_output(Path(paths["registry"]), force=True)
            registry_tmp = _reserve_temp_path(registry_path)
            save_registry(result.registry_papers, registry_tmp)
            os.replace(report_tmp, report_path)
            os.replace(registry_tmp, registry_path)
            print(f"Wrote registry to {registry_path}")
        else:
            os.replace(report_tmp, report_path)
    finally:
        _cleanup_temp_paths([path for path in (report_tmp, registry_tmp) if path is not None])
    _record_audit_event(
        paths,
        command=f"import {import_type}",
        action="import_registry_data",
        affected_paths=[paths["registry"], report_path],
        dry_run=result.dry_run,
        warnings=result.warnings,
        summary=f"Rows read: {result.rows_read}; imported: {result.imported}; updated: {result.updated}; skipped: {result.skipped}",
    )
    print(f"Wrote import report to {report_path}")
    print(f"Rows read: {result.rows_read}; imported: {result.imported}; updated: {result.updated}; skipped: {result.skipped}; dry-run: {result.dry_run}")
    return 0


def _import_paths(args: argparse.Namespace) -> dict[str, Path | None]:
    _reject_project_path_overrides(args, ("registry", "reports_dir"))
    paths = _paths_from_args(args)
    paths["registry"] = Path(paths["registry"])
    paths["reports_dir"] = Path(paths["reports_dir"])
    return paths


def _load_import_registry(path: Path, *, dry_run: bool) -> list:
    if not path.exists():
        return []
    return _load_registry(path, create_if_missing=False)


def cmd_import_zotero_csv(args: argparse.Namespace) -> int:
    paths = _import_paths(args)
    papers = _load_import_registry(paths["registry"], dry_run=args.dry_run)
    result = import_zotero_csv(
        args.source,
        papers,
        registry_path=paths["registry"],
        project=args.project or "",
        dry_run=args.dry_run,
        fill_missing=args.fill_missing,
    )
    return _finish_import(args, result, paths, "zotero_csv")


def cmd_import_generic_csv(args: argparse.Namespace) -> int:
    paths = _import_paths(args)
    papers = _load_import_registry(paths["registry"], dry_run=args.dry_run)
    result = import_generic_csv(
        args.source,
        args.mapping,
        papers,
        registry_path=paths["registry"],
        project=args.project or "",
        dry_run=args.dry_run,
        fill_missing=args.fill_missing,
    )
    return _finish_import(args, result, paths, "generic_csv")


def cmd_import_bibtex(args: argparse.Namespace) -> int:
    paths = _import_paths(args)
    papers = _load_import_registry(paths["registry"], dry_run=args.dry_run)
    result = import_bibtex(
        args.source,
        papers,
        registry_path=paths["registry"],
        project=args.project or "",
        dry_run=args.dry_run,
        fill_missing=args.fill_missing,
    )
    return _finish_import(args, result, paths, "bibtex")


def cmd_import_ris(args: argparse.Namespace) -> int:
    paths = _import_paths(args)
    papers = _load_import_registry(paths["registry"], dry_run=args.dry_run)
    result = import_ris(
        args.source,
        papers,
        registry_path=paths["registry"],
        project=args.project or "",
        dry_run=args.dry_run,
        fill_missing=args.fill_missing,
    )
    return _finish_import(args, result, paths, "ris")


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
    append_audit_event(
        root=summary.root,
        command="synthetic generate",
        action="generate_synthetic_project",
        project=summary.project,
        affected_paths=[summary.root],
        summary=f"Generated {summary.papers} synthetic papers and {summary.claims} claims",
    )
    return 0


def cmd_integrity_check(args: argparse.Namespace) -> int:
    _reject_project_path_overrides(args, ("registry", "bibtex", "notes_dir", "themes", "reports_dir"))
    paths = _paths_from_args(args)
    result = check_workspace_integrity(
        root=paths["root"],
        registry_path=paths["registry"],
        bibtex_path=paths["bibtex"],
        notes_dir=paths["notes_dir"],
        themes_path=paths["themes"],
        reports_dir=paths["reports_dir"],
        profile=paths["profile"],
    )
    print(f"Integrity errors: {len(result.errors)}")
    print(f"Integrity warnings: {len(result.warnings)}")
    if args.out:
        path = write_text(args.out, workspace_integrity_report(result), force=args.force)
        _record_audit_event(paths, command="integrity check", action="write_integrity_report", affected_paths=[path], warnings=[finding.message for finding in result.findings], summary="Wrote workspace integrity report")
        print(f"Wrote {path}")
    elif result.findings:
        _print_findings(result.findings)
    return 1 if args.strict and result.errors else 0


def _audit_log_path_from_args(args: argparse.Namespace) -> tuple[Path, dict[str, Path | None]]:
    paths = _paths_from_args(args)
    target = Path(args.path) if getattr(args, "path", "") else default_audit_log_path(paths["root"])
    return target, paths


def cmd_audit_log_show(args: argparse.Namespace) -> int:
    path, _paths = _audit_log_path_from_args(args)
    events = load_audit_events(path)
    if args.limit:
        events = events[-args.limit :]
    if args.out:
        written = write_text(args.out, audit_log_markdown(events), force=args.force)
        print(f"Wrote {written}")
        return 0
    if args.markdown:
        print(audit_log_markdown(events), end="")
        return 0
    if not events:
        print("No audit events found.")
        return 0
    for event in events:
        print(f"{event.get('timestamp', '')}\t{event.get('project', '')}\t{event.get('action', '')}\t{event.get('summary', '')}")
    return 0


def cmd_audit_log_clear(args: argparse.Namespace) -> int:
    path, paths = _audit_log_path_from_args(args)
    removed = clear_audit_log(path, force=args.force)
    if removed:
        print(f"Cleared audit log {path}")
    else:
        print(f"Audit log did not exist: {path}")
    return 0


def _backup_paths(args: argparse.Namespace) -> dict[str, Path | None]:
    _reject_project_path_overrides(args, ("registry", "bibtex", "notes_dir", "themes", "reports_dir"))
    return _paths_from_args(args)


def cmd_backup_create(args: argparse.Namespace) -> int:
    paths = _backup_paths(args)
    manifest, backup_path = create_backup(
        root=paths["root"],
        registry_path=paths["registry"],
        bibtex_path=paths["bibtex"],
        notes_dir=paths["notes_dir"],
        themes_path=paths["themes"],
        reports_dir=paths["reports_dir"],
        profile=paths["profile"],
        backups_dir=args.backups_dir or None,
        include_reports=args.include_reports,
        notes=args.notes,
    )
    _record_audit_event(paths, command="backup create", action="create_backup", affected_paths=[backup_path], summary=f"Created backup {manifest.backup_id}")
    print(f"Created backup {manifest.backup_id}")
    print(f"Path: {backup_path}")
    print(f"Files included: {len(manifest.included_files)}")
    return 0


def cmd_backup_list(args: argparse.Namespace) -> int:
    paths = _backup_paths(args)
    backups = list_backups(paths["root"], project=_project_id_from_paths(paths) if args.project else "", backups_dir=args.backups_dir or None)
    if not backups:
        print("No backups found.")
        return 0
    for manifest in backups:
        print(f"{manifest.backup_id}\t{manifest.project or 'default'}\t{manifest.created_at}\tfiles={len(manifest.included_files)}")
    return 0


def cmd_backup_inspect(args: argparse.Namespace) -> int:
    paths = _backup_paths(args)
    backup_path = find_backup(paths["root"], args.backup_id, backups_dir=args.backups_dir or None)
    manifest = load_backup_manifest(backup_path)
    content = backup_manifest_report(manifest)
    if args.out:
        path = write_text(args.out, content, force=args.force)
        _record_audit_event(paths, command="backup inspect", action="write_backup_manifest_report", affected_paths=[path], summary=f"Inspected backup {args.backup_id}")
        print(f"Wrote {path}")
    else:
        print(content, end="")
    return 0


def cmd_backup_plan_restore(args: argparse.Namespace) -> int:
    paths = _backup_paths(args)
    plan = plan_restore(
        root=paths["root"],
        backup_id=args.backup_id,
        backups_dir=args.backups_dir or None,
        project=_project_id_from_paths(paths) if args.project else "",
        dry_run=True,
    )
    content = restore_plan_report(plan)
    if args.out:
        path = write_text(args.out, content, force=args.force)
        _record_audit_event(paths, command="backup plan-restore", action="write_restore_plan", affected_paths=[path], summary=f"Planned restore for {args.backup_id}")
        print(f"Wrote {path}")
    else:
        print(content, end="")
    return 0


def cmd_backup_restore(args: argparse.Namespace) -> int:
    paths = _backup_paths(args)
    dry_run = args.dry_run or not args.force
    if args.out:
        _preflight_output_paths([args.out], force=args.force_report)
    if dry_run:
        plan = plan_restore(
            root=paths["root"],
            backup_id=args.backup_id,
            backups_dir=args.backups_dir or None,
            project=_project_id_from_paths(paths) if args.project else "",
            dry_run=True,
        )
    else:
        plan = restore_backup(
            root=paths["root"],
            backup_id=args.backup_id,
            registry_path=paths["registry"],
            bibtex_path=paths["bibtex"],
            notes_dir=paths["notes_dir"],
            themes_path=paths["themes"],
            reports_dir=paths["reports_dir"],
            profile=paths["profile"],
            backups_dir=args.backups_dir or None,
            force=True,
            create_pre_restore_backup=not args.no_pre_restore_backup,
        )
    content = restore_plan_report(plan)
    if args.out:
        path = write_text(args.out, content, force=args.force_report)
        print(f"Wrote {path}")
        affected = [path]
    else:
        print(content, end="")
        affected = []
    _record_audit_event(
        paths,
        command="backup restore",
        action="restore_backup" if not dry_run else "restore_backup_dry_run",
        affected_paths=affected + [args.backup_id],
        dry_run=dry_run,
        warnings=plan.missing_backup_files,
        summary=f"Restore {'planned' if dry_run else 'applied'} for {args.backup_id}",
    )
    return 0


def cmd_migrate_plan(args: argparse.Namespace) -> int:
    if args.from_workflow != "legacy":
        raise ValueError("only --from legacy is supported")
    plan = plan_legacy_migration(root=args.root, to_project=args.to_project)
    content = migration_plan_report(plan)
    if args.out:
        path = write_text(args.out, content, force=args.force)
        print(f"Wrote {path}")
    else:
        print(content, end="")
    return 1 if args.strict and plan.conflicts else 0


def cmd_migrate_run(args: argparse.Namespace) -> int:
    if args.from_workflow != "legacy":
        raise ValueError("only --from legacy is supported")
    dry_run = args.dry_run or not args.force
    if args.out:
        _preflight_output_paths([args.out], force=args.force_report)
    plan, backup = run_legacy_migration(root=args.root, to_project=args.to_project, dry_run=dry_run, force=args.force)
    content = migration_plan_report(plan)
    if args.out:
        path = write_text(args.out, content, force=args.force_report)
        print(f"Wrote {path}")
    else:
        print(content, end="")
    append_audit_event(
        root=args.root,
        command="migrate run",
        action="legacy_migration" if not dry_run else "legacy_migration_dry_run",
        project=args.to_project,
        affected_paths=[operation.target_path for operation in plan.operations],
        dry_run=dry_run,
        warnings=plan.warnings + plan.conflicts,
        success=not plan.conflicts,
        summary=f"Migration {'planned' if dry_run else 'copied'} to project {args.to_project}; backup={backup.backup_id if backup else 'none'}",
    )
    return 1 if plan.conflicts and args.strict else 0


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
    validate_registry_parser.add_argument("--force", action="store_true", help="Overwrite an existing JSON export path.")
    validate_registry_parser.add_argument("--strict", action="store_true", help="Return non-zero when errors are found.")
    validate_registry_parser.set_defaults(func=cmd_validate_registry)

    validate_bib_parser = subparsers.add_parser("validate-bib", help="Validate a BibTeX library.")
    validate_bib_parser.add_argument("bibtex", help="BibTeX file path.")
    validate_bib_parser.add_argument("--registry", default="", help="Optional registry CSV path for link checks.")
    validate_bib_parser.add_argument("--report", help="Optional Markdown report path.")
    validate_bib_parser.add_argument("--force", action="store_true", help="Overwrite an existing report path.")
    validate_bib_parser.add_argument("--strict", action="store_true", help="Return non-zero when errors are found.")
    validate_bib_parser.set_defaults(func=cmd_validate_bib)

    import_parser = subparsers.add_parser("import", help="Import local bibliography data into a registry.")
    import_sub = import_parser.add_subparsers(dest="import_type", required=True)

    def add_import_common(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument("source", help="Input file to import.")
        command_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
        command_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
        command_parser.add_argument("--reports-dir", default=str(default_reports_dir()), help="Reports output directory.")
        command_parser.add_argument("--report", default="", help="Optional exact Markdown import report path.")
        command_parser.add_argument("--dry-run", action="store_true", help="Report what would be imported without writing the registry.")
        command_parser.add_argument("--fill-missing", action="store_true", help="Fill only blank fields on matched registry rows.")
        command_parser.add_argument("--force", action="store_true", help="Overwrite an existing import report path.")

    zotero_import = import_sub.add_parser("zotero-csv", help="Import a Zotero-style CSV export.")
    add_import_common(zotero_import)
    zotero_import.set_defaults(func=cmd_import_zotero_csv)

    csv_import = import_sub.add_parser("csv", help="Import a generic CSV using a JSON column mapping.")
    add_import_common(csv_import)
    csv_import.add_argument("--mapping", required=True, help="JSON mapping from input columns to registry fields.")
    csv_import.set_defaults(func=cmd_import_generic_csv)

    bibtex_import_parser = import_sub.add_parser("bibtex", help="Import registry rows from a local BibTeX library.")
    add_import_common(bibtex_import_parser)
    bibtex_import_parser.set_defaults(func=cmd_import_bibtex)

    ris_import = import_sub.add_parser("ris", help="Import registry rows from a conservative local RIS parser.")
    add_import_common(ris_import)
    ris_import.set_defaults(func=cmd_import_ris)

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
    claims_parser.add_argument("--force", action="store_true", help="Overwrite an existing output CSV path.")
    claims_parser.set_defaults(func=cmd_claims)

    search_parser = subparsers.add_parser("search", help="Search registry, notes, claims, or the local SQLite index.")
    search_parser.add_argument("query", help="Search query.")
    search_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
    search_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    search_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
    search_parser.add_argument("--index", default="", help="SQLite index path for --indexed search. Defaults to .paperwb/index.sqlite under the selected workspace root.")
    search_parser.add_argument("--claims", action="store_true", help="Search extracted claims only.")
    search_parser.add_argument("--notes", action="store_true", help="Search note bodies only.")
    search_parser.add_argument("--text", action="store_true", help="With --indexed, search text sidecar records only.")
    search_parser.add_argument("--indexed", action="store_true", help="Use the local SQLite search index instead of live substring search.")
    search_parser.add_argument("--exact", action="store_true", help="Require the exact phrase instead of matching all query terms.")
    search_parser.add_argument("--markdown", action="store_true", help="Print Markdown table output.")
    search_parser.add_argument("--out", default="", help="Optional Markdown output path for search results.")
    search_parser.add_argument("--force", action="store_true", help="Overwrite an existing --out path.")
    search_parser.add_argument("--limit", type=int, default=25, help="Maximum indexed search results.")
    search_parser.set_defaults(func=cmd_search)

    index_parser = subparsers.add_parser("index", help="Build, inspect, or clear the local SQLite search index.")
    index_sub = index_parser.add_subparsers(dest="index_command", required=True)

    def add_index_source_args(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
        command_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
        command_parser.add_argument("--bibtex", default=str(default_bibtex_path()), help="BibTeX file path.")
        command_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
        command_parser.add_argument("--themes", default=str(default_themes_path()), help="Themes JSON path.")
        command_parser.add_argument("--text-dir", default="", help="Optional text sidecar directory. Defaults to project/text or data/text.")
        command_parser.add_argument("--index", default="", help="SQLite index path. Defaults to .paperwb/index.sqlite under the selected workspace root.")

    index_rebuild = index_sub.add_parser("rebuild", help="Rebuild local search index records from registry, BibTeX, notes, claims, themes, tags, and optional text sidecars.")
    add_index_source_args(index_rebuild)
    index_rebuild.add_argument("--include-text", action="store_true", help="Index user-provided plain-text sidecars from --text-dir.")
    index_rebuild.add_argument("--out", default="", help="Optional Markdown index-status report path after rebuild.")
    index_rebuild.add_argument("--force", action="store_true", help="Overwrite an existing --out report.")
    index_rebuild.set_defaults(func=cmd_index_rebuild)

    index_status_parser = index_sub.add_parser("status", help="Report local search index status and optional stale-index diagnostics.")
    add_index_source_args(index_status_parser)
    index_status_parser.add_argument("--include-text", action="store_true", help="Include text sidecars when checking local files for staleness.")
    index_status_parser.add_argument("--check-files", action="store_true", help="Compare current local file-derived records with indexed content hashes.")
    index_status_parser.add_argument("--out", default="", help="Optional Markdown status report path.")
    index_status_parser.add_argument("--force", action="store_true", help="Overwrite an existing --out report.")
    index_status_parser.add_argument("--strict", action="store_true", help="Return non-zero when stale-index warnings are found.")
    index_status_parser.set_defaults(func=cmd_index_status)

    index_clear = index_sub.add_parser("clear", help="Clear indexed records for the selected project/default workflow.")
    index_clear.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
    index_clear.add_argument("--index", default="", help="SQLite index path. Defaults to .paperwb/index.sqlite under the selected workspace root.")
    index_clear.set_defaults(func=cmd_index_clear)

    files_parser = subparsers.add_parser("files", help="Scan, link, hash, and audit local user-provided files.")
    files_sub = files_parser.add_subparsers(dest="files_command", required=True)

    def add_files_common(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
        command_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
        command_parser.add_argument("--file-registry", default="", help="Local file registry CSV path. Defaults to project/files.csv or data/registries/local_files.csv.")
        command_parser.add_argument("--scan-dir", action="append", default=[], help="Directory under the selected root to scan. Repeatable. Defaults to project papers/text/notes/bibtex or legacy data/papers/data/text/data/notes/data/bibtex.")
        command_parser.add_argument("--large-file-bytes", type=int, default=50 * 1024 * 1024, help="Warn when files exceed this size.")

    files_scan = files_sub.add_parser("scan", help="Scan configured local folders for supported files without modifying them.")
    add_files_common(files_scan)
    files_scan.add_argument("--write-registry", action="store_true", help="Write the scan result to the local file registry CSV.")
    files_scan.add_argument("--force", action="store_true", help="Overwrite an existing local file registry when --write-registry is used.")
    files_scan.set_defaults(func=cmd_files_scan)

    files_status = files_sub.add_parser("status", help="Print local file registry and scan summary.")
    add_files_common(files_status)
    files_status.set_defaults(func=cmd_files_status)

    files_link = files_sub.add_parser("link", help="Link a local file to a paper ID without copying or deleting files.")
    files_link.add_argument("paper_id", help="Paper ID from the registry.")
    files_link.add_argument("path", help="Local file path to link.")
    files_link.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
    files_link.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    files_link.add_argument("--file-registry", default="", help="Local file registry CSV path. Defaults to project/files.csv or data/registries/local_files.csv.")
    files_link.add_argument("--notes", default="", help="Optional note for the local file registry record.")
    files_link.add_argument("--force", action="store_true", help="Allow replacing an existing registry local_pdf_path for PDF links.")
    files_link.set_defaults(func=cmd_files_link)

    files_unlink = files_sub.add_parser("unlink", help="Unlink file registry records for a paper ID without deleting files.")
    files_unlink.add_argument("paper_id", help="Paper ID to unlink.")
    files_unlink.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
    files_unlink.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    files_unlink.add_argument("--file-registry", default="", help="Local file registry CSV path. Defaults to project/files.csv or data/registries/local_files.csv.")
    files_unlink.add_argument("--keep-pdf-path", action="store_true", help="Do not clear registry local_pdf_path metadata.")
    files_unlink.set_defaults(func=cmd_files_unlink)

    files_audit = files_sub.add_parser("audit", help="Generate v0.7 local-file audit reports.")
    add_files_common(files_audit)
    files_audit.add_argument("--reports-dir", default="", help="Output reports directory. Defaults to the selected project/default reports directory.")
    files_audit.add_argument("--force", action="store_true", help="Overwrite existing local-file audit reports.")
    files_audit.set_defaults(func=cmd_files_audit)

    files_hash = files_sub.add_parser("hash", help="Compute SHA256 for a local file.")
    files_hash.add_argument("path", help="Local file path.")
    files_hash.set_defaults(func=cmd_files_hash)

    files_sidecars = files_sub.add_parser("sidecars", help="List or report user-provided top-level text sidecars.")
    add_files_common(files_sidecars)
    files_sidecars.add_argument("--out", default="", help="Optional Markdown sidecar report path.")
    files_sidecars.add_argument("--force", action="store_true", help="Overwrite an existing --out path.")
    files_sidecars.set_defaults(func=cmd_files_sidecars)

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
            "evidence-matrix",
            "claim-bank",
            "citation-bank",
            "paragraph-plan",
            "subsection-readiness",
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
    report_parser.add_argument("--csv-out", default="", help="Optional CSV export path for evidence-matrix reports.")
    report_parser.add_argument("--json-out", default="", help="Optional JSON export path for evidence-matrix reports.")
    report_parser.add_argument("--force", action="store_true", help="Overwrite an existing report file.")
    report_parser.set_defaults(func=cmd_report)

    writing_packet_parser = subparsers.add_parser("writing-packet", help="Generate a theme-specific literature-review writing packet from tracked evidence.")
    writing_packet_parser.add_argument("--theme", required=True, help="Theme name or ID.")
    writing_packet_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
    writing_packet_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    writing_packet_parser.add_argument("--bibtex", default=str(default_bibtex_path()), help="BibTeX file path.")
    writing_packet_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
    writing_packet_parser.add_argument("--themes", default=str(default_themes_path()), help="Themes JSON path.")
    writing_packet_parser.add_argument("--out", default="", help="Output Markdown path. Defaults to the selected reports directory.")
    writing_packet_parser.add_argument("--force", action="store_true", help="Overwrite an existing writing packet.")
    writing_packet_parser.set_defaults(func=cmd_writing_packet)

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

    integrity_parser = subparsers.add_parser("integrity", help="Run v0.9 workspace integrity checks.")
    integrity_sub = integrity_parser.add_subparsers(dest="integrity_command", required=True)
    integrity_check = integrity_sub.add_parser("check", help="Check workspace/project consistency without modifying inputs.")
    integrity_check.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
    integrity_check.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
    integrity_check.add_argument("--bibtex", default=str(default_bibtex_path()), help="BibTeX file path.")
    integrity_check.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
    integrity_check.add_argument("--themes", default=str(default_themes_path()), help="Themes JSON path.")
    integrity_check.add_argument("--reports-dir", default=str(default_reports_dir()), help="Reports output directory.")
    integrity_check.add_argument("--out", default="", help="Optional Markdown integrity report path.")
    integrity_check.add_argument("--force", action="store_true", help="Overwrite an existing --out report.")
    integrity_check.add_argument("--strict", action="store_true", help="Return non-zero when integrity errors are found.")
    integrity_check.set_defaults(func=cmd_integrity_check)

    audit_log_parser = subparsers.add_parser("audit-log", help="Show or clear the local v0.9 audit log.")
    audit_log_sub = audit_log_parser.add_subparsers(dest="audit_log_command", required=True)
    audit_log_show = audit_log_sub.add_parser("show", help="Show audit events for the selected workspace/project.")
    audit_log_show.add_argument("--project", default="", help="Use a project profile audit log.")
    audit_log_show.add_argument("--path", default="", help="Explicit audit log path.")
    audit_log_show.add_argument("--limit", type=int, default=0, help="Show only the most recent N events.")
    audit_log_show.add_argument("--markdown", action="store_true", help="Print Markdown output.")
    audit_log_show.add_argument("--out", default="", help="Optional Markdown output path.")
    audit_log_show.add_argument("--force", action="store_true", help="Overwrite an existing --out report.")
    audit_log_show.set_defaults(func=cmd_audit_log_show)
    audit_log_clear = audit_log_sub.add_parser("clear", help="Clear the selected audit log. Requires --force.")
    audit_log_clear.add_argument("--project", default="", help="Use a project profile audit log.")
    audit_log_clear.add_argument("--path", default="", help="Explicit audit log path.")
    audit_log_clear.add_argument("--force", action="store_true", help="Required confirmation to clear the audit log.")
    audit_log_clear.set_defaults(func=cmd_audit_log_clear)

    backup_parser = subparsers.add_parser("backup", help="Create, inspect, and restore local v0.9 backups.")
    backup_sub = backup_parser.add_subparsers(dest="backup_command", required=True)

    def add_backup_common(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument("--project", default="", help="Use a project profile instead of default data/ paths.")
        command_parser.add_argument("--registry", default=str(default_registry_path()), help="Registry CSV path.")
        command_parser.add_argument("--bibtex", default=str(default_bibtex_path()), help="BibTeX file path.")
        command_parser.add_argument("--notes-dir", default=str(default_notes_dir()), help="Notes directory.")
        command_parser.add_argument("--themes", default=str(default_themes_path()), help="Themes JSON path.")
        command_parser.add_argument("--reports-dir", default=str(default_reports_dir()), help="Reports directory.")
        command_parser.add_argument("--backups-dir", default="", help="Optional backups directory. Defaults to backups/ under the selected root.")

    backup_create = backup_sub.add_parser("create", help="Create a local backup snapshot. PDFs and caches are excluded by default.")
    add_backup_common(backup_create)
    backup_create.add_argument("--include-reports", action="store_true", help="Include generated Markdown reports in the backup.")
    backup_create.add_argument("--notes", default="", help="Optional backup note stored in the manifest.")
    backup_create.set_defaults(func=cmd_backup_create)
    backup_list = backup_sub.add_parser("list", help="List local backup snapshots.")
    add_backup_common(backup_list)
    backup_list.set_defaults(func=cmd_backup_list)
    backup_inspect = backup_sub.add_parser("inspect", help="Inspect a backup manifest.")
    backup_inspect.add_argument("backup_id", help="Backup ID to inspect.")
    add_backup_common(backup_inspect)
    backup_inspect.add_argument("--out", default="", help="Optional Markdown manifest report path.")
    backup_inspect.add_argument("--force", action="store_true", help="Overwrite an existing --out path.")
    backup_inspect.set_defaults(func=cmd_backup_inspect)
    backup_plan = backup_sub.add_parser("plan-restore", help="Plan a restore without modifying files.")
    backup_plan.add_argument("backup_id", help="Backup ID to restore.")
    add_backup_common(backup_plan)
    backup_plan.add_argument("--out", default="", help="Optional Markdown restore-plan report path.")
    backup_plan.add_argument("--force", action="store_true", help="Overwrite an existing --out path.")
    backup_plan.set_defaults(func=cmd_backup_plan_restore)
    backup_restore = backup_sub.add_parser("restore", help="Restore files from a backup. Defaults to dry-run unless --force is provided.")
    backup_restore.add_argument("backup_id", help="Backup ID to restore.")
    add_backup_common(backup_restore)
    backup_restore.add_argument("--dry-run", action="store_true", help="Plan the restore without writing files.")
    backup_restore.add_argument("--force", action="store_true", help="Actually restore files from the backup.")
    backup_restore.add_argument("--no-pre-restore-backup", action="store_true", help="Do not create a pre-restore backup when --force is used.")
    backup_restore.add_argument("--out", default="", help="Optional Markdown restore report path.")
    backup_restore.add_argument("--force-report", action="store_true", help="Overwrite an existing --out report path.")
    backup_restore.set_defaults(func=cmd_backup_restore)

    migrate_parser = subparsers.add_parser("migrate", help="Plan or run non-destructive workspace migrations.")
    migrate_sub = migrate_parser.add_subparsers(dest="migrate_command", required=True)
    migrate_plan = migrate_sub.add_parser("plan", help="Plan a legacy data/ to project-profile migration.")
    migrate_plan.add_argument("--from", dest="from_workflow", default="legacy", choices=["legacy"], help="Source workflow. Only legacy is supported in v0.9.")
    migrate_plan.add_argument("--to-project", required=True, help="New project profile name to create.")
    migrate_plan.add_argument("--root", default=".", help="Workspace root.")
    migrate_plan.add_argument("--out", default="", help="Optional Markdown migration plan path.")
    migrate_plan.add_argument("--force", action="store_true", help="Overwrite an existing --out report.")
    migrate_plan.add_argument("--strict", action="store_true", help="Return non-zero when migration conflicts are present.")
    migrate_plan.set_defaults(func=cmd_migrate_plan)
    migrate_run = migrate_sub.add_parser("run", help="Run or dry-run a legacy data/ to project-profile migration.")
    migrate_run.add_argument("--from", dest="from_workflow", default="legacy", choices=["legacy"], help="Source workflow. Only legacy is supported in v0.9.")
    migrate_run.add_argument("--to-project", required=True, help="New project profile name to create.")
    migrate_run.add_argument("--root", default=".", help="Workspace root.")
    migrate_run.add_argument("--dry-run", action="store_true", help="Plan the migration without copying files.")
    migrate_run.add_argument("--force", action="store_true", help="Actually copy files into the new project. Existing targets still block.")
    migrate_run.add_argument("--out", default="", help="Optional Markdown migration report path.")
    migrate_run.add_argument("--force-report", action="store_true", help="Overwrite an existing --out report path.")
    migrate_run.add_argument("--strict", action="store_true", help="Return non-zero when migration conflicts are present.")
    migrate_run.set_defaults(func=cmd_migrate_run)

    export_parser = subparsers.add_parser("export", help="Export local data to CSV, JSON, or Markdown.")
    export_parser.add_argument(
        "export_type",
        choices=[
            "registry-csv",
            "registry-json",
            "claims",
            "claims-json",
            "reading-list",
            "unread",
            "theme-claims",
            "obsidian",
            "bundle",
            "project-summary",
            "report-index",
        ],
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
    export_parser.add_argument("--format", choices=["markdown", "csv"], default="markdown", help="Reading-list output format.")
    export_parser.add_argument("--included", action="store_true", help="Filter reading-list to papers included in the literature review.")
    export_parser.add_argument("--excluded", action="store_true", help="Filter reading-list to excluded papers and include exclude reasons.")
    export_parser.add_argument("--high-priority", action="store_true", help="Filter reading-list to high or critical priority papers.")
    export_parser.add_argument("--missing-notes", action="store_true", help="Filter reading-list to papers without parsed notes.")
    export_parser.add_argument("--include-pdfs", action="store_true", help="For bundle export only: copy existing local PDFs. Default is false.")
    export_parser.add_argument("--force", action="store_true", help="Overwrite an existing export file. Directory exports still require an empty output directory.")
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
