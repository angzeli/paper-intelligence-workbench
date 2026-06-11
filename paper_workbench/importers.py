"""Local-only importers for common bibliography exchange formats."""

from __future__ import annotations

import csv
import json
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
import re

from .bibtex import parse_bibtex_file
from .errors import format_error_message
from .io import load_json, read_text, write_text
from .paths import display_path
from .registry import REGISTRY_FIELDS, generate_paper_id, normalize_doi, normalize_title, parse_authors, paper_from_row, paper_to_row
from .schema import Author, Paper, SourceType, ValidationFinding, enum_values
from .tags import format_tags, parse_tags


KNOWN_ZOTERO_FIELDS = {
    "title",
    "author",
    "publicationyear",
    "publicationtitle",
    "doi",
    "url",
    "itemtype",
    "dateadded",
    "tags",
    "manualtags",
    "abstractnote",
}
RIS_KNOWN_FIELDS = {"TY", "TI", "T1", "AU", "PY", "Y1", "JO", "JF", "T2", "DO", "UR", "KW", "ER"}
SOURCE_TYPE_BY_LABEL = {
    "journal article": SourceType.JOURNAL_ARTICLE.value,
    "journal_article": SourceType.JOURNAL_ARTICLE.value,
    "article": SourceType.JOURNAL_ARTICLE.value,
    "conference paper": SourceType.CONFERENCE_PAPER.value,
    "conference_paper": SourceType.CONFERENCE_PAPER.value,
    "conference": SourceType.CONFERENCE_PAPER.value,
    "inproceedings": SourceType.CONFERENCE_PAPER.value,
    "proceedings": SourceType.CONFERENCE_PAPER.value,
    "book": SourceType.BOOK.value,
    "thesis": SourceType.THESIS.value,
    "phdthesis": SourceType.THESIS.value,
    "mastersthesis": SourceType.THESIS.value,
    "preprint": SourceType.PREPRINT.value,
    "report": SourceType.REPORT.value,
    "techreport": SourceType.REPORT.value,
    "review": SourceType.REVIEW.value,
    "dataset": SourceType.DATASET.value,
    "misc": SourceType.OTHER.value,
    "manual": SourceType.OTHER.value,
    "unpublished": SourceType.OTHER.value,
    "webpage": SourceType.OTHER.value,
    "document": SourceType.OTHER.value,
    "jour": SourceType.JOURNAL_ARTICLE.value,
    "conf": SourceType.CONFERENCE_PAPER.value,
    "thes": SourceType.THESIS.value,
    "rprt": SourceType.REPORT.value,
    "elec": SourceType.OTHER.value,
}


@dataclass(slots=True)
class ImportCandidate:
    paper: Paper
    row_number: int
    source_identifier: str
    warnings: list[ValidationFinding] = field(default_factory=list)
    unmapped_fields: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ImportResult:
    source_type: str
    source_path: str
    project: str
    registry_path: str
    rows_read: int
    imported: int = 0
    updated: int = 0
    skipped: int = 0
    dry_run: bool = False
    warnings: list[ValidationFinding] = field(default_factory=list)
    unmapped_fields: list[str] = field(default_factory=list)
    imported_paper_ids: list[str] = field(default_factory=list)
    updated_paper_ids: list[str] = field(default_factory=list)
    skipped_records: list[str] = field(default_factory=list)
    registry_papers: list[Paper] = field(default_factory=list)


def _header_key(value: str) -> str:
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]+", "", value.strip().lower())


def _issue(severity: str, code: str, message: str, row_number: int = 0, identifier: str = "", suggestion: str = "") -> ValidationFinding:
    source = f"row {row_number}" if row_number else ""
    return ValidationFinding(severity=severity, code=code, message=message, source=source, identifier=identifier, suggestion=suggestion)


