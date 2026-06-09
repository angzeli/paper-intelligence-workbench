"""Paper registry loading, saving, filtering, and validation."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
import json
from pathlib import Path
import re
import unicodedata

from .io import read_csv_rows, write_csv_rows, write_json
from .schema import Author, Paper, ReadingStatus, ValidationFinding, dataclass_to_plain, enum_values
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
    "user_comment",
]


def normalize_doi(value: str) -> str:
    doi = (value or "").strip().lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    doi = doi.strip().rstrip(".")
    return doi


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
        raise FileNotFoundError(target)
    return [paper_from_row(row) for row in read_csv_rows(target)]


def save_registry(papers: list[Paper], path: str | Path) -> Path:
    return write_csv_rows(path, (paper_to_row(paper) for paper in papers), REGISTRY_FIELDS)


def save_registry_json(papers: list[Paper], path: str | Path) -> Path:
    return write_json(path, [dataclass_to_plain(paper) for paper in papers])


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


def validate_registry(papers: list[Paper]) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
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
        if paper.local_pdf_path and Path(paper.local_pdf_path).is_absolute():
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="absolute_pdf_path",
                    message=f"{paper.paper_id} uses an absolute local_pdf_path.",
                    identifier=paper.paper_id,
                    suggestion="Prefer workspace-relative paths for portability.",
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


def registry_to_json(papers: list[Paper]) -> str:
    return json.dumps([dataclass_to_plain(paper) for paper in papers], indent=2, ensure_ascii=False)
