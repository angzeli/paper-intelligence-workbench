"""Simple local substring search over registry, notes, and claims."""

from __future__ import annotations

import os
from pathlib import Path

from .claims import collect_claims
from .io import read_text
from .registry import display_authors
from .schema import Claim, Paper
from .tags import format_tags


def _contains(value: str, query: str, exact: bool = False) -> bool:
    haystack = value.lower()
    needle = query.lower()
    if exact:
        return needle in haystack
    return all(part in haystack for part in needle.split())


def search_papers(papers: list[Paper], query: str, *, exact: bool = False) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for paper in papers:
        haystack = " ".join(
            [
                paper.paper_id,
                paper.title,
                display_authors(paper.authors),
                paper.year,
                paper.journal,
                paper.doi,
                paper.bibtex_key,
                format_tags(paper.tags),
                paper.user_comment,
            ]
        )
        if _contains(haystack, query, exact=exact):
            results.append({"kind": "paper", "id": paper.paper_id, "title": paper.title, "path": ""})
    return results


def search_claims(claims: list[Claim], query: str, *, exact: bool = False) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for claim in claims:
        haystack = " ".join(
            [
                claim.claim_id,
                claim.paper_id,
                claim.claim_text,
                claim.evidence_type,
                claim.section,
                claim.quote_or_paraphrase,
                claim.user_comment,
                format_tags(claim.tags),
                claim.supports_theme,
            ]
        )
        if _contains(haystack, query, exact=exact):
            results.append({"kind": "claim", "id": claim.claim_id, "title": claim.claim_text, "path": claim.note_file})
    return results


def search_note_files(notes_path: str | Path, query: str, *, exact: bool = False) -> list[dict[str, str]]:
    target = Path(notes_path)
    note_paths = [target] if target.is_file() else sorted(target.glob("*.md"))
    results: list[dict[str, str]] = []
    for note_path in note_paths:
        body = read_text(note_path)
        if _contains(body, query, exact=exact):
            first_line = body.splitlines()[0] if body.splitlines() else note_path.name
            results.append({"kind": "note", "id": note_path.stem, "title": first_line, "path": str(note_path)})
    return results


def search_notes_claims(notes_path: str | Path, query: str, *, exact: bool = False) -> list[dict[str, str]]:
    return search_claims(collect_claims(notes_path), query, exact=exact)


def _display_path(path: str | Path, *, base_path: str | Path | None = None) -> str:
    if not path:
        return ""
    target = Path(path)
    base = Path(base_path) if base_path is not None else Path.cwd()
    try:
        if target.is_absolute():
            return target.relative_to(base.resolve()).as_posix()
    except ValueError:
        pass
    try:
        return Path(os.path.relpath(target, start=base)).as_posix()
    except (OSError, ValueError):
        return target.as_posix()


def results_markdown(results: list[dict[str, str]], query: str, *, base_path: str | Path | None = None) -> str:
    lines = [f"# Search Results: {query}", "", "| Kind | ID | Title | Path |", "| --- | --- | --- | --- |"]
    for result in results:
        title = result.get("title", "").replace("|", "\\|")
        path = _display_path(result.get("path", ""), base_path=base_path)
        lines.append(
            f"| {result.get('kind', '')} | {result.get('id', '')} | {title} | {path} |"
        )
    if not results:
        lines.append("| none |  | No matches. |  |")
    return "\n".join(lines) + "\n"