def _source_type(value: str, warnings: list[ValidationFinding], row_number: int) -> str:
    if not value:
        return SourceType.OTHER.value
    normalized = value.strip().lower().replace("-", " ").replace("_", " ")
    source_type = SOURCE_TYPE_BY_LABEL.get(normalized) or SOURCE_TYPE_BY_LABEL.get(normalized.replace(" ", "_"))
    if source_type:
        return source_type
    warnings.append(
        _issue(
            "warning",
            "unsupported_item_type",
            f"Unsupported item type {value!r}; mapped to other.",
            row_number,
            value,
            "Review source_type after import.",
        )
    )
    return SourceType.OTHER.value


def _year(value: str) -> str:
    match = re.search(r"\d{4}", value or "")
    return match.group(0) if match else (value or "").strip()


def _unmapped_fields(row: dict[str, str], known_keys: set[str]) -> list[str]:
    fields: list[str] = []
    for key, value in row.items():
        if key is not None and value and _header_key(key) not in known_keys:
            fields.append(key)
    return sorted(set(fields))


def _reader_or_error(handle, source: Path) -> csv.DictReader:
    try:
        reader = csv.DictReader(handle)
    except csv.Error as exc:
        raise ValueError(
            format_error_message(
                what="Could not read CSV input.",
                where=str(source),
                why="The import cannot safely map rows when the CSV structure is malformed.",
                next_step=f"Fix the CSV syntax locally and retry. Parser detail: {exc}",
            )
        ) from exc
    if reader.fieldnames is None:
        raise ValueError(
            format_error_message(
                what="CSV input has no header row.",
                where=str(source),
                why="The importer needs named columns to map records into registry fields.",
                next_step="Add a header row such as Title, Author, Publication Year, DOI.",
            )
        )
    return reader


def _missing_columns(reader: csv.DictReader, required: set[str]) -> set[str]:
    available = {_header_key(field) for field in reader.fieldnames or []}
    return {column for column in required if column not in available}


def _paper_from_fields(
    fields: dict[str, str],
    *,
    existing_ids: set[str],
    project: str,
    source_label: str,
    row_number: int,
    warnings: list[ValidationFinding],
) -> Paper:
    title = (fields.get("title") or "").strip()
    authors = parse_authors(fields.get("authors", ""))
    year = _year(fields.get("year", ""))
    paper_id = (fields.get("paper_id") or "").strip() or generate_paper_id(title or "untitled import", authors, year, existing_ids)
    existing_ids.add(paper_id)
    tags = parse_tags(fields.get("tags", ""))
    if source_label:
        tags = parse_tags(tags + [source_label])
    row = {field_name: "" for field_name in REGISTRY_FIELDS}
    row.update(
        {
            "paper_id": paper_id,
            "title": title,
            "authors": fields.get("authors", ""),
            "year": year,
            "journal": fields.get("journal", ""),
            "doi": normalize_doi(fields.get("doi", "")),
            "url": fields.get("url", ""),
            "bibtex_key": fields.get("bibtex_key", ""),
            "tags": format_tags(tags),
            "reading_status": fields.get("reading_status", "unread") or "unread",
            "added_date": fields.get("added_date", "") or date.today().isoformat(),
            "priority": fields.get("priority", ""),
            "project": project or fields.get("project", ""),
            "source_type": fields.get("source_type", "") or SourceType.OTHER.value,
            "reading_priority": fields.get("reading_priority", ""),
            "included_in_lit_review": fields.get("included_in_lit_review", ""),
            "exclude_reason": fields.get("exclude_reason", ""),
            "user_comment": fields.get("user_comment", ""),
        }
    )
    if not title:
        warnings.append(_issue("error", "missing_title", "Imported record is missing title.", row_number, paper_id, "Add a title before importing."))
    if not fields.get("authors", "").strip():
        warnings.append(_issue("warning", "missing_author", f"{paper_id} is missing author.", row_number, paper_id))
    if not year:
        warnings.append(_issue("warning", "missing_year", f"{paper_id} is missing year.", row_number, paper_id))
    return paper_from_row(row)


