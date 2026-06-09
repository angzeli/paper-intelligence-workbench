"""Simple local substring search over registry, notes, and claims."""

from __future__ import annotations

from pathlib import Path

from .claims import collect_claims
from .io import read_text
from .registry import display_authors
from .schema import Claim, Paper
from .tags import format_tags


def _contains(value: str, query: str) -> bool:
    return query.lower() in value.lower()


def search_papers(papers: list[Paper], query: str) -> list[dict[str, str]]:
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
        if _contains(haystack, query):
            results.append({"kind": "paper", "id": paper.paper_id, "title": paper.title, "path": ""})
    return results


def search_claims(claims: list[Claim], query: str) -> list[dict[str, str]]:
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
        if _contains(haystack, query):
            results.append({"kind": "claim", "id": claim.claim_id, "title": claim.claim_text, "path": claim.note_file})
    return results


def search_note_files(notes_path: str | Path, query: str) -> list[dict[str, str]]:
    target = Path(notes_path)
    note_paths = [target] if target.is_file() else sorted(target.glob("*.md"))
    results: list[dict[str, str]] = []
    for note_path in note_paths:
        body = read_text(note_path)
        if _contains(body, query):
            first_line = body.splitlines()[0] if body.splitlines() else note_path.name
            results.append({"kind": "note", "id": note_path.stem, "title": first_line, "path": str(note_path)})
    return results


def search_notes_claims(notes_path: str | Path, query: str) -> list[dict[str, str]]:
    return search_claims(collect_claims(notes_path), query)
