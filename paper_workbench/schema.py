"""Core dataclasses and controlled vocabularies."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReadingStatus(str, Enum):
    UNREAD = "unread"
    SKIMMED = "skimmed"
    PARTIALLY_READ = "partially_read"
    READ = "read"
    DEEPLY_READ = "deeply_read"
    ARCHIVED = "archived"


class ClaimStrength(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    SPECULATIVE = "speculative"


class EvidenceType(str, Enum):
    EXPERIMENTAL_RESULT = "experimental_result"
    REVIEW_STATEMENT = "review_statement"
    METHOD_DESCRIPTION = "method_description"
    THEORY_OR_MECHANISM = "theory_or_mechanism"
    LIMITATION = "limitation"
    BACKGROUND_CONTEXT = "background_context"
    OPINION_OR_INTERPRETATION = "opinion_or_interpretation"
    UNCLEAR = "unclear"


class SourceType(str, Enum):
    JOURNAL_ARTICLE = "journal_article"
    CONFERENCE_PAPER = "conference_paper"
    BOOK = "book"
    THESIS = "thesis"
    PREPRINT = "preprint"
    REPORT = "report"
    REVIEW = "review"
    DATASET = "dataset"
    OTHER = "other"


@dataclass(slots=True)
class Author:
    given: str = ""
    family: str = ""
    raw_name: str = ""

    @classmethod
    def from_string(cls, value: str) -> "Author":
        raw = value.strip()
        if not raw:
            return cls()
        if "," in raw:
            family, given = [part.strip() for part in raw.split(",", 1)]
            return cls(given=given, family=family, raw_name=raw)
        parts = raw.split()
        if len(parts) == 1:
            return cls(family=parts[0], raw_name=raw)
        return cls(given=" ".join(parts[:-1]), family=parts[-1], raw_name=raw)

    def display(self) -> str:
        if self.given and self.family:
            return f"{self.given} {self.family}"
        return self.raw_name or self.family or self.given

    def bibtex_display(self) -> str:
        if self.family and self.given:
            return f"{self.family}, {self.given}"
        return self.raw_name or self.display()


@dataclass(slots=True)
class Paper:
    paper_id: str
    title: str
    authors: list[Author] = field(default_factory=list)
    year: str = ""
    journal: str = ""
    doi: str = ""
    url: str = ""
    local_pdf_path: str = ""
    bibtex_key: str = ""
    tags: list[str] = field(default_factory=list)
    reading_status: str = ReadingStatus.UNREAD.value
    notes_path: str = ""
    added_date: str = ""
    last_reviewed_date: str = ""
    priority: str = ""
    project: str = ""
    source_type: str = ""
    relevance_score: str = ""
    reading_priority: str = ""
    included_in_lit_review: str = ""
    exclude_reason: str = ""
    user_comment: str = ""


@dataclass(slots=True)
class BibTeXEntry:
    entry_type: str
    key: str
    title: str = ""
    authors: list[Author] = field(default_factory=list)
    year: str = ""
    journal: str = ""
    doi: str = ""
    url: str = ""
    raw_fields: dict[str, str] = field(default_factory=dict)
    source_path: str = ""
    parse_warnings: list[str] = field(default_factory=list)

    def venue(self) -> str:
        for name in ("journal", "booktitle", "publisher", "venue"):
            value = self.raw_fields.get(name, "")
            if value:
                return value
        return self.journal


@dataclass(slots=True)
class Claim:
    claim_id: str
    paper_id: str
    claim_text: str
    evidence_type: str = EvidenceType.UNCLEAR.value
    section: str = ""
    page: str = ""
    confidence: str = ""
    tags: list[str] = field(default_factory=list)
    quote_or_paraphrase: str = ""
    user_comment: str = ""
    supports_theme: str = ""
    strength: str = ClaimStrength.WEAK.value
    note_file: str = ""


@dataclass(slots=True)
class EvidenceLink:
    claim_id: str
    paper_id: str
    location: str = ""
    evidence_type: str = EvidenceType.UNCLEAR.value
    quote_or_paraphrase: str = ""
    confidence: str = ""
    note_file: str = ""


@dataclass(slots=True)
class PaperNote:
    paper_id: str = ""
    citation_key: str = ""
    reading_status: str = ReadingStatus.UNREAD.value
    one_sentence_summary: str = ""
    research_question: str = ""
    methods: str = ""
    key_findings: str = ""
    limitations: str = ""
    useful_for: str = ""
    not_useful_for: str = ""
    why_it_matters: str = ""
    personal_reading_notes: str = ""
    claims: list[Claim] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    user_questions: list[str] = field(default_factory=list)
    follow_up_actions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source_path: str = ""


@dataclass(slots=True)
class Tag:
    name: str
    description: str = ""


@dataclass(slots=True)
class ProjectTheme:
    theme_id: str
    name: str
    tags: list[str] = field(default_factory=list)
    min_claims: int = 2
    min_papers: int = 1
    description: str = ""


@dataclass(slots=True)
class ProjectProfile:
    name: str
    root: str
    registry_path: str
    bibtex_path: str
    notes_dir: str
    themes_path: str
    reports_dir: str
    description: str = ""
    is_default: bool = False


@dataclass(slots=True)
class CitationAuditFinding:
    severity: str
    code: str
    message: str
    paper_id: str = ""
    claim_id: str = ""
    theme: str = ""
    suggestion: str = ""


@dataclass(slots=True)
class ValidationFinding:
    severity: str
    code: str
    message: str
    source: str = ""
    identifier: str = ""
    suggestion: str = ""


def enum_values(enum_type: type[Enum]) -> set[str]:
    return {item.value for item in enum_type}


def dataclass_to_plain(value: Any) -> Any:
    if isinstance(value, list):
        return [dataclass_to_plain(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return {
            key: dataclass_to_plain(getattr(value, key))
            for key in value.__dataclass_fields__
        }
    return value