def _match_existing(paper: Paper, papers: list[Paper]) -> list[Paper]:
    matches: dict[str, Paper] = {}
    doi = normalize_doi(paper.doi)
    title = normalize_title(paper.title)
    bibtex_key = paper.bibtex_key.strip()
    for existing in papers:
        if doi and normalize_doi(existing.doi) == doi:
            matches[existing.paper_id] = existing
        if title and normalize_title(existing.title) == title:
            matches[existing.paper_id] = existing
        if bibtex_key and existing.bibtex_key.strip() == bibtex_key:
            matches[existing.paper_id] = existing
    return list(matches.values())


def _blank(value) -> bool:
    if isinstance(value, list):
        return not value
    return not str(value or "").strip()


def _fill_missing(target: Paper, source: Paper) -> list[str]:
    changed: list[str] = []
    for field_name in REGISTRY_FIELDS:
        if field_name == "paper_id":
            continue
        incoming = getattr(source, field_name)
        current = getattr(target, field_name)
        if _blank(current) and not _blank(incoming):
            setattr(target, field_name, incoming)
            changed.append(field_name)
    return changed


def _merge_candidates(
    *,
    source_type: str,
    source_path: str | Path,
    candidates: list[ImportCandidate],
    existing_papers: list[Paper],
    registry_path: str | Path,
    project: str = "",
    dry_run: bool = False,
    fill_missing: bool = False,
) -> ImportResult:
    working = deepcopy(existing_papers)
    result = ImportResult(
        source_type=source_type,
        source_path=str(source_path),
        project=project,
        registry_path=str(registry_path),
        rows_read=len(candidates),
        dry_run=dry_run,
        registry_papers=working,
    )
    for candidate in candidates:
        result.warnings.extend(candidate.warnings)
        result.unmapped_fields.extend(candidate.unmapped_fields)
        if not candidate.paper.title:
            result.skipped += 1
            result.skipped_records.append(candidate.source_identifier)
            continue
        matches = _match_existing(candidate.paper, working)
        if len(matches) > 1:
            result.skipped += 1
            result.skipped_records.append(candidate.source_identifier)
            result.warnings.append(
                _issue(
                    "warning",
                    "ambiguous_match",
                    f"{candidate.source_identifier} matched multiple registry rows: {', '.join(sorted(p.paper_id for p in matches))}.",
                    candidate.row_number,
                    candidate.source_identifier,
                    "Review DOI, title, and BibTeX key before importing.",
                )
            )
            continue
        if len(matches) == 1:
            matched = matches[0]
            if fill_missing:
                changed = _fill_missing(matched, candidate.paper)
                if changed:
                    result.updated += 1
                    result.updated_paper_ids.append(matched.paper_id)
                    result.warnings.append(
                        _issue(
                            "info",
                            "filled_missing_fields",
                            f"{matched.paper_id} would fill missing fields: {', '.join(changed)}." if dry_run else f"{matched.paper_id} filled missing fields: {', '.join(changed)}.",
                            candidate.row_number,
                            matched.paper_id,
                        )
                    )
                else:
                    result.skipped += 1
                    result.skipped_records.append(candidate.source_identifier)
            else:
                result.skipped += 1
                result.skipped_records.append(candidate.source_identifier)
                result.warnings.append(
                    _issue(
                        "warning",
                        "duplicate_record",
                        f"{candidate.source_identifier} matches existing registry row {matched.paper_id}; skipped.",
                        candidate.row_number,
                        candidate.source_identifier,
                        "Use --fill-missing only when you want blank registry fields completed.",
                    )
                )
            continue
        working.append(candidate.paper)
        result.imported += 1
        result.imported_paper_ids.append(candidate.paper.paper_id)
    result.unmapped_fields = sorted(set(result.unmapped_fields))
    if not dry_run:
        existing_papers[:] = working
    result.registry_papers = working
    return result


