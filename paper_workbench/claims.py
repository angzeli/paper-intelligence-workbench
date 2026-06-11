"""Claim extraction and evidence-link helpers."""

from __future__ import annotations

from pathlib import Path

from .io import write_csv_rows
from .notes import parse_note_file
from .schema import Claim, EvidenceLink, PaperNote
from .tags import format_tags


CLAIM_FIELDS = [
    "claim_id",
    "paper_id",
    "claim_text",
    "evidence_type",
    "section",
    "page",
    "confidence",
    "tags",
    "quote_or_paraphrase",
    "user_comment",
    "supports_theme",
    "strength",
    "note_file",
]


def portable_note_path(value: str, *, root: str | Path | None = None) -> str:
    if not value:
        return ""
    path = Path(value)
    if not path.is_absolute():
        return path.as_posix()
    bases = [Path(root)] if root is not None else []
    bases.append(Path.cwd())
    for base in bases:
        try:
            return path.resolve(strict=False).relative_to(base.resolve(strict=False)).as_posix()
        except ValueError:
            continue
    return path.name


def claim_to_row(claim: Claim, *, root: str | Path | None = None) -> dict[str, str]:
    return {
        "claim_id": claim.claim_id,
        "paper_id": claim.paper_id,
        "claim_text": claim.claim_text,
        "evidence_type": claim.evidence_type,
        "section": claim.section,
        "page": claim.page,
        "confidence": claim.confidence,
        "tags": format_tags(claim.tags),
        "quote_or_paraphrase": claim.quote_or_paraphrase,
        "user_comment": claim.user_comment,
        "supports_theme": claim.supports_theme,
        "strength": claim.strength,
        "note_file": portable_note_path(claim.note_file, root=root),
    }


def collect_notes(path: str | Path) -> list[PaperNote]:
    target = Path(path)
    if target.is_file():
        return [parse_note_file(target)]
    return [parse_note_file(note_path) for note_path in sorted(target.glob("*.md"))]


def collect_claims(path: str | Path) -> list[Claim]:
    claims: list[Claim] = []
    for note in collect_notes(path):
        claims.extend(note.claims)
    return claims


def save_claims_csv(claims: list[Claim], path: str | Path, force: bool = True, *, root: str | Path | None = None) -> Path:
    return write_csv_rows(path, (claim_to_row(claim, root=root) for claim in claims), CLAIM_FIELDS, force=force)


def evidence_links_from_claims(claims: list[Claim]) -> list[EvidenceLink]:
    links: list[EvidenceLink] = []
    for claim in claims:
        links.append(
            EvidenceLink(
                claim_id=claim.claim_id,
                paper_id=claim.paper_id,
                location=claim.section or claim.page,
                evidence_type=claim.evidence_type,
                quote_or_paraphrase=claim.quote_or_paraphrase,
                confidence=claim.confidence,
                note_file=claim.note_file,
            )
        )
    return links
