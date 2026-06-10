"""Workspace health diagnostics."""

from __future__ import annotations

from pathlib import Path

from .bibtex import parse_bibtex_file, validate_bibtex
from .claims import collect_notes
from .registry import load_registry, validate_registry
from .schema import ProjectProfile, ValidationFinding
from .tags import group_claims_by_theme, load_themes, normalize_tag, theme_by_tag


def _finding(severity: str, code: str, message: str, identifier: str = "", suggestion: str = "") -> ValidationFinding:
    return ValidationFinding(severity=severity, code=code, message=message, identifier=identifier, suggestion=suggestion)


def workspace_health(
    *,
    root: str | Path = ".",
    registry_path: str | Path,
    bibtex_path: str | Path,
    notes_dir: str | Path,
    themes_path: str | Path,
    reports_dir: str | Path,
    profile: ProjectProfile | None = None,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    root_path = Path(root)
    registry = Path(registry_path)
    bibtex = Path(bibtex_path)
    notes_path = Path(notes_dir)
    themes = Path(themes_path)
    reports = Path(reports_dir)
    expected_dirs = [notes_path, bibtex.parent, reports]
    if profile is None:
        expected_dirs.extend([root_path / "data" / "registries", root_path / "data" / "bibtex", root_path / "data" / "notes"])
    for directory in expected_dirs:
        if not directory.exists():
            findings.append(
                _finding(
                    "warning",
                    "missing_expected_folder",
                    f"Expected folder is missing: {directory}",
                    str(directory),
                    "Run paperwb init or paperwb project init to create the structure.",
                )
            )
    papers = []
    notes = []
    claims = []
    entries = []
    theme_defs = []
    if not registry.exists():
        findings.append(_finding("error", "missing_registry", f"Registry file is missing: {registry}", str(registry)))
    else:
        papers = load_registry(registry)
    if not bibtex.exists():
        findings.append(_finding("warning", "missing_bibtex_file", f"BibTeX file is missing: {bibtex}", str(bibtex)))
    else:
        entries = parse_bibtex_file(bibtex)
    if not notes_path.exists():
        findings.append(_finding("warning", "missing_notes_folder", f"Notes folder is missing: {notes_path}", str(notes_path)))
    else:
        notes = collect_notes(notes_path)
        if not notes:
            findings.append(_finding("warning", "empty_notes_folder", f"Notes folder has no Markdown notes: {notes_path}", str(notes_path)))
        for note in notes:
            claims.extend(note.claims)
            for warning in note.warnings:
                findings.append(
                    _finding(
                        "warning",
                        "note_parse_warning",
                        f"{Path(note.source_path).name}: {warning}",
                        note.paper_id or note.source_path,
                        "Review the note against the structured note format.",
                    )
                )
    if themes.exists():
        theme_defs = load_themes(themes)
    else:
        findings.append(_finding("warning", "missing_themes_file", f"Themes file is missing: {themes}", str(themes)))
    if not reports.exists():
        findings.append(_finding("warning", "reports_folder_missing", f"Reports folder is missing: {reports}", str(reports)))
    if papers:
        findings.extend(validate_registry(papers, root=root_path, claims=claims))
    if entries or papers:
        findings.extend(validate_bibtex(entries, papers))
    registry_ids = {paper.paper_id for paper in papers}
    note_ids = {note.paper_id for note in notes if note.paper_id}
    claim_paper_ids = {claim.paper_id for claim in claims if claim.paper_id}
    for note in notes:
        if note.paper_id and note.paper_id not in registry_ids:
            findings.append(
                _finding(
                    "warning",
                    "note_without_registry_entry",
                    f"Note {note.source_path} references unknown paper_id {note.paper_id}.",
                    note.paper_id,
                    "Add a registry row or correct the note metadata.",
                )
            )
        if not note.claims:
            findings.append(
                _finding(
                    "warning",
                    "note_without_claims",
                    f"Note {note.source_path} has no structured claims.",
                    note.paper_id,
                    "Add claim blocks when this note supports the review.",
                )
            )
    for paper in papers:
        if paper.paper_id not in note_ids and not paper.notes_path:
            findings.append(
                _finding(
                    "warning",
                    "registry_paper_without_notes",
                    f"{paper.paper_id} has no parsed note and no notes_path.",
                    paper.paper_id,
                    "Generate a note template or update notes_path.",
                )
            )
    tag_theme = theme_by_tag(theme_defs)
    theme_ids = {theme.theme_id for theme in theme_defs}
    grouped = group_claims_by_theme(claims, theme_defs)
    for theme in theme_defs:
        theme_claims = grouped.get(theme.theme_id, [])
        theme_papers = {claim.paper_id for claim in theme_claims if claim.paper_id}
        if len(theme_claims) < theme.min_claims:
            findings.append(
                _finding(
                    "warning",
                    "theme_under_supported",
                    f"{theme.name} has {len(theme_claims)} supporting claim(s); target is {theme.min_claims}.",
                    theme.theme_id,
                    "Add more verified claims or adjust the theme threshold.",
                )
            )
        if len(theme_papers) < theme.min_papers:
            findings.append(
                _finding(
                    "warning",
                    "theme_too_few_papers",
                    f"{theme.name} has evidence from {len(theme_papers)} paper(s); target is {theme.min_papers}.",
                    theme.theme_id,
                    "Add evidence from more papers or adjust the theme threshold.",
                )
            )
    for claim in claims:
        if not (claim.section or claim.page):
            findings.append(
                _finding(
                    "error",
                    "claim_missing_evidence_location",
                    f"{claim.claim_id} has no section/page evidence location.",
                    claim.claim_id,
                    "Add a section, page, figure, table, or appendix location.",
                )
            )
        if not claim.confidence:
            findings.append(
                _finding("warning", "claim_missing_confidence", f"{claim.claim_id} has no confidence value.", claim.claim_id)
            )
        if not claim.tags:
            findings.append(_finding("warning", "claim_missing_tags", f"{claim.claim_id} has no tags.", claim.claim_id))
        if claim.supports_theme and normalize_tag(claim.supports_theme) not in theme_ids:
            findings.append(
                _finding(
                    "warning",
                    "claim_theme_without_definition",
                    f"{claim.claim_id} supports undefined theme {claim.supports_theme!r}.",
                    claim.claim_id,
                    "Add the theme definition or correct Supports theme.",
                )
            )
        if claim.tags and not any(tag in tag_theme for tag in claim.tags):
            findings.append(
                _finding(
                    "warning",
                    "claim_without_theme_mapping",
                    f"{claim.claim_id} tags do not map to a defined theme.",
                    claim.claim_id,
                    "Add a matching theme tag or revise the claim tags.",
                )
            )
    for paper_id in sorted(registry_ids - claim_paper_ids):
        matching = [paper for paper in papers if paper.paper_id == paper_id]
        if matching and matching[0].reading_status in {"read", "deeply_read"}:
            findings.append(
                _finding(
                    "warning",
                    "read_paper_without_claims",
                    f"{paper_id} is read/deeply_read but has no extracted claims.",
                    paper_id,
                    "Add structured claims if this paper supports the review.",
                )
            )
    return findings
