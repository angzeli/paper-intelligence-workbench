"""Structured Markdown paper note templates and parsing."""

from __future__ import annotations

from pathlib import Path
import re

from .io import read_text, write_text
from .registry import normalize_title
from .schema import Claim, ClaimStrength, EvidenceType, Paper, PaperNote, ReadingStatus, enum_values
from .tags import format_tags, parse_tags


HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.MULTILINE)
BULLET_FIELD_RE = re.compile(r"^\s*-\s*([^:]+):\s*(.*)$")


def _safe_filename(value: str) -> str:
    slug = normalize_title(value).replace(" ", "_")
    return slug[:80] or "paper_note"


def render_note_template(paper: Paper) -> str:
    title = paper.title or paper.paper_id
    return f"""# Paper Note: {title}

## Metadata
- Paper ID: {paper.paper_id}
- BibTeX key: {paper.bibtex_key}
- DOI: {paper.doi}
- Year: {paper.year}
- Journal: {paper.journal}
- Tags: {format_tags(paper.tags)}
- Reading status: {paper.reading_status}

## One-sentence summary


## Why this paper matters


## Research question or problem


## Method / approach


## Key findings


## Limitations


## Useful for my literature review


## Not useful for


## Claims and evidence

### Claim 1
- Claim:
- Evidence type:
- Section / page:
- Quote or paraphrase:
- Confidence:
- Tags:
- User comment:
- Strength:
- Supports theme:

## Open questions


## Follow-up actions

"""


def write_note_template(
    paper: Paper,
    notes_dir: str | Path = "data/notes",
    output_path: str | Path | None = None,
    force: bool = False,
) -> Path:
    if output_path:
        target = Path(output_path)
    else:
        filename = f"{paper.paper_id or _safe_filename(paper.title)}.md"
        target = Path(notes_dir) / filename
    return write_text(target, render_note_template(paper), force=force)


def _section_map(markdown: str) -> dict[str, str]:
    matches = list(HEADING_RE.finditer(markdown))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        title = match.group(2).strip().lower()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections[title] = markdown[start:end].strip()
    return sections


def _parse_bullet_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_label = ""
    for line in block.splitlines():
        match = BULLET_FIELD_RE.match(line)
        if match:
            current_label = match.group(1).strip().lower()
            fields[current_label] = match.group(2).strip()
        elif current_label and line.strip():
            fields[current_label] = (fields[current_label] + " " + line.strip()).strip()
    return fields


def _plain_section(sections: dict[str, str], title: str) -> str:
    return re.sub(r"\n{2,}", "\n", sections.get(title, "").strip())


def _list_section(sections: dict[str, str], title: str) -> list[str]:
    text = sections.get(title, "")
    values: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            values.append(stripped[2:].strip())
        elif stripped:
            values.append(stripped)
    return values


def _split_location(value: str) -> tuple[str, str]:
    section = value.strip()
    page = ""
    page_match = re.search(r"(?:page|p\.?|pp\.)\s*([0-9ivxIVX,-]+)", value)
    if page_match:
        page = page_match.group(1)
    return section, page


def _normalize_evidence_type(value: str, warnings: list[str]) -> str:
    normalized = (value or EvidenceType.UNCLEAR.value).strip().lower().replace("-", "_").replace(" ", "_")
    if normalized not in enum_values(EvidenceType):
        warnings.append(f"Unknown evidence type {value!r}; using unclear.")
        return EvidenceType.UNCLEAR.value
    return normalized


def _normalize_strength(value: str, warnings: list[str]) -> str:
    normalized = (value or ClaimStrength.WEAK.value).strip().lower().replace("-", "_").replace(" ", "_")
    if normalized not in enum_values(ClaimStrength):
        warnings.append(f"Unknown claim strength {value!r}; using weak.")
        return ClaimStrength.WEAK.value
    return normalized


def _normalize_status(value: str, warnings: list[str]) -> str:
    normalized = (value or ReadingStatus.UNREAD.value).strip().lower().replace("-", "_").replace(" ", "_")
    if normalized not in enum_values(ReadingStatus):
        warnings.append(f"Unknown reading status {value!r}; using unread.")
        return ReadingStatus.UNREAD.value
    return normalized


def parse_note(markdown: str, source_path: str = "") -> PaperNote:
    sections = _section_map(markdown)
    warnings: list[str] = []
    metadata = _parse_bullet_fields(sections.get("metadata", ""))
    paper_id = metadata.get("paper id", "")
    citation_key = metadata.get("bibtex key", "")
    if not paper_id:
        warnings.append("Metadata is missing Paper ID.")
    note = PaperNote(
        paper_id=paper_id,
        citation_key=citation_key,
        reading_status=_normalize_status(metadata.get("reading status", ""), warnings),
        one_sentence_summary=_plain_section(sections, "one-sentence summary"),
        research_question=_plain_section(sections, "research question or problem"),
        methods=_plain_section(sections, "method / approach"),
        key_findings=_plain_section(sections, "key findings"),
        limitations=_plain_section(sections, "limitations"),
        useful_for=_plain_section(sections, "useful for my literature review"),
        not_useful_for=_plain_section(sections, "not useful for"),
        tags=parse_tags(metadata.get("tags", "")),
        user_questions=_list_section(sections, "open questions"),
        follow_up_actions=_list_section(sections, "follow-up actions"),
        warnings=warnings,
        source_path=source_path,
    )
    note.claims = _parse_claims(markdown, note, warnings)
    return note


def parse_note_file(path: str | Path) -> PaperNote:
    target = Path(path)
    return parse_note(read_text(target), source_path=str(target))


def _parse_claims(markdown: str, note: PaperNote, warnings: list[str]) -> list[Claim]:
    claim_heading_re = re.compile(r"^###\s+Claim\s+([A-Za-z0-9_-]+).*?$", re.MULTILINE)
    matches = list(claim_heading_re.finditer(markdown))
    claims: list[Claim] = []
    for index, match in enumerate(matches):
        ordinal = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        block = markdown[start:end]
        fields = _parse_bullet_fields(block)
        claim_text = fields.get("claim", "").strip()
        if not claim_text:
            warnings.append(f"Claim {ordinal} is missing claim text.")
            continue
        location = fields.get("section / page", "")
        section, page = _split_location(location)
        if not location.strip():
            warnings.append(f"Claim {ordinal} is missing evidence location.")
        claim_tags = parse_tags(fields.get("tags", "")) or list(note.tags)
        claim_id = f"{note.paper_id or 'unknown'}:c{len(claims) + 1}"
        claims.append(
            Claim(
                claim_id=claim_id,
                paper_id=note.paper_id,
                claim_text=claim_text,
                evidence_type=_normalize_evidence_type(fields.get("evidence type", ""), warnings),
                section=section,
                page=page,
                confidence=fields.get("confidence", ""),
                tags=claim_tags,
                quote_or_paraphrase=fields.get("quote or paraphrase", ""),
                user_comment=fields.get("user comment", ""),
                supports_theme=fields.get("supports theme", ""),
                strength=_normalize_strength(fields.get("strength", ""), warnings),
                note_file=note.source_path,
            )
        )
    return claims
