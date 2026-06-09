"""Lightweight BibTeX parsing and validation."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re

from .io import read_text
from .registry import normalize_doi
from .schema import Author, BibTeXEntry, Paper, ValidationFinding


ENTRY_RE = re.compile(r"@([A-Za-z]+)\s*([({])", re.MULTILINE)
FIELD_NAME_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")
VENUE_BY_TYPE = {
    "article": ("journal",),
    "inproceedings": ("booktitle",),
    "conference": ("booktitle",),
    "proceedings": ("title", "publisher"),
    "book": ("publisher",),
    "inbook": ("publisher",),
    "thesis": ("school", "institution"),
    "phdthesis": ("school",),
    "mastersthesis": ("school",),
    "unpublished": ("note",),
    "misc": ("howpublished", "url", "note"),
}
REQUIRED_FIELDS_BY_TYPE = {
    "article": ("title", "author", "year", "journal"),
    "book": ("title", "author", "year", "publisher"),
    "inproceedings": ("title", "author", "year", "booktitle"),
    "conference": ("title", "author", "year", "booktitle"),
    "thesis": ("title", "author", "year"),
    "phdthesis": ("title", "author", "year", "school"),
    "mastersthesis": ("title", "author", "year", "school"),
    "unpublished": ("title", "author", "year", "note"),
    "misc": ("title",),
}
INCONSISTENT_FIELD_SUGGESTIONS = {
    "journaltitle": "journal",
    "date": "year",
    "authors": "author",
    "urls": "url",
    "link": "url",
    "publication": "journal",
}


def clean_bibtex_value(value: str) -> str:
    text = value.strip()
    while len(text) >= 2 and ((text[0] == "{" and text[-1] == "}") or (text[0] == '"' and text[-1] == '"')):
        text = text[1:-1].strip()
    text = text.replace("\\&", "&")
    text = re.sub(r"\s+", " ", text)
    return text


def _matching_close(open_char: str) -> str:
    return "}" if open_char == "{" else ")"


def _find_entry_end(text: str, start: int, open_char: str) -> int:
    close_char = _matching_close(open_char)
    depth = 0
    in_quote = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_quote = not in_quote
        if in_quote:
            continue
        if char == open_char:
            depth += 1
        elif char == close_char:
            depth -= 1
            if depth == 0:
                return index
    return -1


def _parse_value(text: str, start: int) -> tuple[str, int]:
    index = start
    while index < len(text) and text[index].isspace():
        index += 1
    if index >= len(text):
        return "", index
    if text[index] == "{":
        end = _find_balanced_brace(text, index)
        if end == -1:
            return text[index:].strip(), len(text)
        return text[index : end + 1], end + 1
    if text[index] == '"':
        index += 1
        value: list[str] = ['"']
        escaped = False
        while index < len(text):
            char = text[index]
            value.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                return "".join(value), index + 1
            index += 1
        return "".join(value), index
    start_index = index
    while index < len(text) and text[index] != ",":
        index += 1
    return text[start_index:index].strip(), index


def _find_balanced_brace(text: str, start: int) -> int:
    depth = 0
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return -1


def _parse_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    index = 0
    while index < len(body):
        while index < len(body) and body[index] in ", \n\r\t":
            index += 1
        match = FIELD_NAME_RE.match(body, index)
        if not match:
            index += 1
            continue
        name = match.group(0).lower()
        index = match.end()
        while index < len(body) and body[index].isspace():
            index += 1
        if index >= len(body) or body[index] != "=":
            continue
        index += 1
        value, index = _parse_value(body, index)
        fields[name] = clean_bibtex_value(value)
        while index < len(body) and body[index] != ",":
            index += 1
        if index < len(body) and body[index] == ",":
            index += 1
    return fields


def parse_bibtex(text: str, source_path: str = "") -> list[BibTeXEntry]:
    entries: list[BibTeXEntry] = []
    position = 0
    while True:
        match = ENTRY_RE.search(text, position)
        if not match:
            break
        entry_type = match.group(1).lower()
        open_char = match.group(2)
        body_start = match.end()
        body_end = _find_entry_end(text, match.end() - 1, open_char)
        if body_end == -1:
            entries.append(
                BibTeXEntry(
                    entry_type=entry_type,
                    key="",
                    source_path=source_path,
                    parse_warnings=[f"Could not find closing delimiter for @{entry_type} entry."],
                )
            )
            break
        raw_body = text[body_start:body_end]
        if "," not in raw_body:
            entries.append(
                BibTeXEntry(
                    entry_type=entry_type,
                    key=raw_body.strip(),
                    source_path=source_path,
                    parse_warnings=[f"Could not parse fields for @{entry_type} entry."],
                )
            )
            position = body_end + 1
            continue
        key, fields_body = raw_body.split(",", 1)
        fields = _parse_fields(fields_body)
        authors = [Author.from_string(part) for part in re.split(r"\s+and\s+", fields.get("author", "")) if part.strip()]
        entries.append(
            BibTeXEntry(
                entry_type=entry_type,
                key=key.strip(),
                title=fields.get("title", ""),
                authors=authors,
                year=fields.get("year", ""),
                journal=fields.get("journal", ""),
                doi=normalize_doi(fields.get("doi", "")),
                url=fields.get("url", ""),
                raw_fields=fields,
                source_path=source_path,
                parse_warnings=[],
            )
        )
        position = body_end + 1
    return entries


def parse_bibtex_file(path: str | Path) -> list[BibTeXEntry]:
    target = Path(path)
    return parse_bibtex(read_text(target), source_path=str(target))


def _duplicate_groups(entries: list[BibTeXEntry], attr: str) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        value = getattr(entry, attr)
        if value:
            grouped[value].append(entry.key)
    return {value: keys for value, keys in grouped.items() if len(keys) > 1}


def _title_capitalization_warning(title: str) -> bool:
    words = [word for word in re.findall(r"[A-Za-z]{4,}", title) if not word.isupper()]
    if not words:
        return False
    uppercase_words = [word for word in words if word[:1].isupper()]
    return len(uppercase_words) <= 1 and len(words) >= 4


def validate_bibtex(entries: list[BibTeXEntry], registry_papers: list[Paper] | None = None) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    for key, duplicate_keys in _duplicate_groups(entries, "key").items():
        findings.append(
            ValidationFinding(
                severity="error",
                code="duplicate_bibtex_key",
                message=f"BibTeX key {key!r} appears {len(duplicate_keys)} times.",
                identifier=key,
                suggestion="Use one unique key per BibTeX entry.",
            )
        )
    for doi, keys in _duplicate_groups(entries, "doi").items():
        findings.append(
            ValidationFinding(
                severity="error",
                code="duplicate_bibtex_doi",
                message=f"DOI {doi} appears in BibTeX keys: {', '.join(keys)}.",
                identifier=doi,
                suggestion="Confirm whether these entries are duplicates.",
            )
        )
    for entry in entries:
        for warning in entry.parse_warnings:
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="bibtex_parse_warning",
                    message=warning,
                    source=entry.source_path,
                    identifier=entry.key,
                    suggestion="Review the surrounding BibTeX manually; the parser is conservative.",
                )
            )
        if not entry.key:
            findings.append(
                ValidationFinding("error", "missing_key", "A BibTeX entry is missing its key.", entry.source_path)
            )
        required_fields = REQUIRED_FIELDS_BY_TYPE.get(entry.entry_type, ("title", "author", "year"))
        for field in required_fields:
            if field == "author":
                value = " and ".join(author.display() for author in entry.authors)
            elif field == "title":
                value = entry.title
            elif field == "year":
                value = entry.year
            else:
                value = entry.raw_fields.get(field, "")
            if not str(value).strip():
                findings.append(
                    ValidationFinding(
                        severity="error",
                        code=f"missing_{field}",
                        message=f"{entry.key or '<missing key>'} is missing {field}.",
                        source=entry.source_path,
                        identifier=entry.key,
                        suggestion=f"Add the {field} field if known.",
                    )
                )
        expected_venue_fields = VENUE_BY_TYPE.get(entry.entry_type, ("journal", "booktitle", "publisher"))
        if not any(entry.raw_fields.get(field, "") for field in expected_venue_fields):
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="missing_venue",
                    message=f"{entry.key} is missing expected venue field(s): {', '.join(expected_venue_fields)}.",
                    source=entry.source_path,
                    identifier=entry.key,
                    suggestion="Add journal, booktitle, publisher, school, or venue data when available.",
                )
            )
        for field, value in entry.raw_fields.items():
            if not value:
                findings.append(
                    ValidationFinding(
                        severity="warning",
                        code="empty_field",
                        message=f"{entry.key} has an empty {field} field.",
                        source=entry.source_path,
                        identifier=entry.key,
                        suggestion="Remove empty fields or fill them with user-verified data.",
                    )
                )
            if field in INCONSISTENT_FIELD_SUGGESTIONS:
                suggested = INCONSISTENT_FIELD_SUGGESTIONS[field]
                findings.append(
                    ValidationFinding(
                        severity="warning",
                        code="inconsistent_field_name",
                        message=f"{entry.key} uses {field}; expected {suggested}.",
                        source=entry.source_path,
                        identifier=entry.key,
                        suggestion=f"Consider renaming {field} to {suggested}.",
                    )
                )
        if entry.year and not re.fullmatch(r"\d{4}", entry.year):
            findings.append(
                ValidationFinding(
                    severity="error",
                    code="invalid_year",
                    message=f"{entry.key} has invalid year {entry.year!r}; expected YYYY.",
                    source=entry.source_path,
                    identifier=entry.key,
                    suggestion="Use a four-digit publication year.",
                )
            )
        if entry.entry_type in {"article", "inproceedings", "conference"} and not entry.doi:
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="missing_doi",
                    message=f"{entry.key} has no DOI.",
                    source=entry.source_path,
                    identifier=entry.key,
                    suggestion="Add a DOI only if you have verified one locally.",
                )
            )
        if entry.title and _title_capitalization_warning(entry.title):
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="title_capitalization",
                    message=f"{entry.key} title may have unprotected capitalization.",
                    source=entry.source_path,
                    identifier=entry.key,
                    suggestion="Protect proper nouns with braces if needed; do not guess.",
                )
            )
        if len([value for value in (entry.title, entry.year, entry.venue()) if value]) <= 2:
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="suspiciously_incomplete",
                    message=f"{entry.key} looks sparse.",
                    source=entry.source_path,
                    identifier=entry.key,
                    suggestion="Review the entry for missing author, venue, DOI, or URL fields.",
                )
            )
    if registry_papers is not None:
        registry_keys = {paper.bibtex_key for paper in registry_papers if paper.bibtex_key}
        entry_keys = {entry.key for entry in entries if entry.key}
        for entry_key in sorted(entry_keys - registry_keys):
            findings.append(
                ValidationFinding(
                    severity="warning",
                    code="bibtex_not_linked_to_registry",
                    message=f"BibTeX entry {entry_key} is not linked to any registry paper.",
                    identifier=entry_key,
                    suggestion="Add the key to a paper row or keep it as an intentional extra reference.",
                )
            )
        for paper in registry_papers:
            if not paper.bibtex_key:
                findings.append(
                    ValidationFinding(
                        severity="warning",
                        code="registry_missing_bibtex_key",
                        message=f"{paper.paper_id} has no BibTeX key.",
                        identifier=paper.paper_id,
                        suggestion="Link the paper to a verified BibTeX entry when available.",
                    )
                )
            elif paper.bibtex_key not in entry_keys:
                findings.append(
                    ValidationFinding(
                        severity="error",
                        code="registry_bibtex_key_missing_from_library",
                        message=f"{paper.paper_id} references missing BibTeX key {paper.bibtex_key}.",
                        identifier=paper.paper_id,
                        suggestion="Add the BibTeX entry or correct the registry bibtex_key.",
                    )
                )
    return findings
