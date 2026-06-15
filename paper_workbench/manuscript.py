"""Manuscript citation QA built from local evidence only.

This module audits draft manuscripts against the local registry, BibTeX
entries, structured notes, and tracked claims. It deliberately uses transparent
lexical matching and does not rewrite prose or infer scientific truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

from .claim_lifecycle import ClaimLifecycleRecord
from .drafts import (
    DraftAuditReport,
    DraftDocument,
    EvidenceMatch,
    ParagraphAuditFinding,
    audit_draft,
    citation_coverage_report,
    paragraph_evidence_matrix_report,
    parse_markdown_draft,
    parse_report,
    revision_checklist_report,
)
from .schema import BibTeXEntry, Claim, Paper, PaperNote, ProjectTheme
from .tags import normalize_tag, parse_tags, theme_by_tag


@dataclass(slots=True)
class ManuscriptCitationContext:
    section: str
    paragraph_id: str
    citation_key: str
    paper_id: str = ""
    paper_title: str = ""
    year: str = ""
    evidence_type: str = ""
    matched_claim_id: str = ""
    matched_claim: str = ""
    claim_strength: str = ""
    confidence: str = ""
    evidence_location: str = ""
    warning: str = ""


@dataclass(slots=True)
class ClaimTraceabilityRow:
    claim_id: str
    claim: str
    paper_id: str
    citation_key: str = ""
    paragraph_ids: list[str] = field(default_factory=list)
    status: str = "not used"
    warning: str = ""


@dataclass(slots=True)
class ManuscriptQAResult:
    draft_path: str
    project: str
    document: DraftDocument
    audit: DraftAuditReport
    citation_contexts: list[ManuscriptCitationContext] = field(default_factory=list)
    verdict: str = "needs evidence strengthening"


def parse_manuscript(path: str | Path) -> DraftDocument:
    """Parse a Markdown or LaTeX-ish manuscript draft conservatively."""

    return parse_markdown_draft(path)


def audit_manuscript(
    path: str | Path,
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    bibtex_entries: list[BibTeXEntry],
    themes: list[ProjectTheme],
    *,
    project: str = "",
    claim_lifecycle: Mapping[str, ClaimLifecycleRecord] | None = None,
) -> ManuscriptQAResult:
    document = parse_manuscript(path)
    audit = audit_draft(document, papers, notes, claims, bibtex_entries, themes, project=project, claim_lifecycle=claim_lifecycle)
    contexts = build_citation_contexts(audit, papers, claims)
    verdict = manuscript_readiness_verdict(audit)
    return ManuscriptQAResult(
        draft_path=document.source_path,
        project=project or "default",
        document=document,
        audit=audit,
        citation_contexts=contexts,
        verdict=verdict,
    )


def manuscript_readiness_verdict(report: DraftAuditReport) -> str:
    codes = {finding.code for finding in report.findings}
    if {"citation_key_not_in_bibtex", "citation_key_not_in_registry"} & codes:
        return "needs citation cleanup"
    if "paragraph_without_citations" in codes or "possible_unsupported_claim" in codes:
        return "not ready"
    if {
        "strong_wording_with_weak_evidence",
        "paragraph_only_review_statement_evidence",
        "paragraph_no_evidence_match",
        "cited_paper_only_weak_claims",
        "cited_paper_without_claims",
        "matched_claim_not_verified",
        "matched_claim_deprecated",
        "matched_claim_contradicted",
    } & codes:
        return "needs evidence strengthening"
    return "ready for manual writing review"


def build_citation_contexts(report: DraftAuditReport, papers: list[Paper], claims: list[Claim]) -> list[ManuscriptCitationContext]:
    paper_by_key = {paper.bibtex_key: paper for paper in papers if paper.bibtex_key}
    claim_by_id = {claim.claim_id: claim for claim in claims}
    findings_by_paragraph: dict[str, list[ParagraphAuditFinding]] = {}
    findings_by_key: dict[str, list[ParagraphAuditFinding]] = {}
    for finding in report.findings:
        if finding.paragraph_id:
            findings_by_paragraph.setdefault(finding.paragraph_id, []).append(finding)
        if finding.citation_key:
            findings_by_key.setdefault(finding.citation_key, []).append(finding)

    contexts: list[ManuscriptCitationContext] = []
    for paragraph in report.document.paragraphs:
        for citation in paragraph.citations:
            paper = paper_by_key.get(citation.key)
            match = _best_match_for_key(paragraph.linked_evidence_matches, citation.key)
            claim = claim_by_id.get(match.claim_id) if match else None
            warning = _context_warning(paragraph.paragraph_id, citation.key, findings_by_paragraph, findings_by_key)
            contexts.append(
                ManuscriptCitationContext(
                    section=paragraph.section_title,
                    paragraph_id=paragraph.paragraph_id,
                    citation_key=citation.key,
                    paper_id=paper.paper_id if paper else "",
                    paper_title=paper.title if paper else "",
                    year=paper.year if paper else "",
                    evidence_type=match.evidence_type if match else "",
                    matched_claim_id=match.claim_id if match else "",
                    matched_claim=match.claim_text if match else "",
                    claim_strength=match.strength if match else "",
                    confidence=match.confidence if match else "",
                    evidence_location=_claim_location(claim) if claim else "",
                    warning=warning,
                )
            )
    return contexts


def build_claim_traceability(
    report: DraftAuditReport,
    claims: list[Claim],
    papers: list[Paper],
    themes: list[ProjectTheme],
    *,
    theme: str = "",
) -> list[ClaimTraceabilityRow]:
    selected = _claims_for_theme(claims, themes, theme)
    paper_by_id = {paper.paper_id: paper for paper in papers}
    rows: list[ClaimTraceabilityRow] = []
    for claim in selected:
        paragraphs = [
            paragraph
            for paragraph in report.document.paragraphs
            if any(match.claim_id == claim.claim_id for match in paragraph.linked_evidence_matches)
        ]
        paragraph_ids = [paragraph.paragraph_id for paragraph in paragraphs]
        paper = paper_by_id.get(claim.paper_id)
        cited = paper.bibtex_key if paper else ""
        status = "used" if paragraph_ids else "not used"
        warning = ""
        if len(paragraph_ids) > 1:
            warning = "duplicated across multiple paragraphs"
        if paragraph_ids and (claim.strength in {"weak", "speculative"} or not (claim.section or claim.page)):
            warning = "used but evidence is weak or missing location"
        rows.append(
            ClaimTraceabilityRow(
                claim_id=claim.claim_id,
                claim=claim.claim_text,
                paper_id=claim.paper_id,
                citation_key=cited,
                paragraph_ids=paragraph_ids,
                status=status,
                warning=warning,
            )
        )
    return rows


def manuscript_parse_report(document: DraftDocument) -> str:
    content = parse_report(document)
    return content.replace("# Draft Parse Report", "# Manuscript Parse Report", 1)


def manuscript_citations_report(result: ManuscriptQAResult) -> str:
    content = citation_coverage_report(result.audit)
    return content.replace("# Draft Citation Coverage Report", "# Manuscript Citation Coverage Report", 1)


def manuscript_revision_checklist_report(result: ManuscriptQAResult) -> str:
    content = revision_checklist_report(result.audit)
    return content.replace("# Draft Revision Checklist", "# Manuscript Revision Checklist", 1)


def manuscript_context_table_report(result: ManuscriptQAResult) -> str:
    lines = [
        "# Citation Context Table",
        "",
        "This table maps citation occurrences to local registry rows and heuristic claim matches. It does not verify scientific truth.",
        "",
        f"Draft file: {result.draft_path}",
        f"Project: {result.project}",
        "",
        "| Section | Paragraph | Citation key | Paper title | Year | Evidence type | Matched claim | Strength | Confidence | Evidence location | Warning |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not result.citation_contexts:
        lines.append("|  |  | No citation keys found. |  |  |  |  |  |  |  |  |")
    for context in result.citation_contexts:
        lines.append(
            "| {section} | {paragraph} | {key} | {title} | {year} | {evidence} | {claim} | {strength} | {confidence} | {location} | {warning} |".format(
                section=_escape(context.section),
                paragraph=_escape(context.paragraph_id),
                key=_escape(context.citation_key),
                title=_escape(context.paper_title or "[missing]"),
                year=_escape(context.year or "[missing]"),
                evidence=_escape(context.evidence_type or "[no match]"),
                claim=_escape(_claim_label(context.matched_claim_id, context.matched_claim)),
                strength=_escape(context.claim_strength or "[missing]"),
                confidence=_escape(context.confidence or "[missing]"),
                location=_escape(context.evidence_location or "[missing]"),
                warning=_escape(context.warning),
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def claim_traceability_report(rows: list[ClaimTraceabilityRow], *, draft_path: str, project: str, theme: str = "") -> str:
    lines = [
        "# Claim-to-Draft Traceability",
        "",
        "This report checks whether user-tracked claims appear in the manuscript draft through local heuristic matching.",
        "",
        f"Draft file: {draft_path}",
        f"Project: {project}",
        f"Theme: {theme or '[all tracked claims]'}",
        "",
        "| Claim ID | Paper ID | Citation key | Status | Paragraphs | Claim | Warning |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not rows:
        lines.append("|  |  |  | No tracked claims found. |  |  |  |")
    for row in rows:
        lines.append(
            "| {claim_id} | {paper_id} | {key} | {status} | {paragraphs} | {claim} | {warning} |".format(
                claim_id=_escape(row.claim_id),
                paper_id=_escape(row.paper_id),
                key=_escape(row.citation_key or "[missing]"),
                status=_escape(row.status),
                paragraphs=_escape("; ".join(row.paragraph_ids) or "[not used]"),
                claim=_escape(row.claim),
                warning=_escape(row.warning),
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def manuscript_qa_report(result: ManuscriptQAResult) -> str:
    unknown_bib = [item.key for item in result.audit.citation_coverage if not item.in_bibtex]
    unknown_registry = [item.key for item in result.audit.citation_coverage if not item.in_registry]
    missing_notes = [item.key for item in result.audit.citation_coverage if item.in_registry and not item.has_note]
    missing_claims = [item.key for item in result.audit.citation_coverage if item.in_registry and item.has_note and item.claim_count == 0]
    no_citation = _finding_paragraphs(result.audit, "paragraph_without_citations")
    weak = _finding_paragraphs(result.audit, "strong_wording_with_weak_evidence") | _finding_paragraphs(result.audit, "paragraph_no_evidence_match")
    review_only = _finding_paragraphs(result.audit, "paragraph_only_review_statement_evidence")
    checklist = manuscript_revision_checklist_report(result).split("\n", 4)[-1].rstrip()
    matrix = paragraph_evidence_matrix_report(result.audit).split("\n", 6)[-1].rstrip()
    lines = [
        "# Manuscript Citation QA Report",
        "",
        "This reviewer-style QA report audits a user-written manuscript draft against local user-tracked evidence. It does not rewrite prose, judge scientific truth, or fabricate support.",
        "",
        f"Draft file: {result.draft_path}",
        f"Project: {result.project}",
        f"Manuscript title: {result.document.title or '[none]'}",
        f"Sections: {len(result.document.sections)}",
        f"Paragraphs: {len(result.document.paragraphs)}",
        f"Citation keys found: {len(result.audit.citation_coverage)}",
        f"Unknown BibTeX keys: {len(unknown_bib)}",
        f"Unknown registry keys: {len(unknown_registry)}",
        f"Cited papers missing notes: {len(missing_notes)}",
        f"Cited papers missing claims: {len(missing_claims)}",
        f"Paragraphs with no citation: {len(no_citation)}",
        f"Paragraphs with weak or missing evidence: {len(weak)}",
        f"Review-statement-only paragraphs: {len(review_only)}",
        f"Final readiness verdict: {result.verdict}",
        "",
        "## Citation Keys Found",
        "",
    ]
    if result.audit.citation_coverage:
        for status in result.audit.citation_coverage:
            lines.append(f"- `{status.key}` -> {status.paper_id or '[not linked]'}")
    else:
        lines.append("- No citation keys found.")
    lines.extend(
        [
            "",
            "## QA Findings",
            "",
            _findings_table(result.audit),
            "",
            "## Paragraph Evidence Table",
            "",
            matrix,
            "",
            "## Citation Context Table",
            "",
            manuscript_context_table_report(result).split("\n", 7)[-1].rstrip(),
            "",
            "## Revision Checklist",
            "",
            checklist,
            "",
            "## Suggested Follow-up Reading",
            "",
        ]
    )
    followups = _followup_reading_items(result.audit)
    lines.extend(f"- {item}" for item in followups) if followups else lines.append("- No citation-specific follow-up reading items were generated.")
    lines.extend(["", "## Boundary", "", "Use this report to revise manually. Do not treat lexical matches as semantic certainty."])
    return "\n".join(lines).rstrip() + "\n"


def manuscript_paragraph_evidence_report(result: ManuscriptQAResult) -> str:
    content = paragraph_evidence_matrix_report(result.audit)
    return content.replace("# Paragraph Evidence Matrix", "# Manuscript Paragraph Evidence Table", 1)


def _best_match_for_key(matches: list[EvidenceMatch], citation_key: str) -> EvidenceMatch | None:
    keyed = [match for match in matches if match.citation_key == citation_key]
    candidates = keyed or matches
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: (-item.score, item.claim_id))[0]


def _claim_location(claim: Claim | None) -> str:
    if claim is None:
        return ""
    return claim.section or claim.page or ""


def _claim_label(claim_id: str, claim_text: str) -> str:
    if claim_id and claim_text:
        return f"{claim_id}: {claim_text}"
    return claim_text or claim_id or "[no local claim match]"


def _context_warning(
    paragraph_id: str,
    citation_key: str,
    findings_by_paragraph: dict[str, list[ParagraphAuditFinding]],
    findings_by_key: dict[str, list[ParagraphAuditFinding]],
) -> str:
    warnings = [finding.code for finding in findings_by_key.get(citation_key, [])]
    warnings.extend(finding.code for finding in findings_by_paragraph.get(paragraph_id, []))
    return "; ".join(_ordered_unique(warnings))


def _claims_for_theme(claims: list[Claim], themes: list[ProjectTheme], theme: str) -> list[Claim]:
    if not theme:
        return claims
    wanted = normalize_tag(theme)
    tag_map = theme_by_tag(themes)
    selected: list[Claim] = []
    for claim in claims:
        claim_themes = {normalize_tag(claim.supports_theme)} if claim.supports_theme else set()
        for tag in parse_tags(claim.tags):
            mapped = tag_map.get(tag)
            if mapped:
                claim_themes.add(mapped.theme_id)
            if normalize_tag(tag) == wanted:
                claim_themes.add(wanted)
        if wanted in claim_themes:
            selected.append(claim)
    return selected


def _finding_paragraphs(report: DraftAuditReport, code: str) -> set[str]:
    return {finding.paragraph_id for finding in report.findings if finding.code == code and finding.paragraph_id}


def _findings_table(report: DraftAuditReport) -> str:
    lines = ["| Severity | Code | Paragraph | Citation | Paper | Message | Suggestion |", "| --- | --- | --- | --- | --- | --- | --- |"]
    if not report.findings:
        lines.append("|  | none |  |  |  | No findings. |  |")
        return "\n".join(lines)
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
    return "\n".join(lines)


def _followup_reading_items(report: DraftAuditReport) -> list[str]:
    items: list[str] = []
    for status in report.citation_coverage:
        if not status.in_registry:
            items.append(f"Link `{status.key}` to a registry paper or remove the citation.")
        elif not status.has_note:
            items.append(f"Create a structured note for `{status.key}` ({status.paper_id}).")
        elif status.claim_count == 0:
            items.append(f"Add claim/evidence blocks for `{status.key}` ({status.paper_id}).")
        elif status.strongest_claim_strength in {"weak", "speculative"}:
            items.append(f"Re-check weak evidence before relying on `{status.key}` ({status.paper_id}).")
    return _ordered_unique(items)


def _ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _escape(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ").strip()
