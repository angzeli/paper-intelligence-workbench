"""Paper registry loading, saving, filtering, and validation."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
import json
from pathlib import Path
import re
import unicodedata

from .errors import format_error_message
from .io import read_csv_rows, write_csv_rows, write_json
from .schema import Author, Claim, Paper, ReadingStatus, SourceType, ValidationFinding, dataclass_to_plain, enum_values
from .tags import format_tags, parse_tags


REGISTRY_FIELDS = [
    "paper_id",
    "title",
    "authors",
    "year",
    "journal",
    "doi",
    "url",
    "local_pdf_path",
    "bibtex_key",
    "tags",
    "reading_status",
    "notes_path",
    "added_date",
    "last_reviewed_date",
    "priority",
    "project",
    "source_type",
    "relevance_score",
    "reading_priority",
    "included_in_lit_review",
    "exclude_reason",
    "user_comment",
]

PRIORITY_VALUES = {"", "low", "medium", "high", "critical"}
BOOLEAN_TRUE = {"true", "yes", "y", "1", "included"}
BOOLEAN_FALSE = {"false", "no", "n", "0", "excluded"}
READ_STATUSES_WITH_NOTES = {ReadingStatus.READ.value, ReadingStatus.DEEPLY_READ.value}
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
REQUIRED_REGISTRY_HEADERS = {"paper_id", "title", "authors", "year"}


def normalize_doi(value: str) -> str:
    doi = (value or "").strip().lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    doi = doi.strip().strip("<>").rstrip(".")
    return doi


def looks_like_malformed_doi(value: str) -> bool:
    doi = normalize_doi(value)
    if not doi:
        return False
    return doi.startswith("10.") and DOI_RE.fullmatch(doi) is None


def normalize_title(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    normalized = normalized.lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def parse_authors(value: str | list[str] | list[Author] | None) -> list[Author]:
    if not value:
        return []
    if isinstance(value, list):
        result: list[Author] = []
        for item in value:
            if isinstance(item, Author):
                result.append(item)
            else:
                result.append(Author.from_string(str(item)))
        return result
    parts = [part.strip() for part in re.split(r"\s+and\s+|;", value) if part.strip()]
    return [Author.from_string(part) for part in parts]


def format_authors(authors: list[Author]) -> str:
    return "; ".join(author.bibtex_display() for author in authors if author.display())


def display_authors(authors: list[Author]) -> str:
    return "; ".join(author.display() for author in authors if author.display())


def validate_reading_status(value: str) -> str:
    normalized = (value or ReadingStatus.UNREAD.value).strip().lower().replace("-", "_")
    if normalized not in enum_values(ReadingStatus):
        raise ValueError(f"invalid reading status: {value}")
    return normalized


def parse_boolish(value: str) -> bool | None:
    normalized = (value or "").strip().lower()
    if not normalized:
        return None
    if normalized in BOOLEAN_TRUE:
        return True
    if normalized in BOOLEAN_FALSE:
        return False
    return None


def paper_from_row(row: dict[str, str]) -> Paper:
    return Paper(
        paper_id=(row.get("paper_id") or "").strip(),
        title=(row.get("title") or "").strip(),
        authors=parse_authors(row.get("authors", "")),
        year=(row.get("year") or "").strip(),
        journal=(row.get("journal") or "").strip(),
        doi=normalize_doi(row.get("doi", "")),
        url=(row.get("url") or "").strip(),
        local_pdf_path=(row.get("local_pdf_path") or "").strip(),
        bibtex_key=(row.get("bibtex_key") or "").strip(),
        tags=parse_tags(row.get("tags", "")),
        reading_status=(row.get("reading_status") or ReadingStatus.UNREAD.value).strip(),
        notes_path=(row.get("notes_path") or "").strip(),
        added_date=(row.get("added_date") or "").strip(),
        last_reviewed_date=(row.get("last_reviewed_date") or "").strip(),
        priority=(row.get("priority") or "").strip(),
        project=(row.get("project") or "").strip(),
        source_type=(row.get("source_type") or "").strip(),
        relevance_score=(row.get("relevance_score") or "").strip(),
        reading_priority=(row.get("reading_priority") or "").strip(),
        included_in_lit_review=(row.get("included_in_lit_review") or "").strip(),
        exclude_reason=(row.get("exclude_reason") or "").strip(),
        user_comment=(row.get("user_comment") or "").strip(),
    )


def paper_to_row(paper: Paper) -> dict[str, str]:
    return {
        "paper_id": paper.paper_id,
        "title": paper.title,
        "authors": format_authors(paper.authors),
        "year": str(paper.year),
        "journal": paper.journal,
        "doi": normalize_doi(paper.doi),
        "url": paper.url,
        "local_pdf_path": paper.local_pdf_path,
        "bibtex_key": paper.bibtex_key,
        "tags": format_tags(paper.tags),
        "reading_status": paper.reading_status,
        "notes_path": paper.notes_path,
        "added_date": paper.added_date,
        "last_reviewed_date": paper.last_reviewed_date,
        "priority": str(paper.priority),
        "project": paper.project,
        "source_type": paper.source_type,
        "relevance_score": str(paper.relevance_score),
        "reading_priority": str(paper.reading_priority),
        "included_in_lit_review": str(paper.included_in_lit_review),
        "exclude_reason": paper.exclude_reason,
        "user_comment": paper.user_comment,
    }


def create_empty_registry(path: str | Path) -> Path:
    target = Path(path)
    if target.exists():
        return target
    return write_csv_rows(target, [], REGISTRY_FIELDS)


def load_registry(path: str | Path) -> list[Paper]:
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(
            format_error_message(
                what="Registry CSV not found.",
                where=str(target),
                why="The registry loader cannot validate or report papers without a CSV file.",
                next_step="Run `paperwb init`, pass an existing --registry path, or use --project for a configured project.",
            )
        )
    return [paper_from_row(row) for row in read_csv_rows(target)]


def validate_registry_headers(path: str | Path) -> list[ValidationFinding]:
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(
            format_error_message(
                what="Registry CSV not found.",
                where=str(target),
                why="Header validation needs an existing CSV file.",
                next_step="Run `paperwb init`, pass an existing registry path, or create a CSV with the documented headers.",
            )
        )
    first_line = target.read_text(encoding="utf-8").splitlines()
    if not first_line:
        return [
            ValidationFinding(
                severity="error",
                code="missing_header",
                message=format_error_message(
                    what="Registry CSV is empty.",
                    where=str(target),
                    why="The registry loader needs a header row before it can validate paper records.",
                    next_step="Create the registry with `paperwb init` or add the documented registry columns.",
                ),
                identifier=str(target),
                suggestion="Add a header row with paper_id, title, authors, and year.",
            )
        ]
    headers = [header.strip() for header in first_line[0].split(",")]
    missing = sorted(REQUIRED_REGISTRY_HEADERS - set(headers))
    if not missing:
        return []
    return [
        ValidationFinding(
            severity="error",
            code="missing_required_column",
            message=format_error_message(
                what="Registry CSV is missing required columns.",
                where=str(target),
                why="Rows cannot be validated reliably when core fields are absent.",
                next_step=f"Add missing columns: {', '.join(missing)}.",
            ),
            identifier=str(target),
            suggestion="Use the registry schema documented in docs/REGISTRY_SCHEMA.md.",
        )
    ]


def save_registry(papers: list[Paper], path: str | Path) -> Path:
    return write_csv_rows(path, (paper_to_row(paper) for paper in papers), REGISTRY_FIELDS)


def save_registry_json(papers: list[Paper], path: str | Path, force: bool = True) -> Path:
    return write_json(path, [dataclass_to_plain(paper) for paper in papers], force=force)


def _slug_words(value: str, limit: int = 4) -> list[str]:
    words = normalize_title(value).split()
    stop = {"a", "an", "the", "and", "or", "of", "to", "in", "for", "on", "with"}
    return [word for word in words if word not in stop][:limit]


def generate_paper_id(title: str, authors: list[Author], year: str, existing_ids: set[str] | None = None) -> str:
    existing = existing_ids or set()
    first_author = "paper"
    if authors:
        first_author = normalize_title(authors[0].family or authors[0].raw_name or "paper").replace(" ", "")
    base_parts = [first_author or "paper", re.sub(r"\D", "", str(year))[:4] or "undated"]
    base_parts.extend(_slug_words(title, limit=3))
    base = "_".join(part for part in base_parts if part)
    candidate = base
    counter = 2
    while candidate in existing:
        candidate = f"{base}_{counter}"
        counter += 1
    return candidate


def add_paper(
    papers: list[Paper],
    *,
    title: str,
    authors: str | list[str] | list[Author] | None = None,
    year: str = "",
    journal: str = "",
    doi: str = "",
    url: str = "",
    local_pdf_path: str = "",
    bibtex_key: str = "",
    tags: str | list[str] | None = None,
    reading_status: str = ReadingStatus.UNREAD.value,
    notes_path: str = "",
    priority: str = "",
    project: str = "",
    source_type: str = "",
    relevance_score: str = "",
    reading_priority: str = "",
    included_in_lit_review: str = "",
    exclude_reason: str = "",
    user_comment: str = "",
    paper_id: str = "",
) -> Paper:
    parsed_authors = parse_authors(authors)
    existing_ids = {paper.paper_id for paper in papers}
    resolved_id = paper_id or generate_paper_id(title, parsed_authors, year, existing_ids)
    paper = Paper(
        paper_id=resolved_id,
        title=title.strip(),
        authors=parsed_authors,
        year=str(year).strip(),
        journal=journal.strip(),
        doi=normalize_doi(doi),
        url=url.strip(),
        local_pdf_path=local_pdf_path.strip(),
        bibtex_key=bibtex_key.strip(),
        tags=parse_tags(tags),
        reading_status=validate_reading_status(reading_status),
        notes_path=notes_path.strip(),
        added_date=date.today().isoformat(),
        priority=str(priority).strip(),
        project=project.strip(),
        source_type=source_type.strip(),
        relevance_score=str(relevance_score).strip(),
        reading_priority=str(reading_priority).strip(),
        included_in_lit_review=str(included_in_lit_review).strip(),
        exclude_reason=exclude_reason.strip(),
        user_comment=user_comment.strip(),
    )
    papers.append(paper)
    return paper


def filter_papers(
    papers: list[Paper],
    *,
    tag: str = "",
    year: str = "",
    journal: str = "",
    status: str = "",
    priority: str = "",
    author: str = "",
) -> list[Paper]:
    result = papers
    if tag:
        normalized = set(parse_tags(tag))
        result = [paper for paper in result if normalized.intersection(parse_tags(paper.tags))]
    if year:
        result = [paper for paper in result if str(paper.year) == str(year)]
    if journal:
        needle = journal.lower()
        result = [paper for paper in result if needle in paper.journal.lower()]
    if status:
        wanted = status.strip().lower().replace("-", "_")
        result = [paper for paper in result if paper.reading_status == wanted]
    if priority:
        result = [paper for paper in result if str(paper.priority) == str(priority)]
    if author:
        needle = author.lower()
        result = [paper for paper in result if needle in display_authors(paper.authors).lower()]
    return result


def validate_registry(
    papers: list[Paper],
    *,
    root: str | Path | None = None,
    claims: list[Claim] | None = None,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    root_path = Path(root) if root is not None else None
    claims_by_paper: dict[str, list[Claim]] = {}
    if claims is not None:
        for claim in claims:
            claims_by_paper.setdefault(claim.paper_id, []).append(claim)
    ids = _duplicate_groups([(paper.paper_id, paper.paper_id) for paper in papers])
    for paper_id, duplicate_ids in ids.items():
        findings.append(
            ValidationFinding(
                severity="error",
                code="duplicate_paper_id",
                message=f"Paper ID {paper_id!r} appears {len(duplicate_ids)} times.",
                identifier=paper_id,
                suggestion="Give each registry row a stable unique paper_id.",
            )
        )
    for paper in papers:
        required = {
            "paper_id": paper.paper_id,
            "title": paper.title,
            "authors": display_authors(paper.authors),
            "year": paper.year,
        }
        for field, value in required.items():
            if not str(value).strip():
                findings.append(
                    ValidationFinding(
                        severity="error",
                        code=f"missing_{field}",
                        message=f"{paper.paper_id or '<missing id>'} is missing {field}.",
                        identifier=paper.paper_id,
                        suggestion=f"Fill the {field} field in the registry.",
                    )
                )
        if paper.reading_status not in enum_values(ReadingStatus):
            findings.append(
                ValidationFinding(
                    severity="error",
                    code="invalid_reading_status",
                    message=f"{paper.paper_id} has invalid reading status {paper.reading_status!r}.",
                    identifier=paper.paper_id,
                    suggestion=f"Use one of: {', '.join(sorted(enum_values(ReadingStatus)))}.",
                )
            )
        if paper.year and not re.fullmatch(r"\d{4}", str(paper.year)):
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="invalid_year",
                    message=f"{paper.paper_id} has year {paper.year!r}; expected YYYY.",
                    identifier=paper.paper_id,
                    suggestion="Use a four-digit publication year when known.",
                )
            )
        if paper.priority.lower() not in PRIORITY_VALUES:
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="invalid_priority",
                    message=f"{paper.paper_id} has priority {paper.priority!r}.",
                    identifier=paper.paper_id,
                    suggestion=f"Use one of: {', '.join(sorted(value for value in PRIORITY_VALUES if value))}.",
                )
            )
        if paper.reading_priority.lower() not in PRIORITY_VALUES:
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="invalid_reading_priority",
                    message=f"{paper.paper_id} has reading_priority {paper.reading_priority!r}.",
                    identifier=paper.paper_id,
                    suggestion=f"Use one of: {', '.join(sorted(value for value in PRIORITY_VALUES if value))}.",
                )
            )
        if paper.source_type and paper.source_type not in enum_values(SourceType):
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="invalid_source_type",
                    message=f"{paper.paper_id} has source_type {paper.source_type!r}.",
                    identifier=paper.paper_id,
                    suggestion=f"Use one of: {', '.join(sorted(enum_values(SourceType)))}.",
                )
            )
        if paper.relevance_score:
            try:
                score = float(paper.relevance_score)
            except ValueError:
                findings.append(
                    ValidationFinding(
                        severity="warning",
                        code="invalid_relevance_score",
                        message=f"{paper.paper_id} has non-numeric relevance_score {paper.relevance_score!r}.",
                        identifier=paper.paper_id,
                        suggestion="Use a number from 0 to 5 or leave relevance_score blank.",
                    )
                )
            else:
                if score < 0 or score > 5:
                    findings.append(
                        ValidationFinding(
                            severity="warning",
                            code="invalid_relevance_score",
                            message=f"{paper.paper_id} has relevance_score {paper.relevance_score}; expected 0-5.",
                            identifier=paper.paper_id,
                            suggestion="Use a number from 0 to 5.",
                        )
                    )
        included = parse_boolish(paper.included_in_lit_review)
        if paper.included_in_lit_review and included is None:
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="invalid_included_in_lit_review",
                    message=f"{paper.paper_id} has included_in_lit_review {paper.included_in_lit_review!r}.",
                    identifier=paper.paper_id,
                    suggestion="Use true/false, yes/no, or leave blank.",
                )
            )
        if included is False and not paper.exclude_reason:
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="excluded_without_reason",
                    message=f"{paper.paper_id} is excluded from the literature review without an exclude_reason.",
                    identifier=paper.paper_id,
                    suggestion="Add exclude_reason so future audits understand the decision.",
                )
            )
        if included is True and claims is not None and not claims_by_paper.get(paper.paper_id):
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="included_without_claims",
                    message=f"{paper.paper_id} is included in the literature review but has no extracted claims.",
                    identifier=paper.paper_id,
                    suggestion="Add structured claims before using this paper as support.",
                )
            )
        if paper.reading_status in READ_STATUSES_WITH_NOTES and not paper.notes_path:
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="read_paper_missing_notes_path",
                    message=f"{paper.paper_id} is marked {paper.reading_status} but has no notes_path.",
                    identifier=paper.paper_id,
                    suggestion="Add notes_path or generate a note template.",
                )
            )
        if not paper.bibtex_key:
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="missing_bibtex_key",
                    message=f"{paper.paper_id} is not linked to a BibTeX key.",
                    identifier=paper.paper_id,
                    suggestion="Add bibtex_key once a citation entry is available.",
                )
            )
        if looks_like_malformed_doi(paper.doi):
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="malformed_doi",
                    message=f"{paper.paper_id} has DOI-like value {paper.doi!r} that does not match a common DOI pattern.",
                    identifier=paper.paper_id,
                    suggestion="Verify the DOI locally; do not guess or auto-correct.",
                )
            )
        if paper.local_pdf_path:
            pdf_path = Path(paper.local_pdf_path)
            if pdf_path.is_absolute():
                findings.append(
                    ValidationFinding(
                        severity="warning",
                        code="absolute_pdf_path",
                        message=f"{paper.paper_id} uses an absolute local_pdf_path.",
                        identifier=paper.paper_id,
                        suggestion="Prefer workspace-relative paths for portability.",
                    )
                )
            elif root_path is not None:
                resolved_pdf_path = (root_path / pdf_path).resolve(strict=False)
                try:
                    resolved_pdf_path.relative_to(root_path.resolve(strict=False))
                except ValueError:
                    findings.append(
                        ValidationFinding(
                            severity="error",
                            code="path_escapes_workspace",
                            message=f"{paper.paper_id} local_pdf_path escapes the workspace: {paper.local_pdf_path}.",
                            identifier=paper.paper_id,
                            suggestion="Use a path inside the selected workspace or leave local_pdf_path blank.",
                        )
                    )
                else:
                    if not resolved_pdf_path.exists():
                        findings.append(
                            ValidationFinding(
                                severity="warning",
                                code="missing_local_pdf_path",
                                message=f"{paper.paper_id} local_pdf_path does not exist: {paper.local_pdf_path}.",
                                identifier=paper.paper_id,
                                suggestion="Fix the path or leave local_pdf_path blank; do not download copyrighted PDFs.",
                            )
                        )
        if root_path is not None and paper.notes_path:
            notes_path = Path(paper.notes_path)
            resolved_notes_path = (root_path / notes_path).resolve(strict=False) if not notes_path.is_absolute() else notes_path.resolve(strict=False)
            if notes_path.is_absolute():
                findings.append(
                    ValidationFinding(
                        severity="warning",
                        code="absolute_notes_path",
                        message=f"{paper.paper_id} uses an absolute notes_path.",
                        identifier=paper.paper_id,
                        suggestion="Prefer workspace-relative notes_path values for portability.",
                    )
                )
                if not resolved_notes_path.exists():
                    findings.append(
                        ValidationFinding(
                            severity="warning",
                            code="notes_path_missing_file",
                            message=f"{paper.paper_id} notes_path does not exist: {paper.notes_path}.",
                            identifier=paper.paper_id,
                            suggestion="Generate the note file or correct notes_path.",
                        )
                    )
            else:
                try:
                    resolved_notes_path.relative_to(root_path.resolve(strict=False))
                except ValueError:
                    findings.append(
                        ValidationFinding(
                            severity="error",
                            code="path_escapes_workspace",
                            message=f"{paper.paper_id} notes_path escapes the workspace: {paper.notes_path}.",
                            identifier=paper.paper_id,
                            suggestion="Use a notes_path inside the selected workspace.",
                        )
                    )
                else:
                    if not resolved_notes_path.exists() and not Path(paper.notes_path).exists():
                        findings.append(
                            ValidationFinding(
                                severity="warning",
                                code="notes_path_missing_file",
                                message=f"{paper.paper_id} notes_path does not exist: {paper.notes_path}.",
                                identifier=paper.paper_id,
                                suggestion="Generate the note file or correct notes_path.",
                            )
                        )
    for doi, paper_ids in detect_duplicate_doi(papers).items():
        findings.append(
            ValidationFinding(
                severity="error",
                code="duplicate_doi",
                message=f"DOI {doi} appears in papers: {', '.join(paper_ids)}.",
                identifier=doi,
                suggestion="Merge duplicate records or correct the DOI.",
            )
        )
    for title, paper_ids in detect_duplicate_title(papers).items():
        findings.append(
            ValidationFinding(
                severity="warning",
                code="duplicate_title",
                message=f"Normalized title {title!r} appears in papers: {', '.join(paper_ids)}.",
                identifier=title,
                suggestion="Confirm whether these rows represent the same paper.",
            )
        )
    for key, paper_ids in detect_duplicate_bibtex_keys(papers).items():
        findings.append(
            ValidationFinding(
                severity="error",
                code="duplicate_bibtex_key",
                message=f"BibTeX key {key!r} is used by papers: {', '.join(paper_ids)}.",
                identifier=key,
                suggestion="Use one unique BibTeX key per paper.",
            )
        )
    return findings


def _duplicate_groups(pairs: list[tuple[str, str]], skip_empty: bool = True) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for identifier, value in pairs:
        if skip_empty and not value:
            continue
        grouped[value].append(identifier)
    return {value: ids for value, ids in grouped.items() if len(ids) > 1}


def detect_duplicate_doi(papers: list[Paper]) -> dict[str, list[str]]:
    return _duplicate_groups([(paper.paper_id, normalize_doi(paper.doi)) for paper in papers])


def detect_duplicate_title(papers: list[Paper]) -> dict[str, list[str]]:
    return _duplicate_groups([(paper.paper_id, normalize_title(paper.title)) for paper in papers])


def detect_duplicate_bibtex_keys(papers: list[Paper]) -> dict[str, list[str]]:
    return _duplicate_groups([(paper.paper_id, paper.bibtex_key.strip()) for paper in papers])


def registry_to_json(papers: list[Paper]) -> str:
    return json.dumps([dataclass_to_plain(paper) for paper in papers], indent=2, ensure_ascii=False)
