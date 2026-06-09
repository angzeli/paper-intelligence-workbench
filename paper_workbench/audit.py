"""Citation and evidence completeness audits."""

from __future__ import annotations

from pathlib import Path

from .bibtex import validate_bibtex
from .registry import detect_duplicate_doi, detect_duplicate_title, parse_boolish, validate_registry
from .schema import BibTeXEntry, CitationAuditFinding, Claim, EvidenceType, Paper, PaperNote
from .tags import group_claims_by_theme, normalize_tag, parse_tags, theme_by_tag


LOW_CONFIDENCE_VALUES = {"low", "weak", "uncertain", "speculative", "needs-check", "needs_check"}


def citation_audit(
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    bibtex_entries: list[BibTeXEntry],
    themes,
    root: str | Path = ".",
) -> list[CitationAuditFinding]:
    findings: list[CitationAuditFinding] = []
    root_path = Path(root)
    note_ids = {note.paper_id for note in notes if note.paper_id}
    claims_by_paper: dict[str, list[Claim]] = {}
    for claim in claims:
        claims_by_paper.setdefault(claim.paper_id, []).append(claim)
    for paper in papers:
        note_exists = paper.paper_id in note_ids
        if paper.notes_path:
            note_exists = note_exists or (root_path / paper.notes_path).exists()
        if not note_exists:
            findings.append(
                CitationAuditFinding(
                    "warning",
                    "paper_without_notes",
                    f"{paper.paper_id} has no parsed note.",
                    paper_id=paper.paper_id,
                    suggestion="Generate a note template and add reading notes before citing this paper.",
                )
            )
        if not paper.bibtex_key:
            findings.append(
                CitationAuditFinding(
                    "warning",
                    "registry_missing_bibtex_key",
                    f"{paper.paper_id} has no BibTeX key.",
                    paper_id=paper.paper_id,
                    suggestion="Link the paper to a verified BibTeX entry.",
                )
            )
    for note in notes:
        if not note.claims:
            findings.append(
                CitationAuditFinding(
                    "warning",
                    "note_without_claims",
                    f"{note.paper_id or note.source_path} has notes but no structured claims.",
                    paper_id=note.paper_id,
                    suggestion="Add at least one claim/evidence block if this paper supports the review.",
                )
            )
    for claim in claims:
        if not (claim.section or claim.page):
            findings.append(
                CitationAuditFinding(
                    "error",
                    "claim_missing_evidence_location",
                    f"{claim.claim_id} has no section or page evidence location.",
                    paper_id=claim.paper_id,
                    claim_id=claim.claim_id,
                    suggestion="Add section, page, figure, table, or appendix location.",
                )
            )
        if claim.confidence.strip().lower() in LOW_CONFIDENCE_VALUES or claim.strength in {"weak", "speculative"}:
            findings.append(
                CitationAuditFinding(
                    "warning",
                    "low_confidence_claim",
                    f"{claim.claim_id} is marked low confidence or weak.",
                    paper_id=claim.paper_id,
                    claim_id=claim.claim_id,
                    suggestion="Re-read the evidence before using this claim as core support.",
                )
            )
    for doi, paper_ids in detect_duplicate_doi(papers).items():
        findings.append(
            CitationAuditFinding(
                "error",
                "duplicate_doi",
                f"Duplicate DOI {doi}: {', '.join(paper_ids)}.",
                suggestion="Merge duplicates or correct DOI values.",
            )
        )
    for title, paper_ids in detect_duplicate_title(papers).items():
        findings.append(
            CitationAuditFinding(
                "warning",
                "duplicate_title",
                f"Possible duplicate title {title!r}: {', '.join(paper_ids)}.",
                suggestion="Check whether these registry rows describe the same paper.",
            )
        )
    grouped = group_claims_by_theme(claims, themes)
    theme_ids = {theme.theme_id for theme in themes}
    tag_theme_map = theme_by_tag(themes)
    for theme in themes:
        theme_claims = grouped.get(theme.theme_id, [])
        theme_papers = {claim.paper_id for claim in theme_claims if claim.paper_id}
        if len(theme_claims) < theme.min_claims:
            findings.append(
                CitationAuditFinding(
                    "warning",
                    "theme_under_supported",
                    f"{theme.name} has {len(theme_claims)} supporting claim(s); target is {theme.min_claims}.",
                    theme=theme.theme_id,
                    suggestion="Add more verified claims or lower the theme's stated coverage expectations.",
                )
            )
        if len(theme_papers) < theme.min_papers:
            findings.append(
                CitationAuditFinding(
                    "warning",
                    "theme_too_few_papers",
                    f"{theme.name} has evidence from {len(theme_papers)} paper(s); target is {theme.min_papers}.",
                    theme=theme.theme_id,
                    suggestion="Add more papers with verified claims for this theme.",
                )
            )
        if theme_claims and all(claim.evidence_type == EvidenceType.REVIEW_STATEMENT.value for claim in theme_claims):
            findings.append(
                CitationAuditFinding(
                    "warning",
                    "theme_only_review_statements",
                    f"{theme.name} is supported only by review statements.",
                    theme=theme.theme_id,
                    suggestion="Look for direct experimental, methodological, or theoretical evidence.",
                )
            )
    for finding in validate_registry(papers, root=root, claims=claims):
        if finding.code in {"missing_local_pdf_path", "absolute_pdf_path", "duplicate_bibtex_key", "included_without_claims"}:
            findings.append(
                CitationAuditFinding(
                    finding.severity,
                    finding.code,
                    finding.message,
                    paper_id=finding.identifier,
                    suggestion=finding.suggestion,
                )
            )
    for finding in validate_bibtex(bibtex_entries, papers):
        if finding.code in {"bibtex_not_linked_to_registry", "registry_bibtex_key_missing_from_library", "duplicate_bibtex_key", "duplicate_bibtex_doi"}:
            findings.append(
                CitationAuditFinding(
                    finding.severity,
                    finding.code,
                    finding.message,
                    paper_id=finding.identifier,
                    suggestion=finding.suggestion,
                )
            )
    for claim in claims:
        if not claim.confidence:
            findings.append(
                CitationAuditFinding(
                    "warning",
                    "claim_missing_confidence",
                    f"{claim.claim_id} has no confidence value.",
                    paper_id=claim.paper_id,
                    claim_id=claim.claim_id,
                    suggestion="Add confidence before using this claim in a literature-review outline.",
                )
            )
        if claim.supports_theme and normalize_tag(claim.supports_theme) not in theme_ids:
            findings.append(
                CitationAuditFinding(
                    "warning",
                    "claim_theme_without_definition",
                    f"{claim.claim_id} is tagged to undefined theme {claim.supports_theme!r}.",
                    paper_id=claim.paper_id,
                    claim_id=claim.claim_id,
                    theme=claim.supports_theme,
                    suggestion="Define the theme or correct Supports theme.",
                )
            )
    weak_claim_papers = {claim.paper_id for claim in claims if claim.strength in {"weak", "speculative"}}
    for paper in papers:
        if parse_boolish(paper.included_in_lit_review) is True and paper.paper_id in weak_claim_papers:
            findings.append(
                CitationAuditFinding(
                    "warning",
                    "included_paper_with_weak_evidence",
                    f"{paper.paper_id} is included in the literature review but has weak/speculative evidence.",
                    paper_id=paper.paper_id,
                    suggestion="Re-read or add stronger evidence before relying on this paper.",
                )
            )
    for paper in papers:
        mapped_themes = {tag_theme_map[tag].theme_id for tag in parse_tags(paper.tags) if tag in tag_theme_map}
        for theme_id in mapped_themes:
            has_theme_claim = any(
                normalize_tag(claim.supports_theme) == theme_id
                or theme_id in {tag_theme_map[tag].theme_id for tag in parse_tags(claim.tags) if tag in tag_theme_map}
                for claim in claims_by_paper.get(paper.paper_id, [])
            )
            if not has_theme_claim:
                findings.append(
                    CitationAuditFinding(
                        "warning",
                        "paper_theme_without_claim",
                        f"{paper.paper_id} is tagged for theme {theme_id} but has no clear supporting claim.",
                        paper_id=paper.paper_id,
                        theme=theme_id,
                        suggestion="Add a claim block or remove the theme tag if the paper is not evidence.",
                    )
                )
    return findings
