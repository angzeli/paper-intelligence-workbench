"""Literature-review authoring aids derived from local evidence only."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

from .claim_lifecycle import ClaimLifecycleRecord, lifecycle_status_for_claim
from .io import write_csv_rows, write_json
from .registry import parse_boolish
from .schema import BibTeXEntry, Claim, EvidenceType, Paper, PaperNote, ProjectTheme, dataclass_to_plain
from .tags import group_claims_by_theme, normalize_tag, parse_tags, theme_by_tag


EVIDENCE_MATRIX_FIELDS = [
    "theme",
    "claim_id",
    "claim",
    "paper_id",
    "paper_title",
    "bibtex_key",
    "evidence_type",
    "strength",
    "confidence",
    "section_or_page",
    "quote_or_paraphrase",
    "limitations",
    "tags",
]

PRIMARY_EVIDENCE_TYPES = {
    EvidenceType.EXPERIMENTAL_RESULT.value,
    EvidenceType.METHOD_DESCRIPTION.value,
    EvidenceType.THEORY_OR_MECHANISM.value,
}

STRENGTH_ORDER = {"strong": 4, "moderate": 3, "weak": 2, "speculative": 1, "": 0}


@dataclass(slots=True)
class LiteratureReviewSection:
    project: str
    theme: str
    candidate_title: str
    purpose: str


@dataclass(slots=True)
class SectionOutline:
    section: LiteratureReviewSection
    key_claim_ids: list[str] = field(default_factory=list)
    supporting_paper_ids: list[str] = field(default_factory=list)
    citation_keys: list[str] = field(default_factory=list)
    evidence_strength: str = ""
    caveats: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    suggested_paragraph_order: list[str] = field(default_factory=list)
    claims_not_ready: list[str] = field(default_factory=list)
    follow_up_actions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EvidenceMatrixRow:
    theme: str
    claim_id: str
    claim: str
    paper_id: str
    paper_title: str = ""
    bibtex_key: str = ""
    evidence_type: str = ""
    strength: str = ""
    confidence: str = ""
    section_or_page: str = ""
    quote_or_paraphrase: str = ""
    limitations: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EvidenceMatrix:
    project: str
    theme: str
    rows: list[EvidenceMatrixRow] = field(default_factory=list)


@dataclass(slots=True)
class ClaimBank:
    project: str
    theme: str
    strong_claims: list[Claim] = field(default_factory=list)
    moderate_claims: list[Claim] = field(default_factory=list)
    weak_claims: list[Claim] = field(default_factory=list)
    missing_evidence_claims: list[Claim] = field(default_factory=list)
    review_statement_claims: list[Claim] = field(default_factory=list)
    conflicting_tag_claims: list[Claim] = field(default_factory=list)
    not_ready_claims: list[Claim] = field(default_factory=list)


@dataclass(slots=True)
class CitationBank:
    project: str
    theme: str
    groups: dict[str, list[Paper]] = field(default_factory=dict)
    linked_claim_ids: dict[str, list[str]] = field(default_factory=dict)
    warnings: dict[str, list[str]] = field(default_factory=dict)


@dataclass(slots=True)
class ParagraphStep:
    order: int
    purpose: str
    claims_to_use: list[str] = field(default_factory=list)
    papers_to_cite: list[str] = field(default_factory=list)
    claims_to_avoid: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ParagraphPlan:
    project: str
    theme: str
    steps: list[ParagraphStep] = field(default_factory=list)


@dataclass(slots=True)
class GapReport:
    project: str
    theme: str
    missing_notes: list[str] = field(default_factory=list)
    missing_bibtex: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    weak_claims: list[str] = field(default_factory=list)
    review_only: bool = False


@dataclass(slots=True)
class WritingReadinessReport:
    project: str
    theme: str
    score: int
    status: str
    factors: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    follow_up_actions: list[str] = field(default_factory=list)


def _escape(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def _theme_for_query(theme_query: str, themes: list[ProjectTheme]) -> ProjectTheme | None:
    wanted = normalize_tag(theme_query)
    for theme in themes:
        if theme.theme_id == wanted or normalize_tag(theme.name) == wanted:
            return theme
    return None


def _theme_claims(theme: ProjectTheme, claims: list[Claim], themes: list[ProjectTheme]) -> list[Claim]:
    return group_claims_by_theme(claims, themes).get(theme.theme_id, [])


def _location(claim: Claim) -> str:
    return claim.section or claim.page or ""


def _note_limitations(notes_by_id: dict[str, PaperNote], paper_id: str) -> str:
    note = notes_by_id.get(paper_id)
    return note.limitations if note else ""


def _paper_ids_for_theme(theme: ProjectTheme, papers: list[Paper], claims: list[Claim], themes: list[ProjectTheme]) -> list[str]:
    tag_map = theme_by_tag(themes)
    paper_ids = {claim.paper_id for claim in _theme_claims(theme, claims, themes) if claim.paper_id}
    for paper in papers:
        if any(tag in tag_map and tag_map[tag].theme_id == theme.theme_id for tag in parse_tags(paper.tags)):
            paper_ids.add(paper.paper_id)
    return sorted(paper_ids)


def _claim_theme_ids(claim: Claim, themes: list[ProjectTheme]) -> set[str]:
    mapping = theme_by_tag(themes)
    ids: set[str] = set()
    if claim.supports_theme:
        ids.add(normalize_tag(claim.supports_theme))
    for tag in parse_tags(claim.tags):
        theme = mapping.get(tag)
        if theme:
            ids.add(theme.theme_id)
    return ids


def build_evidence_matrix(
    theme_query: str,
    papers: list[Paper],
    claims: list[Claim],
    themes: list[ProjectTheme],
    notes: list[PaperNote],
    *,
    project: str = "",
) -> EvidenceMatrix:
    theme = _theme_for_query(theme_query, themes)
    if theme is None:
        return EvidenceMatrix(project=project, theme=theme_query, rows=[])
    paper_by_id = {paper.paper_id: paper for paper in papers}
    notes_by_id = {note.paper_id: note for note in notes if note.paper_id}
    rows: list[EvidenceMatrixRow] = []
    for claim in _theme_claims(theme, claims, themes):
        paper = paper_by_id.get(claim.paper_id)
        rows.append(
            EvidenceMatrixRow(
                theme=theme.theme_id,
                claim_id=claim.claim_id,
                claim=claim.claim_text,
                paper_id=claim.paper_id,
                paper_title=paper.title if paper else "",
                bibtex_key=paper.bibtex_key if paper else "",
                evidence_type=claim.evidence_type,
                strength=claim.strength,
                confidence=claim.confidence,
                section_or_page=_location(claim),
                quote_or_paraphrase=claim.quote_or_paraphrase,
                limitations=_note_limitations(notes_by_id, claim.paper_id),
                tags=parse_tags(claim.tags),
            )
        )
    return EvidenceMatrix(project=project, theme=theme.theme_id, rows=rows)


def evidence_matrix_report(matrix: EvidenceMatrix, theme_name: str | None = None) -> str:
    label = theme_name or matrix.theme
    lines = [
        f"# Evidence Matrix: {label}",
        "",
        "This matrix reorganizes user-tracked claims and evidence. It does not validate scientific truth or write final prose.",
        "",
        f"Project: {matrix.project or 'default'}",
        f"Claims: {len(matrix.rows)}",
        "",
        "| Claim ID | Claim | Paper | BibTeX key | Evidence type | Strength | Confidence | Location | Quote or paraphrase | Limitations | Tags |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not matrix.rows:
        lines.append("|  | No mapped claims. |  |  |  |  |  |  |  |  |  |")
    for row in matrix.rows:
        paper = f"{row.paper_id}: {row.paper_title}" if row.paper_title else row.paper_id
        lines.append(
            "| {claim_id} | {claim} | {paper} | {bibtex_key} | {evidence_type} | {strength} | {confidence} | {location} | {quote} | {limitations} | {tags} |".format(
                claim_id=_escape(row.claim_id),
                claim=_escape(row.claim),
                paper=_escape(paper),
                bibtex_key=_escape(row.bibtex_key or "[missing]"),
                evidence_type=_escape(row.evidence_type),
                strength=_escape(row.strength),
                confidence=_escape(row.confidence or "[missing]"),
                location=_escape(row.section_or_page or "[missing]"),
                quote=_escape(row.quote_or_paraphrase),
                limitations=_escape(row.limitations),
                tags=_escape("; ".join(row.tags)),
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def write_evidence_matrix_csv(matrix: EvidenceMatrix, path: str | Path, *, force: bool = True) -> Path:
    rows = []
    for row in matrix.rows:
        rows.append(
            {
                "theme": row.theme,
                "claim_id": row.claim_id,
                "claim": row.claim,
                "paper_id": row.paper_id,
                "paper_title": row.paper_title,
                "bibtex_key": row.bibtex_key,
                "evidence_type": row.evidence_type,
                "strength": row.strength,
                "confidence": row.confidence,
                "section_or_page": row.section_or_page,
                "quote_or_paraphrase": row.quote_or_paraphrase,
                "limitations": row.limitations,
                "tags": "; ".join(row.tags),
            }
        )
    return write_csv_rows(path, rows, EVIDENCE_MATRIX_FIELDS, force=force)


def write_evidence_matrix_json(matrix: EvidenceMatrix, path: str | Path, *, force: bool = True) -> Path:
    return write_json(path, dataclass_to_plain(matrix), force=force)


def build_claim_bank(
    theme_query: str,
    claims: list[Claim],
    themes: list[ProjectTheme],
    *,
    project: str = "",
) -> ClaimBank:
    theme = _theme_for_query(theme_query, themes)
    if theme is None:
        return ClaimBank(project=project, theme=theme_query)
    theme_claims = _theme_claims(theme, claims, themes)
    conflicting = [claim for claim in theme_claims if len(_claim_theme_ids(claim, themes) - {theme.theme_id}) > 0]
    missing = [claim for claim in theme_claims if not _location(claim)]
    weak = [claim for claim in theme_claims if claim.strength in {"weak", "speculative"}]
    review = [claim for claim in theme_claims if claim.evidence_type == EvidenceType.REVIEW_STATEMENT.value]
    not_ready_ids = {claim.claim_id for claim in missing + weak + review}
    return ClaimBank(
        project=project,
        theme=theme.theme_id,
        strong_claims=[claim for claim in theme_claims if claim.strength == "strong"],
        moderate_claims=[claim for claim in theme_claims if claim.strength == "moderate"],
        weak_claims=weak,
        missing_evidence_claims=missing,
        review_statement_claims=review,
        conflicting_tag_claims=conflicting,
        not_ready_claims=[claim for claim in theme_claims if claim.claim_id in not_ready_ids],
    )


def _claim_lines(claims: list[Claim]) -> list[str]:
    if not claims:
        return ["- None."]
    return [f"- **{claim.claim_id}** ({claim.strength}, {claim.evidence_type}; {_location(claim) or 'missing location'}): {claim.claim_text}" for claim in claims]


def claim_bank_report(bank: ClaimBank) -> str:
    lines = [
        f"# Claim Bank: {bank.theme}",
        "",
        "This report lists user-entered claims without rewriting them into final literature-review prose.",
        "",
        "## Strong Claims",
        *_claim_lines(bank.strong_claims),
        "",
        "## Moderate Claims",
        *_claim_lines(bank.moderate_claims),
        "",
        "## Weak or Speculative Claims",
        *_claim_lines(bank.weak_claims),
        "",
        "## Claims Missing Evidence Location",
        *_claim_lines(bank.missing_evidence_claims),
        "",
        "## Claims Supported by Review Statements",
        *_claim_lines(bank.review_statement_claims),
        "",
        "## Claims With Conflicting Theme Tags",
        *_claim_lines(bank.conflicting_tag_claims),
        "",
        "## Claims Not Ready for Confident Use",
        *_claim_lines(bank.not_ready_claims),
    ]
    return "\n".join(lines).rstrip() + "\n"


def _paper_category(claims: list[Claim], missing_note: bool) -> str:
    if missing_note or not claims:
        return "not yet usable"
    if any(not _location(claim) or claim.strength in {"weak", "speculative"} for claim in claims):
        return "not yet usable"
    evidence_types = {claim.evidence_type for claim in claims}
    if EvidenceType.EXPERIMENTAL_RESULT.value in evidence_types:
        return "primary evidence"
    if EvidenceType.METHOD_DESCRIPTION.value in evidence_types:
        return "method"
    if EvidenceType.THEORY_OR_MECHANISM.value in evidence_types:
        return "mechanism"
    if EvidenceType.LIMITATION.value in evidence_types:
        return "limitation"
    if EvidenceType.REVIEW_STATEMENT.value in evidence_types:
        return "review context"
    if EvidenceType.BACKGROUND_CONTEXT.value in evidence_types:
        return "background"
    if EvidenceType.OPINION_OR_INTERPRETATION.value in evidence_types:
        return "comparison"
    return "not yet usable"


def build_citation_bank(
    theme_query: str,
    papers: list[Paper],
    claims: list[Claim],
    themes: list[ProjectTheme],
    notes: list[PaperNote],
    entries: list[BibTeXEntry],
    *,
    project: str = "",
) -> CitationBank:
    theme = _theme_for_query(theme_query, themes)
    if theme is None:
        return CitationBank(project=project, theme=theme_query)
    paper_by_id = {paper.paper_id: paper for paper in papers}
    note_ids = {note.paper_id for note in notes if note.paper_id}
    entry_keys = {entry.key for entry in entries if entry.key}
    claims_by_paper: dict[str, list[Claim]] = defaultdict(list)
    for claim in _theme_claims(theme, claims, themes):
        claims_by_paper[claim.paper_id].append(claim)
    bank = CitationBank(project=project, theme=theme.theme_id)
    for category in ("background", "method", "primary evidence", "mechanism", "limitation", "review context", "comparison", "not yet usable"):
        bank.groups[category] = []
    for paper_id in _paper_ids_for_theme(theme, papers, claims, themes):
        paper = paper_by_id.get(paper_id)
        if paper is None:
            continue
        warnings: list[str] = []
        if paper.paper_id not in note_ids:
            warnings.append("missing note")
        if not paper.bibtex_key:
            warnings.append("missing BibTeX key")
        elif paper.bibtex_key not in entry_keys:
            warnings.append("BibTeX key missing from library")
        linked_claims = claims_by_paper.get(paper.paper_id, [])
        category = _paper_category(linked_claims, "missing note" in warnings)
        bank.groups.setdefault(category, []).append(paper)
        bank.linked_claim_ids[paper.paper_id] = [claim.claim_id for claim in linked_claims]
        bank.warnings[paper.paper_id] = warnings
    return bank


def _best_strength(claims: list[Claim]) -> str:
    if not claims:
        return "none"
    return max((claim.strength or "" for claim in claims), key=lambda value: STRENGTH_ORDER.get(value, 0))


def citation_bank_report(bank: CitationBank, claims: list[Claim] | None = None) -> str:
    claim_by_id = {claim.claim_id: claim for claim in claims or []}
    lines = [
        f"# Citation Bank: {bank.theme}",
        "",
        "This report groups papers by likely citation use based on user-tracked evidence. It does not invent citation roles.",
        "",
    ]
    for category, papers in bank.groups.items():
        lines.extend([f"## {category.title()}", ""])
        if not papers:
            lines.append("- None.")
            lines.append("")
            continue
        lines.extend(["| Paper | Year | Journal | BibTeX key | Reading status | Linked claims | Evidence strength | Warnings |", "| --- | --- | --- | --- | --- | --- | --- | --- |"])
        for paper in sorted(papers, key=lambda item: (item.year, item.paper_id)):
            claim_ids = bank.linked_claim_ids.get(paper.paper_id, [])
            linked_claims = [claim_by_id[claim_id] for claim_id in claim_ids if claim_id in claim_by_id]
            lines.append(
                f"| {_escape(paper.paper_id + ': ' + paper.title)} | {_escape(paper.year)} | {_escape(paper.journal)} | {_escape(paper.bibtex_key or '[missing]')} | {_escape(paper.reading_status)} | {_escape('; '.join(claim_ids) or '[none]')} | {_escape(_best_strength(linked_claims))} | {_escape('; '.join(bank.warnings.get(paper.paper_id, [])) or 'none')} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_paragraph_plan(
    theme_query: str,
    papers: list[Paper],
    claims: list[Claim],
    themes: list[ProjectTheme],
    notes: list[PaperNote],
    *,
    project: str = "",
) -> ParagraphPlan:
    theme = _theme_for_query(theme_query, themes)
    if theme is None:
        return ParagraphPlan(project=project, theme=theme_query)
    theme_claims = _theme_claims(theme, claims, themes)
    paper_by_id = {paper.paper_id: paper for paper in papers}

    def claim_ids(*evidence_types: str, ready_only: bool = True) -> list[str]:
        selected = [claim for claim in theme_claims if claim.evidence_type in evidence_types]
        if ready_only:
            selected = [claim for claim in selected if _location(claim) and claim.strength in {"strong", "moderate"}]
        return [claim.claim_id for claim in selected[:6]]

    def paper_keys(claim_ids_: list[str]) -> list[str]:
        ids = {claim.paper_id for claim in theme_claims if claim.claim_id in claim_ids_}
        return sorted({paper_by_id[paper_id].bibtex_key or paper_id for paper_id in ids if paper_id in paper_by_id})

    weak_or_missing = [claim.claim_id for claim in theme_claims if claim.strength in {"weak", "speculative"} or not _location(claim)]
    steps = [
        ParagraphStep(1, "Opening context and scope", claim_ids(EvidenceType.BACKGROUND_CONTEXT.value, EvidenceType.REVIEW_STATEMENT.value, ready_only=False)),
        ParagraphStep(2, "Key mechanism or problem", claim_ids(EvidenceType.THEORY_OR_MECHANISM.value, EvidenceType.EXPERIMENTAL_RESULT.value)),
        ParagraphStep(3, "Primary evidence from tracked papers", claim_ids(EvidenceType.EXPERIMENTAL_RESULT.value)),
        ParagraphStep(4, "Methods that explain how evidence was produced", claim_ids(EvidenceType.METHOD_DESCRIPTION.value)),
        ParagraphStep(5, "Limitations, caveats, and competing interpretations", claim_ids(EvidenceType.LIMITATION.value, EvidenceType.OPINION_OR_INTERPRETATION.value, ready_only=False)),
        ParagraphStep(6, "Gap leading to the next subsection", []),
    ]
    for step in steps:
        step.papers_to_cite = paper_keys(step.claims_to_use)
        step.claims_to_avoid = weak_or_missing[:8] if step.order in {5, 6} else []
        step.missing_evidence = [claim.claim_id for claim in theme_claims if not _location(claim)][:8] if step.order == 6 else []
        if step.order == 6 and not step.claims_to_use:
            step.caveats.append("Use this paragraph to document missing evidence and follow-up reading, not to assert unsupported conclusions.")
    return ParagraphPlan(project=project, theme=theme.theme_id, steps=steps)


def paragraph_plan_report(plan: ParagraphPlan) -> str:
    lines = [
        f"# Paragraph Plan: {plan.theme}",
        "",
        "This is a planning aid. It provides paragraph purposes and evidence references, not polished final prose.",
        "",
    ]
    if not plan.steps:
        lines.append("Theme not found or no paragraph plan available.")
        return "\n".join(lines).rstrip() + "\n"
    for step in plan.steps:
        lines.extend([f"## {step.order}. {step.purpose}", ""])
        lines.append(f"- Claims to use: {'; '.join(step.claims_to_use) if step.claims_to_use else 'none yet'}")
        lines.append(f"- Papers to cite: {'; '.join(step.papers_to_cite) if step.papers_to_cite else 'none yet'}")
        lines.append(f"- Claims to avoid: {'; '.join(step.claims_to_avoid) if step.claims_to_avoid else 'none flagged'}")
        lines.append(f"- Missing evidence: {'; '.join(step.missing_evidence) if step.missing_evidence else 'none flagged for this paragraph'}")
        lines.append(f"- Caveats: {'; '.join(step.caveats) if step.caveats else 'none recorded'}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_gap_report(
    theme: ProjectTheme,
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    entries: list[BibTeXEntry],
    themes: list[ProjectTheme],
    *,
    project: str = "",
) -> GapReport:
    note_ids = {note.paper_id for note in notes if note.paper_id}
    paper_by_id = {paper.paper_id: paper for paper in papers}
    entry_keys = {entry.key for entry in entries if entry.key}
    theme_claims = _theme_claims(theme, claims, themes)
    paper_ids = _paper_ids_for_theme(theme, papers, claims, themes)
    missing_notes = [paper_id for paper_id in paper_ids if paper_id not in note_ids]
    missing_bibtex = [
        paper_id
        for paper_id in paper_ids
        if paper_id in paper_by_id and (not paper_by_id[paper_id].bibtex_key or paper_by_id[paper_id].bibtex_key not in entry_keys)
    ]
    missing_evidence = [claim.claim_id for claim in theme_claims if not _location(claim)]
    weak_claims = [claim.claim_id for claim in theme_claims if claim.strength in {"weak", "speculative"}]
    review_only = bool(theme_claims) and all(claim.evidence_type == EvidenceType.REVIEW_STATEMENT.value for claim in theme_claims)
    return GapReport(
        project=project,
        theme=theme.theme_id,
        missing_notes=missing_notes,
        missing_bibtex=missing_bibtex,
        missing_evidence=missing_evidence,
        weak_claims=weak_claims,
        review_only=review_only,
    )


def build_subsection_readiness(
    theme_query: str,
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    entries: list[BibTeXEntry],
    themes: list[ProjectTheme],
    *,
    project: str = "",
) -> WritingReadinessReport:
    theme = _theme_for_query(theme_query, themes)
    if theme is None:
        return WritingReadinessReport(project=project, theme=theme_query, score=0, status="theme_not_found", blockers=[f"Theme not found: {theme_query}"])
    theme_claims = _theme_claims(theme, claims, themes)
    paper_by_id = {paper.paper_id: paper for paper in papers}
    paper_ids = _paper_ids_for_theme(theme, papers, claims, themes)
    read_statuses = {"read", "deeply_read"}
    read_papers = [paper_by_id[paper_id] for paper_id in paper_ids if paper_id in paper_by_id and paper_by_id[paper_id].reading_status in read_statuses]
    strong_claims = [claim for claim in theme_claims if claim.strength == "strong"]
    evidence_types = {claim.evidence_type for claim in theme_claims if claim.evidence_type and claim.evidence_type != EvidenceType.UNCLEAR.value}
    gap = build_gap_report(theme, papers, notes, claims, entries, themes, project=project)
    score = 0
    factors: list[str] = []

    def add(points: int, passed: bool, message: str) -> None:
        nonlocal score
        if passed:
            score += points
            factors.append(f"+{points}: {message}")
        else:
            factors.append(f"+0/{points}: {message}")

    add(20, len(paper_ids) >= theme.min_papers, f"{len(paper_ids)} supporting/tagged paper(s), target {theme.min_papers}")
    add(15, len(read_papers) >= min(theme.min_papers, max(1, len(paper_ids))), f"{len(read_papers)} read/deeply-read paper(s)")
    add(15, len(theme_claims) >= theme.min_claims, f"{len(theme_claims)} tracked claim(s), target {theme.min_claims}")
    add(15, bool(strong_claims), f"{len(strong_claims)} strong claim(s)")
    add(10, len(evidence_types) >= 2, f"{len(evidence_types)} evidence type(s)")
    add(10, not gap.missing_notes, f"{len(gap.missing_notes)} paper(s) missing notes")
    add(10, not gap.missing_evidence, f"{len(gap.missing_evidence)} claim(s) missing evidence locations")
    add(5, not gap.missing_bibtex, f"{len(gap.missing_bibtex)} paper(s) missing linked BibTeX")
    add(5, not gap.review_only, "theme is not supported only by review statements")

    blockers: list[str] = []
    warnings: list[str] = []
    if not theme_claims:
        blockers.append("No tracked claims are mapped to this theme.")
    if gap.missing_evidence:
        blockers.append("Some claims are missing evidence locations.")
    if gap.review_only:
        warnings.append("Mapped claims rely only on review statements.")
    if gap.missing_notes:
        warnings.append("Some tagged/supporting papers do not have parsed notes.")
    if gap.missing_bibtex:
        warnings.append("Some supporting papers are missing linked BibTeX entries.")
    if any(parse_boolish(paper_by_id[paper_id].included_in_lit_review) is True for paper_id in gap.missing_bibtex if paper_id in paper_by_id):
        warnings.append("At least one included paper is missing linked BibTeX.")

    if score >= 75 and not blockers:
        status = "ready_to_outline"
    elif score >= 50:
        status = "needs_targeted_follow_up"
    else:
        status = "not_ready"
    follow_up = []
    if gap.missing_notes:
        follow_up.append("Add or parse notes for tagged/supporting papers.")
    if gap.missing_evidence:
        follow_up.append("Add section, page, figure, table, or appendix locations before citing claims.")
    if not strong_claims:
        follow_up.append("Identify at least one strong direct-evidence claim before drafting the subsection.")
    if gap.review_only:
        follow_up.append("Look for primary or methodological evidence beyond review statements.")
    if gap.missing_bibtex:
        follow_up.append("Link supporting papers to verified BibTeX entries.")
    return WritingReadinessReport(project=project, theme=theme.theme_id, score=min(score, 100), status=status, factors=factors, blockers=blockers, warnings=warnings, follow_up_actions=follow_up)


def subsection_readiness_report(report: WritingReadinessReport) -> str:
    lines = [
        f"# Subsection Readiness: {report.theme}",
        "",
        "This is a local completeness score for writing preparation. It is not a truth score and does not judge whether claims are scientifically correct.",
        "",
        f"- Project: {report.project or 'default'}",
        f"- Score: {report.score}/100",
        f"- Status: {report.status}",
        "",
        "## Scoring Factors",
        *[f"- {factor}" for factor in report.factors],
        "",
        "## Blockers",
        *([f"- {item}" for item in report.blockers] if report.blockers else ["- None."]),
        "",
        "## Warnings",
        *([f"- {item}" for item in report.warnings] if report.warnings else ["- None."]),
        "",
        "## Follow-up Actions",
        *([f"- {item}" for item in report.follow_up_actions] if report.follow_up_actions else ["- No immediate follow-up actions from the readiness rubric."]),
    ]
    return "\n".join(lines).rstrip() + "\n"


def build_section_outline(
    theme_query: str,
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    entries: list[BibTeXEntry],
    themes: list[ProjectTheme],
    *,
    project: str = "",
) -> SectionOutline:
    theme = _theme_for_query(theme_query, themes)
    if theme is None:
        section = LiteratureReviewSection(project=project, theme=theme_query, candidate_title=theme_query, purpose="Theme not found.")
        return SectionOutline(section=section, follow_up_actions=[f"Define or correct theme {theme_query!r}."])
    paper_by_id = {paper.paper_id: paper for paper in papers}
    theme_claims = _theme_claims(theme, claims, themes)
    strong_or_moderate = [claim for claim in theme_claims if claim.strength in {"strong", "moderate"}]
    paper_ids = _paper_ids_for_theme(theme, papers, claims, themes)
    citation_keys = sorted({paper_by_id[paper_id].bibtex_key for paper_id in paper_ids if paper_id in paper_by_id and paper_by_id[paper_id].bibtex_key})
    gap = build_gap_report(theme, papers, notes, claims, entries, themes, project=project)
    readiness = build_subsection_readiness(theme.theme_id, papers, notes, claims, entries, themes, project=project)
    paragraph_plan = build_paragraph_plan(theme.theme_id, papers, claims, themes, notes, project=project)
    section = LiteratureReviewSection(
        project=project,
        theme=theme.theme_id,
        candidate_title=theme.name,
        purpose=f"Prepare an evidence-backed subsection plan for {theme.name}.",
    )
    return SectionOutline(
        section=section,
        key_claim_ids=[claim.claim_id for claim in strong_or_moderate],
        supporting_paper_ids=paper_ids,
        citation_keys=citation_keys,
        evidence_strength=f"{len(strong_or_moderate)} strong/moderate claim(s); readiness {readiness.score}/100",
        caveats=readiness.warnings,
        missing_evidence=gap.missing_evidence,
        suggested_paragraph_order=[step.purpose for step in paragraph_plan.steps],
        claims_not_ready=sorted(set(gap.weak_claims + gap.missing_evidence)),
        follow_up_actions=readiness.follow_up_actions,
    )


def _section_outline_markdown(outline: SectionOutline) -> str:
    lines = [
        f"## Section Outline: {outline.section.candidate_title}",
        "",
        f"- Purpose: {outline.section.purpose}",
        f"- Evidence strength: {outline.evidence_strength or 'not assessed'}",
        f"- Supporting papers: {'; '.join(outline.supporting_paper_ids) if outline.supporting_paper_ids else 'none yet'}",
        f"- Citation keys: {'; '.join(outline.citation_keys) if outline.citation_keys else 'none with verified keys'}",
        "",
        "### Key Claims",
        *([f"- {claim_id}" for claim_id in outline.key_claim_ids] if outline.key_claim_ids else ["- None marked strong or moderate."]),
        "",
        "### Suggested Paragraph Order",
        *([f"- {item}" for item in outline.suggested_paragraph_order] if outline.suggested_paragraph_order else ["- Add verified evidence before planning paragraph order."]),
        "",
        "### Claims Not Ready for Use",
        *([f"- {claim_id}" for claim_id in outline.claims_not_ready] if outline.claims_not_ready else ["- None flagged."]),
        "",
        "### Follow-up Actions",
        *([f"- {item}" for item in outline.follow_up_actions] if outline.follow_up_actions else ["- No immediate actions from the readiness rubric."]),
    ]
    return "\n".join(lines).rstrip() + "\n"


def writing_packet_report(
    theme_query: str,
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    entries: list[BibTeXEntry],
    themes: list[ProjectTheme],
    *,
    project: str = "",
    claim_lifecycle: Mapping[str, ClaimLifecycleRecord] | None = None,
) -> str:
    theme = _theme_for_query(theme_query, themes)
    theme_name = theme.name if theme else theme_query
    outline = build_section_outline(theme_query, papers, notes, claims, entries, themes, project=project)
    matrix = build_evidence_matrix(theme_query, papers, claims, themes, notes, project=project)
    bank = build_claim_bank(theme_query, claims, themes, project=project)
    citations = build_citation_bank(theme_query, papers, claims, themes, notes, entries, project=project)
    plan = build_paragraph_plan(theme_query, papers, claims, themes, notes, project=project)
    readiness = build_subsection_readiness(theme_query, papers, notes, claims, entries, themes, project=project)
    parts = [
        f"# Literature Review Writing Packet: {theme_name}",
        "",
        "Boundary: this packet is a local planning artifact. It does not fabricate claims, citations, quotes, summaries, or polished final prose.",
        "",
        _section_outline_markdown(outline),
        evidence_matrix_report(matrix, theme_name=theme_name).replace(f"# Evidence Matrix: {theme_name}", "## Evidence Matrix", 1),
        claim_bank_report(bank).replace(f"# Claim Bank: {bank.theme}", "## Claim Bank", 1),
        citation_bank_report(citations, claims).replace(f"# Citation Bank: {citations.theme}", "## Citation Bank", 1),
        paragraph_plan_report(plan).replace(f"# Paragraph Plan: {plan.theme}", "## Paragraph Plan", 1),
        subsection_readiness_report(readiness).replace(f"# Subsection Readiness: {readiness.theme}", "## Subsection Readiness", 1),
    ]
    if claim_lifecycle is not None:
        parts.append(_claim_lifecycle_warnings_markdown(theme_query, claims, themes, claim_lifecycle))
    return "\n\n".join(part.rstrip() for part in parts).rstrip() + "\n"


def _claim_lifecycle_warnings_markdown(
    theme_query: str,
    claims: list[Claim],
    themes: list[ProjectTheme],
    records: Mapping[str, ClaimLifecycleRecord],
) -> str:
    theme = _theme_for_query(theme_query, themes)
    theme_name = theme.name if theme else theme_query
    mapped = _theme_claims(theme, claims, themes) if theme else []
    rows: list[tuple[Claim, str]] = []
    for claim in mapped:
        status = lifecycle_status_for_claim(claim, records)
        if status not in {"verified", "ready_for_draft_use"}:
            rows.append((claim, status))
    lines = [
        "## Claim Lifecycle Warnings",
        "",
        f"Theme: {theme_name}",
        "",
        "These warnings come from local review state only. They do not decide whether a claim is scientifically true.",
        "",
        "| Claim ID | Status | Reason to review before draft use |",
        "| --- | --- | --- |",
    ]
    if rows:
        for claim, status in sorted(rows, key=lambda item: item[0].claim_id):
            reason = "verify against note before draft use"
            if status == "needs_evidence_location":
                reason = "add or check page/section evidence location"
            elif status == "too_weak_to_use":
                reason = "claim is weak/speculative or low-confidence"
            elif status == "deprecated":
                reason = "claim is deprecated and should be avoided"
            elif status == "contradicted":
                reason = "claim is in contradiction review"
            elif status == "needs_rereading":
                reason = "paper or note needs rereading"
            lines.append(f"| `{claim.claim_id}` | {status} | {reason} |")
    else:
        lines.append("| none | ready/verified | No lifecycle warnings for mapped claims. |")
    return "\n".join(lines).rstrip() + "\n"
