"""Draft citation and manuscript-evidence auditing.

The matching in this module is deliberately transparent and lexical. It does
not infer scientific truth, invent claims, or rewrite draft prose.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from .schema import BibTeXEntry, Claim, EvidenceType, Paper, PaperNote, ProjectTheme
from .tags import normalize_tag, parse_tags, theme_by_tag


CITE_COMMAND_RE = re.compile(r"\\cite[a-zA-Z*]*\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]+)\}")
AT_CITATION_RE = re.compile(r"(?<![\\\w./:-])@([A-Za-z0-9][A-Za-z0-9_.:+-]*)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9.+-]*")

STRONG_WORDING = (
    "proves",
    "confirms",
    "demonstrates",
    "clearly shows",
    "definitively",
    "always",
    "never",
    "exclusively",
    "significantly improves",
)

WEAK_STRENGTHS = {"weak", "speculative"}
LOW_CONFIDENCE = {"low", "weak", "uncertain", "speculative", "needs-check", "needs_check"}
LOW_READING_STATUS = {"unread", "skimmed"}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "may",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "under",
    "with",
}


@dataclass(slots=True)
class DraftCitation:
    key: str
    raw_text: str
    pattern: str
    paragraph_id: str = ""
    line_number: int = 0


@dataclass(slots=True)
class EvidenceMatch:
    claim_id: str
    paper_id: str
    citation_key: str = ""
    score: int = 0
    match_confidence: str = "low"
    matched_terms: list[str] = field(default_factory=list)
    claim_text: str = ""
    evidence_type: str = ""
    strength: str = ""
    confidence: str = ""
    theme: str = ""


@dataclass(slots=True)
class DraftParagraph:
    paragraph_id: str
    section_title: str
    section_level: int
    order: int
    text: str
    line_start: int
    citation_keys: list[str] = field(default_factory=list)
    citations: list[DraftCitation] = field(default_factory=list)
    possible_claim_like_sentences: list[str] = field(default_factory=list)
    linked_evidence_matches: list[EvidenceMatch] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggested_follow_up_actions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DraftSection:
    section_id: str
    title: str
    level: int
    order: int


@dataclass(slots=True)
class DraftDocument:
    source_path: str
    title: str = ""
    sections: list[DraftSection] = field(default_factory=list)
    paragraphs: list[DraftParagraph] = field(default_factory=list)
    citations: list[DraftCitation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ParagraphAuditFinding:
    severity: str
    code: str
    message: str
    paragraph_id: str = ""
    citation_key: str = ""
    paper_id: str = ""
    suggestion: str = ""


@dataclass(slots=True)
class CitationCoverage:
    key: str
    in_bibtex: bool = False
    in_registry: bool = False
    paper_id: str = ""
    title: str = ""
    reading_status: str = ""
    has_note: bool = False
    claim_count: int = 0
    strongest_claim_strength: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DraftAuditReport:
    draft_path: str
    project: str
    document: DraftDocument
    citation_coverage: list[CitationCoverage] = field(default_factory=list)
    findings: list[ParagraphAuditFinding] = field(default_factory=list)


def _escape(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def _tokens(value: str) -> set[str]:
    return {token for token in TOKEN_RE.findall(value.lower()) if token not in STOPWORDS and len(token) > 1}


def _ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _split_citation_keys(raw: str) -> list[str]:
    keys: list[str] = []
    for part in re.split(r"[;,]", raw):
        value = part.strip().lstrip("@").strip("{}[]()").rstrip(".,;:!?")
        value = re.sub(r"^[A-Za-z]+\s+", "", value)
        if value:
            keys.append(value)
    return keys


def extract_citations(text: str, *, paragraph_id: str = "", line_number: int = 0) -> list[DraftCitation]:
    citation_matches: list[tuple[int, int, str, str, list[str]]] = []
    for order, match in enumerate(CITE_COMMAND_RE.finditer(text)):
        citation_matches.append((match.start(), order, match.group(0), "cite-command", _split_citation_keys(match.group(1))))
    offset = len(citation_matches)
    for order, match in enumerate(AT_CITATION_RE.finditer(text), start=offset):
        citation_matches.append((match.start(), order, match.group(0), "at-key", [match.group(1).rstrip(".,;:!?")]))
    citations: list[DraftCitation] = []
    for _start, _order, raw, pattern, keys in sorted(citation_matches, key=lambda item: (item[0], item[1])):
        for key in keys:
            citations.append(DraftCitation(key=key, raw_text=raw, pattern=pattern, paragraph_id=paragraph_id, line_number=line_number))
    return citations


def _claim_like_sentences(text: str) -> list[str]:
    sentences = [sentence.strip() for sentence in SENTENCE_RE.split(text.strip()) if sentence.strip()]
    claim_like: list[str] = []
    lowered = text.lower()
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(phrase in sentence_lower for phrase in STRONG_WORDING) or len(_tokens(sentence)) >= 8:
            claim_like.append(sentence)
    if not claim_like and lowered:
        claim_like.append(text.strip())
    return claim_like


def parse_markdown_draft(path: str | Path) -> DraftDocument:
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"draft file not found: {target}")
    lines = target.read_text(encoding="utf-8").splitlines()
    sections: list[DraftSection] = []
    paragraphs: list[DraftParagraph] = []
    warnings: list[str] = []
    current_title = "Untitled"
    current_level = 0
    title = ""
    buffer: list[str] = []
    paragraph_start = 1
    in_fence = False

    def flush(end_line: int) -> None:
        nonlocal buffer, paragraph_start
        text = " ".join(line.strip() for line in buffer).strip()
        buffer = []
        if not text:
            return
        paragraph_id = f"p{len(paragraphs) + 1:03d}"
        citations = extract_citations(text, paragraph_id=paragraph_id, line_number=paragraph_start)
        keys = _ordered_unique([citation.key for citation in citations])
        paragraph_warnings: list[str] = []
        if "@" in text and not citations:
            paragraph_warnings.append("Possible ambiguous citation marker not parsed.")
        paragraph = DraftParagraph(
            paragraph_id=paragraph_id,
            section_title=current_title,
            section_level=current_level,
            order=len(paragraphs) + 1,
            text=text,
            line_start=paragraph_start,
            citation_keys=keys,
            citations=citations,
            possible_claim_like_sentences=_claim_like_sentences(text),
            warnings=paragraph_warnings,
        )
        paragraphs.append(paragraph)

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            flush(line_number)
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = HEADING_RE.match(stripped)
        if heading:
            flush(line_number)
            current_level = len(heading.group(1))
            current_title = heading.group(2).strip()
            if not title and current_level == 1:
                title = current_title
            sections.append(DraftSection(section_id=f"s{len(sections) + 1:03d}", title=current_title, level=current_level, order=len(sections) + 1))
            continue
        if not stripped:
            flush(line_number)
            continue
        if not buffer:
            paragraph_start = line_number
        buffer.append(line)
    flush(len(lines) + 1)

    citations: list[DraftCitation] = []
    for paragraph in paragraphs:
        citations.extend(paragraph.citations)
        for warning in paragraph.warnings:
            warnings.append(f"{paragraph.paragraph_id}: {warning}")
    if not sections:
        warnings.append("No Markdown headings were found.")
    return DraftDocument(source_path=str(target), title=title, sections=sections, paragraphs=paragraphs, citations=citations, warnings=warnings)


def _claim_location(claim: Claim) -> str:
    return claim.section or claim.page or ""


def _claim_strength_value(value: str) -> int:
    return {"strong": 4, "moderate": 3, "weak": 2, "speculative": 1}.get(value, 0)


def _strongest_strength(claims: list[Claim]) -> str:
    if not claims:
        return ""
    return max((claim.strength for claim in claims), key=_claim_strength_value)


def _claim_theme(claim: Claim, themes: list[ProjectTheme]) -> str:
    if claim.supports_theme:
        return normalize_tag(claim.supports_theme)
    mapping = theme_by_tag(themes)
    for tag in parse_tags(claim.tags):
        theme = mapping.get(tag)
        if theme:
            return theme.theme_id
    return ""


def _theme_hits(text: str, themes: list[ProjectTheme]) -> list[str]:
    normalized = text.lower().replace("-", " ")
    hits: list[str] = []
    for theme in themes:
        candidates = [theme.name, theme.theme_id, *theme.tags]
        for candidate in candidates:
            candidate_text = str(candidate).lower().replace("-", " ")
            if candidate_text and candidate_text in normalized:
                hits.append(theme.theme_id)
                break
    return _ordered_unique(hits)


def _strong_wording_hits(text: str) -> list[str]:
    lowered = text.lower()
    return [phrase for phrase in STRONG_WORDING if phrase in lowered]


def _match_claim(paragraph: DraftParagraph, claim: Claim, paper: Paper | None, themes: list[ProjectTheme]) -> EvidenceMatch | None:
    paragraph_tokens = _tokens(paragraph.text)
    claim_tokens = _tokens(" ".join([claim.claim_text, claim.quote_or_paraphrase, " ".join(parse_tags(claim.tags)), claim.supports_theme]))
    overlap = sorted(paragraph_tokens & claim_tokens)
    cited = bool(paper and paper.bibtex_key and paper.bibtex_key in paragraph.citation_keys)
    score = min(len(overlap), 8)
    tag_hits = []
    paragraph_lower = paragraph.text.lower().replace("-", " ")
    for tag in parse_tags(claim.tags + ([claim.supports_theme] if claim.supports_theme else [])):
        if tag.replace("-", " ") in paragraph_lower:
            tag_hits.append(tag)
    score += 2 * len(tag_hits)
    if cited:
        score += 3
    if claim.claim_text and claim.claim_text.lower() in paragraph.text.lower():
        score += 6
    if not cited and score < 4:
        return None
    if cited and not overlap and not tag_hits and claim.claim_text.lower() not in paragraph.text.lower():
        return None
    confidence = "high" if score >= 9 else "moderate" if score >= 6 else "low"
    return EvidenceMatch(
        claim_id=claim.claim_id,
        paper_id=claim.paper_id,
        citation_key=paper.bibtex_key if paper else "",
        score=score,
        match_confidence=confidence,
        matched_terms=_ordered_unique(overlap + tag_hits),
        claim_text=claim.claim_text,
        evidence_type=claim.evidence_type,
        strength=claim.strength,
        confidence=claim.confidence,
        theme=_claim_theme(claim, themes),
    )


def _add_finding(findings: list[ParagraphAuditFinding], finding: ParagraphAuditFinding, seen: set[tuple[str, str, str, str]]) -> None:
    key = (finding.code, finding.paragraph_id, finding.citation_key, finding.paper_id)
    if key not in seen:
        seen.add(key)
        findings.append(finding)


def audit_draft(
    document: DraftDocument,
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    bibtex_entries: list[BibTeXEntry],
    themes: list[ProjectTheme],
    *,
    project: str = "",
) -> DraftAuditReport:
    findings: list[ParagraphAuditFinding] = []
    seen_findings: set[tuple[str, str, str, str]] = set()
    bibtex_keys = {entry.key for entry in bibtex_entries}
    papers_by_key = {paper.bibtex_key: paper for paper in papers if paper.bibtex_key}
    notes_by_paper = {note.paper_id: note for note in notes if note.paper_id}
    claims_by_paper: dict[str, list[Claim]] = {}
    for claim in claims:
        claims_by_paper.setdefault(claim.paper_id, []).append(claim)

    citation_keys = _ordered_unique([citation.key for citation in document.citations])
    coverage: list[CitationCoverage] = []
    for key in citation_keys:
        paper = papers_by_key.get(key)
        paper_claims = claims_by_paper.get(paper.paper_id, []) if paper else []
        status = CitationCoverage(
            key=key,
            in_bibtex=key in bibtex_keys,
            in_registry=paper is not None,
            paper_id=paper.paper_id if paper else "",
            title=paper.title if paper else "",
            reading_status=paper.reading_status if paper else "",
            has_note=bool(paper and paper.paper_id in notes_by_paper),
            claim_count=len(paper_claims),
            strongest_claim_strength=_strongest_strength(paper_claims),
        )
        if not status.in_bibtex:
            status.warnings.append("citation key not found in BibTeX")
            _add_finding(
                findings,
                ParagraphAuditFinding("error", "citation_key_not_in_bibtex", f"Citation key {key} is not present in the BibTeX library.", citation_key=key, suggestion="Add or correct the BibTeX entry before using this citation."),
                seen_findings,
            )
        if not status.in_registry:
            status.warnings.append("citation key not found in registry")
            _add_finding(
                findings,
                ParagraphAuditFinding("error", "citation_key_not_in_registry", f"Citation key {key} is not linked to a registry paper.", citation_key=key, suggestion="Link the citation key to a paper registry row."),
                seen_findings,
            )
        if paper:
            if paper.reading_status in LOW_READING_STATUS:
                status.warnings.append(f"paper reading status is {paper.reading_status}")
                _add_finding(
                    findings,
                    ParagraphAuditFinding("warning", "cited_paper_low_reading_status", f"{key} cites {paper.paper_id}, which is marked {paper.reading_status}.", citation_key=key, paper_id=paper.paper_id, suggestion="Read or re-check the paper before relying on it."),
                    seen_findings,
                )
            if not status.has_note:
                status.warnings.append("cited paper has no structured note")
                _add_finding(
                    findings,
                    ParagraphAuditFinding("warning", "cited_paper_without_note", f"{key} cites {paper.paper_id}, which has no parsed structured note.", citation_key=key, paper_id=paper.paper_id, suggestion="Create or parse a note before treating this citation as checked."),
                    seen_findings,
                )
            elif not paper_claims:
                status.warnings.append("cited paper has no extracted claims")
                _add_finding(
                    findings,
                    ParagraphAuditFinding("warning", "cited_paper_without_claims", f"{key} cites {paper.paper_id}, which has no extracted claims.", citation_key=key, paper_id=paper.paper_id, suggestion="Add claim/evidence blocks to the note."),
                    seen_findings,
                )
            elif all(claim.strength in WEAK_STRENGTHS or claim.confidence.lower() in LOW_CONFIDENCE for claim in paper_claims):
                status.warnings.append("cited paper has only weak or low-confidence claims")
                _add_finding(
                    findings,
                    ParagraphAuditFinding("warning", "cited_paper_only_weak_claims", f"{key} cites {paper.paper_id}, which currently has only weak or low-confidence claims.", citation_key=key, paper_id=paper.paper_id, suggestion="Re-read the paper or add stronger evidence before making confident statements."),
                    seen_findings,
                )
        coverage.append(status)

    for paragraph in document.paragraphs:
        candidate_claims = claims
        if paragraph.citation_keys:
            cited_paper_ids = {papers_by_key[key].paper_id for key in paragraph.citation_keys if key in papers_by_key}
            candidate_claims = [claim for claim in claims if claim.paper_id in cited_paper_ids] or claims
        matches: list[EvidenceMatch] = []
        for claim in candidate_claims:
            paper = next((item for item in papers if item.paper_id == claim.paper_id), None)
            match = _match_claim(paragraph, claim, paper, themes)
            if match:
                matches.append(match)
        matches.sort(key=lambda item: (-item.score, item.claim_id))
        paragraph.linked_evidence_matches = matches[:5]
        strong_hits = _strong_wording_hits(paragraph.text)
        theme_hits = _theme_hits(paragraph.text, themes)
        if not paragraph.citation_keys and len(_tokens(paragraph.text)) >= 8:
            _add_finding(
                findings,
                ParagraphAuditFinding("warning", "paragraph_without_citations", f"{paragraph.paragraph_id} has no citation keys.", paragraph_id=paragraph.paragraph_id, suggestion="Add citations or mark the paragraph as connective prose."),
                seen_findings,
            )
        if paragraph.citation_keys and not paragraph.linked_evidence_matches:
            _add_finding(
                findings,
                ParagraphAuditFinding("warning", "paragraph_no_evidence_match", f"{paragraph.paragraph_id} has citations but no local claim match.", paragraph_id=paragraph.paragraph_id, suggestion="Check whether the cited paper supports this paragraph in your notes."),
                seen_findings,
            )
        if paragraph.linked_evidence_matches and all(match.evidence_type == EvidenceType.REVIEW_STATEMENT.value for match in paragraph.linked_evidence_matches):
            _add_finding(
                findings,
                ParagraphAuditFinding("warning", "paragraph_only_review_statement_evidence", f"{paragraph.paragraph_id} currently matches only review-statement evidence.", paragraph_id=paragraph.paragraph_id, suggestion="Add primary experimental, method, or mechanism evidence if the paragraph makes a direct claim."),
                seen_findings,
            )
        weak_matches = [
            match
            for match in paragraph.linked_evidence_matches
            if match.strength in WEAK_STRENGTHS or match.confidence.lower() in LOW_CONFIDENCE or match.evidence_type == EvidenceType.REVIEW_STATEMENT.value
        ]
        if strong_hits and (not paragraph.linked_evidence_matches or len(weak_matches) == len(paragraph.linked_evidence_matches)):
            _add_finding(
                findings,
                ParagraphAuditFinding("warning", "strong_wording_with_weak_evidence", f"{paragraph.paragraph_id} uses strong wording ({', '.join(strong_hits)}) but local evidence is weak, missing, or review-only.", paragraph_id=paragraph.paragraph_id, suggestion="Soften wording or add stronger tracked evidence."),
                seen_findings,
            )
        if theme_hits and not paragraph.citation_keys:
            _add_finding(
                findings,
                ParagraphAuditFinding("warning", "possible_unsupported_claim", f"{paragraph.paragraph_id} mentions project theme(s) {', '.join(theme_hits)} without citations.", paragraph_id=paragraph.paragraph_id, suggestion="Add supporting citations or verify this is only transitional prose."),
                seen_findings,
            )
        for warning in paragraph.warnings:
            _add_finding(
                findings,
                ParagraphAuditFinding("warning", "ambiguous_citation_marker", warning, paragraph_id=paragraph.paragraph_id, suggestion="Use @key, [@key], or \\cite{key} citation syntax."),
                seen_findings,
            )
    return DraftAuditReport(draft_path=document.source_path, project=project or "default", document=document, citation_coverage=coverage, findings=findings)


def parse_report(document: DraftDocument) -> str:
    lines = [
        "# Draft Parse Report",
        "",
        f"Draft file: {document.source_path}",
        f"Title: {document.title or '[none]'}",
        f"Sections: {len(document.sections)}",
        f"Paragraphs: {len(document.paragraphs)}",
        f"Citations: {len(document.citations)}",
        "",
        "## Sections",
        "",
    ]
    if not document.sections:
        lines.append("- No headings found.")
    for section in document.sections:
        lines.append(f"- h{section.level} {section.section_id}: {section.title}")
    lines.extend(["", "## Paragraphs", "", "| Paragraph | Section | Citations | Preview |", "| --- | --- | --- | --- |"])
    for paragraph in document.paragraphs:
        preview = paragraph.text[:120] + ("..." if len(paragraph.text) > 120 else "")
        lines.append(f"| {paragraph.paragraph_id} | {_escape(paragraph.section_title)} | {_escape('; '.join(paragraph.citation_keys) or '[none]')} | {_escape(preview)} |")
    if document.warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in document.warnings:
            lines.append(f"- {warning}")
    return "\n".join(lines).rstrip() + "\n"


def citation_coverage_report(report: DraftAuditReport) -> str:
    lines = [
        "# Draft Citation Coverage Report",
        "",
        f"Draft file: {report.draft_path}",
        f"Project: {report.project}",
        "",
        "| Citation key | BibTeX | Registry | Paper ID | Reading status | Note | Claims | Strongest claim | Warnings |",
        "| --- | --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    if not report.citation_coverage:
        lines.append("|  | No citation keys found. |  |  |  |  |  |  |  |")
    for status in report.citation_coverage:
        lines.append(
            "| {key} | {bib} | {reg} | {paper} | {reading} | {note} | {claims} | {strength} | {warnings} |".format(
                key=_escape(status.key),
                bib="yes" if status.in_bibtex else "no",
                reg="yes" if status.in_registry else "no",
                paper=_escape(status.paper_id or "[missing]"),
                reading=_escape(status.reading_status or "[missing]"),
                note="yes" if status.has_note else "no",
                claims=status.claim_count,
                strength=_escape(status.strongest_claim_strength or "[none]"),
                warnings=_escape("; ".join(status.warnings)),
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def paragraph_evidence_matrix_report(report: DraftAuditReport) -> str:
    lines = [
        "# Paragraph Evidence Matrix",
        "",
        "This matrix uses local keyword, tag, theme, and citation-key overlap. It is a heuristic evidence audit, not semantic certainty.",
        "",
        f"Draft file: {report.draft_path}",
        f"Project: {report.project}",
        "",
        "| Paragraph | Section | Citations | Matched claims | Evidence summary | Warnings |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    findings_by_paragraph: dict[str, list[ParagraphAuditFinding]] = {}
    for finding in report.findings:
        if finding.paragraph_id:
            findings_by_paragraph.setdefault(finding.paragraph_id, []).append(finding)
    for paragraph in report.document.paragraphs:
        matches = "; ".join(f"{match.claim_id} ({match.strength}, {match.evidence_type}, score={match.score})" for match in paragraph.linked_evidence_matches)
        evidence = "; ".join(
            f"{match.paper_id}/{match.citation_key or '[no key]'}: {match.match_confidence} via {', '.join(match.matched_terms[:5]) or 'citation/claim overlap'}"
            for match in paragraph.linked_evidence_matches
        )
        warnings = "; ".join(f"{finding.code}: {finding.suggestion}" for finding in findings_by_paragraph.get(paragraph.paragraph_id, []))
        lines.append(
            f"| {paragraph.paragraph_id} | {_escape(paragraph.section_title)} | {_escape('; '.join(paragraph.citation_keys) or '[none]')} | {_escape(matches or '[none]')} | {_escape(evidence or '[none]')} | {_escape(warnings)} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def revision_checklist_report(report: DraftAuditReport) -> str:
    lines = [
        "# Draft Revision Checklist",
        "",
        "Use this checklist to revise the draft manually. The tool does not rewrite prose or invent support.",
        "",
    ]
    if not report.findings:
        lines.append("- [ ] No audit findings. Still verify citations manually before submission.")
        return "\n".join(lines).rstrip() + "\n"
    for finding in report.findings:
        location = f" ({finding.paragraph_id})" if finding.paragraph_id else ""
        citation = f" [{finding.citation_key}]" if finding.citation_key else ""
        paper = f" [{finding.paper_id}]" if finding.paper_id else ""
        lines.append(f"- [ ] {finding.code}{location}{citation}{paper}: {finding.suggestion or finding.message}")
    return "\n".join(lines).rstrip() + "\n"


def draft_audit_markdown(report: DraftAuditReport) -> str:
    unknown_bib = [item.key for item in report.citation_coverage if not item.in_bibtex]
    unknown_registry = [item.key for item in report.citation_coverage if not item.in_registry]
    missing_notes = [item.key for item in report.citation_coverage if item.in_registry and not item.has_note]
    weak_paragraphs = [
        finding.paragraph_id
        for finding in report.findings
        if finding.code in {"strong_wording_with_weak_evidence", "paragraph_only_review_statement_evidence", "paragraph_no_evidence_match"}
    ]
    uncited = [finding.paragraph_id for finding in report.findings if finding.code == "paragraph_without_citations"]
    lines = [
        "# Draft Citation And Evidence Audit",
        "",
        "This report audits a user-written Markdown draft against local user-tracked evidence. It does not rewrite the draft, judge scientific truth, or fabricate support.",
        "",
        f"Draft file: {report.draft_path}",
        f"Project: {report.project}",
        f"Sections: {len(report.document.sections)}",
        f"Paragraphs: {len(report.document.paragraphs)}",
        f"Citation keys found: {len(report.citation_coverage)}",
        f"Unknown BibTeX keys: {len(unknown_bib)}",
        f"Unknown registry keys: {len(unknown_registry)}",
        f"Cited papers missing notes: {len(missing_notes)}",
        f"Paragraphs with weak or missing evidence: {len(set(weak_paragraphs))}",
        f"Paragraphs with no citations: {len(set(uncited))}",
        "",
        "## Citation Keys Found",
        "",
    ]
    if report.citation_coverage:
        for status in report.citation_coverage:
            label = status.paper_id or "[not linked]"
            lines.append(f"- `{status.key}` -> {label}")
    else:
        lines.append("- No citation keys found.")
    lines.extend(["", "## Findings", ""])
    if not report.findings:
        lines.append("No findings.")
    else:
        lines.extend(["| Severity | Code | Paragraph | Citation | Paper | Message | Suggestion |", "| --- | --- | --- | --- | --- | --- | --- |"])
        for finding in report.findings:
            lines.append(
                "| {severity} | {code} | {paragraph} | {citation} | {paper} | {message} | {suggestion} |".format(
                    severity=_escape(finding.severity),
                    code=_escape(finding.code),
                    paragraph=_escape(finding.paragraph_id),
                    citation=_escape(finding.citation_key),
                    paper=_escape(finding.paper_id),
                    message=_escape(finding.message),
                    suggestion=_escape(finding.suggestion),
                )
            )
    lines.extend(["", "## Citation Coverage", "", citation_coverage_report(report).split("\n", 4)[-1].rstrip(), "", "## Paragraph Evidence Mapping", "", paragraph_evidence_matrix_report(report).split("\n", 6)[-1].rstrip(), "", "## Recommended Revision Checklist", "", revision_checklist_report(report).split("\n", 4)[-1].rstrip()])
    return "\n".join(lines).rstrip() + "\n"