def import_zotero_csv(
    path: str | Path,
    existing_papers: list[Paper],
    *,
    registry_path: str | Path,
    project: str = "",
    dry_run: bool = False,
    fill_missing: bool = False,
) -> ImportResult:
    source = Path(path)
    existing_ids = {paper.paper_id for paper in existing_papers}
    candidates: list[ImportCandidate] = []
    with source.open(newline="", encoding="utf-8") as handle:
        reader = _reader_or_error(handle, source)
        missing = _missing_columns(reader, {"title"})
        if missing:
            raise ValueError(
                format_error_message(
                    what="Zotero CSV import is missing required columns.",
                    where=str(source),
                    why="Rows without a Title column cannot become reliable registry records.",
                    next_step=f"Export Title from Zotero or rename the title column. Missing: {', '.join(sorted(missing))}.",
                )
            )
        for row_number, row in enumerate(reader, start=2):
            normalized = {_header_key(key): value for key, value in row.items()}
            warnings: list[ValidationFinding] = []
            source_type = _source_type(normalized.get("itemtype", ""), warnings, row_number)
            tags = parse_tags(f"{normalized.get('tags', '')}; {normalized.get('manualtags', '')}")
            abstract = normalized.get("abstractnote", "").strip()
            fields = {
                "title": normalized.get("title", ""),
                "authors": normalized.get("author", ""),
                "year": normalized.get("publicationyear", ""),
                "journal": normalized.get("publicationtitle", ""),
                "doi": normalized.get("doi", ""),
                "url": normalized.get("url", ""),
                "source_type": source_type,
                "added_date": normalized.get("dateadded", ""),
                "tags": format_tags(tags),
                "user_comment": f"Imported from Zotero-style CSV. Abstract note: {abstract[:240]}" if abstract else "Imported from Zotero-style CSV.",
            }
            paper = _paper_from_fields(fields, existing_ids=existing_ids, project=project, source_label="imported-zotero", row_number=row_number, warnings=warnings)
            candidates.append(
                ImportCandidate(
                    paper=paper,
                    row_number=row_number,
                    source_identifier=paper.title or f"row {row_number}",
                    warnings=warnings,
                    unmapped_fields=_unmapped_fields(row, KNOWN_ZOTERO_FIELDS),
                )
            )
    return _merge_candidates(
        source_type="zotero-csv",
        source_path=source,
        candidates=candidates,
        existing_papers=existing_papers,
        registry_path=registry_path,
        project=project,
        dry_run=dry_run,
        fill_missing=fill_missing,
    )


def _mapping_columns(path: str | Path) -> dict[str, str]:
    try:
        data = load_json(path)
    except json.JSONDecodeError as exc:
        raise ValueError(
            format_error_message(
                what="Import mapping is not valid JSON.",
                where=str(path),
                why="The generic CSV importer cannot determine how to map columns.",
                next_step=f"Fix the JSON mapping file and retry. Parser detail: {exc.msg}",
            )
        ) from exc
    mapping = data.get("columns", data.get("mapping", data))
    if not isinstance(mapping, dict):
        raise ValueError(
            format_error_message(
                what="Import mapping has the wrong shape.",
                where=str(path),
                why="The generic CSV importer expects a JSON object or a `columns` object.",
                next_step='Use a mapping like {"columns": {"Title": "title"}}.',
            )
        )
    normalized: dict[str, str] = {}
    for source, target in mapping.items():
        if target not in REGISTRY_FIELDS:
            raise ValueError(
                format_error_message(
                    what=f"Import mapping target {target!r} is not a registry field.",
                    where=str(path),
                    why="Writing to unknown fields would silently drop user data.",
                    next_step=f"Use one of: {', '.join(REGISTRY_FIELDS)}.",
                )
            )
        normalized[str(source)] = str(target)
    return normalized


def import_generic_csv(
    path: str | Path,
    mapping_path: str | Path,
    existing_papers: list[Paper],
    *,
    registry_path: str | Path,
    project: str = "",
    dry_run: bool = False,
    fill_missing: bool = False,
) -> ImportResult:
    source = Path(path)
    mapping = _mapping_columns(mapping_path)
    existing_ids = {paper.paper_id for paper in existing_papers}
    known_headers = {_header_key(key) for key in mapping}
    candidates: list[ImportCandidate] = []
    with source.open(newline="", encoding="utf-8") as handle:
        reader = _reader_or_error(handle, source)
        missing = [column for column in mapping if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(
                format_error_message(
                    what="Generic CSV mapping references missing source columns.",
                    where=str(source),
                    why="The importer cannot safely map fields that are not present in the CSV header.",
                    next_step=f"Fix the mapping or CSV header. Missing columns: {', '.join(missing)}.",
                )
            )
        for row_number, row in enumerate(reader, start=2):
            warnings: list[ValidationFinding] = []
            fields = {registry_field: row.get(source_field, "") for source_field, registry_field in mapping.items()}
            paper = _paper_from_fields(fields, existing_ids=existing_ids, project=project, source_label="imported-csv", row_number=row_number, warnings=warnings)
            candidates.append(
                ImportCandidate(
                    paper=paper,
                    row_number=row_number,
                    source_identifier=paper.title or f"row {row_number}",
                    warnings=warnings,
                    unmapped_fields=_unmapped_fields(row, known_headers),
                )
            )
    return _merge_candidates(
        source_type="generic-csv",
        source_path=source,
        candidates=candidates,
        existing_papers=existing_papers,
        registry_path=registry_path,
        project=project,
        dry_run=dry_run,
        fill_missing=fill_missing,
    )


def import_bibtex(
    path: str | Path,
    existing_papers: list[Paper],
    *,
    registry_path: str | Path,
    project: str = "",
    dry_run: bool = False,
    fill_missing: bool = False,
) -> ImportResult:
    entries = parse_bibtex_file(path)
    existing_ids = {paper.paper_id for paper in existing_papers}
    candidates: list[ImportCandidate] = []
    for row_number, entry in enumerate(entries, start=1):
        warnings = [
            _issue("warning", "bibtex_parse_warning", warning, row_number, entry.key, "Review this entry before relying on imported metadata.")
            for warning in entry.parse_warnings
        ]
        source_type = _source_type(entry.entry_type, warnings, row_number)
        fields = {
            "title": entry.title,
            "authors": "; ".join(author.bibtex_display() for author in entry.authors),
            "year": entry.year,
            "journal": entry.venue(),
            "doi": entry.doi,
            "url": entry.url,
            "bibtex_key": entry.key,
            "source_type": source_type,
            "tags": "imported-bibtex",
            "user_comment": "Imported from local BibTeX.",
        }
        paper = _paper_from_fields(fields, existing_ids=existing_ids, project=project, source_label="", row_number=row_number, warnings=warnings)
        candidates.append(ImportCandidate(paper=paper, row_number=row_number, source_identifier=entry.key or paper.title or f"entry {row_number}", warnings=warnings))
    return _merge_candidates(
        source_type="bibtex",
        source_path=path,
        candidates=candidates,
        existing_papers=existing_papers,
        registry_path=registry_path,
        project=project,
        dry_run=dry_run,
        fill_missing=fill_missing,
    )


def parse_ris(text: str) -> list[dict[str, list[str]]]:
    records: list[dict[str, list[str]]] = []
    current: dict[str, list[str]] = {}
    for raw_line in text.splitlines():
        if not raw_line.strip():
            continue
        match = re.match(r"^([A-Z0-9]{2})\s*-\s*(.*)$", raw_line)
        if not match:
            continue
        tag, value = match.group(1), match.group(2).strip()
        if tag == "TY":
            current = {"TY": [value]}
        elif tag == "ER":
            if current:
                records.append(current)
            current = {}
        else:
            current.setdefault(tag, []).append(value)
    if current:
        records.append(current)
    return records


def import_ris(
    path: str | Path,
    existing_papers: list[Paper],
    *,
    registry_path: str | Path,
    project: str = "",
    dry_run: bool = False,
    fill_missing: bool = False,
) -> ImportResult:
    records = parse_ris(read_text(path))
    existing_ids = {paper.paper_id for paper in existing_papers}
    candidates: list[ImportCandidate] = []
    for row_number, record in enumerate(records, start=1):
        warnings: list[ValidationFinding] = []
        title = (record.get("TI") or record.get("T1") or [""])[0]
        year = _year((record.get("PY") or record.get("Y1") or [""])[0])
        source_type = _source_type((record.get("TY") or [""])[0], warnings, row_number)
        fields = {
            "title": title,
            "authors": "; ".join(record.get("AU", [])),
            "year": year,
            "journal": (record.get("JO") or record.get("JF") or record.get("T2") or [""])[0],
            "doi": (record.get("DO") or [""])[0],
            "url": (record.get("UR") or [""])[0],
            "source_type": source_type,
            "tags": format_tags(record.get("KW", []) + ["imported-ris"]),
            "user_comment": "Imported from local RIS.",
        }
        paper = _paper_from_fields(fields, existing_ids=existing_ids, project=project, source_label="", row_number=row_number, warnings=warnings)
        unknown = sorted(tag for tag, values in record.items() if tag not in RIS_KNOWN_FIELDS and any(values))
        for tag in unknown:
            warnings.append(_issue("warning", "unmapped_field", f"RIS tag {tag} was not mapped.", row_number, tag))
        candidates.append(
            ImportCandidate(
                paper=paper,
                row_number=row_number,
                source_identifier=paper.title or f"RIS record {row_number}",
                warnings=warnings,
                unmapped_fields=unknown,
            )
        )
    return _merge_candidates(
        source_type="ris",
        source_path=path,
        candidates=candidates,
        existing_papers=existing_papers,
        registry_path=registry_path,
        project=project,
        dry_run=dry_run,
        fill_missing=fill_missing,
    )


def import_report(result: ImportResult) -> str:
    lines = [
        f"# Import Report: {result.source_type}",
        "",
        f"- Source file: {_display_path(result.source_path)}",
        f"- Project: {result.project or 'default data workflow'}",
        f"- Dry run: {str(result.dry_run).lower()}",
        f"- Rows read: {result.rows_read}",
        f"- Records imported: {result.imported}",
        f"- Records updated: {result.updated}",
        f"- Records skipped: {result.skipped}",
        f"- Output registry path: {_display_path(result.registry_path)}",
        "",
        "## Imported Paper IDs",
        "",
    ]
    lines.extend(f"- {paper_id}" for paper_id in result.imported_paper_ids) if result.imported_paper_ids else lines.append("- None.")
    lines.extend(["", "## Updated Paper IDs", ""])
    lines.extend(f"- {paper_id}" for paper_id in result.updated_paper_ids) if result.updated_paper_ids else lines.append("- None.")
    lines.extend(["", "## Skipped Records", ""])
    lines.extend(f"- {record}" for record in result.skipped_records) if result.skipped_records else lines.append("- None.")
    lines.extend(["", "## Unmapped Fields", ""])
    lines.extend(f"- {field_name}" for field_name in sorted(set(result.unmapped_fields))) if result.unmapped_fields else lines.append("- None.")
    lines.extend(["", "## Warnings", ""])
    if result.warnings:
        lines.extend(["| Severity | Code | Source | Identifier | Message | Suggestion |", "| --- | --- | --- | --- | --- | --- |"])
        for warning in result.warnings:
            lines.append(
                "| {severity} | {code} | {source} | {identifier} | {message} | {suggestion} |".format(
                    severity=warning.severity,
                    code=warning.code,
                    source=_escape(warning.source),
                    identifier=_escape(warning.identifier),
                    message=_escape(warning.message),
                    suggestion=_escape(warning.suggestion),
                )
            )
    else:
        lines.append("No warnings.")
    return "\n".join(lines).rstrip() + "\n"


def _display_path(path: str | Path) -> str:
    return display_path(path)


def write_import_report(result: ImportResult, out: str | Path, *, force: bool = False) -> Path:
    return write_text(out, import_report(result), force=force)


def _escape(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
