"""Markdown report generation."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from .audit import citation_audit
from .bibtex import validate_bibtex
from .io import write_text
from .registry import display_authors, validate_registry
from .schema import BibTeXEntry, CitationAuditFinding, Claim, EvidenceType, Paper, PaperNote, ProjectTheme, ValidationFinding
from .tags import count_paper_tags, group_claims_by_theme, normalize_tag, theme_by_tag


def write_report(name: str, content: str, reports_dir: str | Path = "reports") -> Path:
    target = Path(reports_dir) / f"{name}.md"
    return write_text(target, content)


def _finding_rows(findings: list[ValidationFinding] | list[CitationAuditFinding]) -> str:
    if not findings:
        return "No findings.\n"
    lines = ["| Severity | Code | Identifier | Message | Suggestion |", "| --- | --- | --- | --- | --- |"]
    for finding in findings:
        identifier = getattr(finding, "identifier", "") or getattr(finding, "paper_id", "") or getattr(finding, "claim_id", "") or getattr(finding, "theme", "")
        lines.append(
            "| {severity} | {code} | {identifier} | {message} | {suggestion} |".format(
                severity=finding.severity,
                code=finding.code,
                identifier=_escape(identifier),
                message=_escape(finding.message),
                suggestion=_escape(getattr(finding, "suggestion", "")),
            )
        )
    return "\n".join(lines) + "\n"


def _escape(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def inventory_report(papers: list[Paper]) -> str:
    lines = [
        "# Paper Inventory Report",
        "",
        f"Total papers: {len(papers)}",
        "",
        "| Paper ID | Title | Authors | Year | Status | Tags |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for paper in papers:
        lines.append(
            f"| {_escape(paper.paper_id)} | {_escape(paper.title)} | {_escape(display_authors(paper.authors))} | {_escape(paper.year)} | {_escape(paper.reading_status)} | {_escape('; '.join(paper.tags))} |"
        )
    findings = validate_registry(papers)
    lines.extend(["", "## Registry Findings", "", _finding_rows(findings)])
    return "\n".join(lines).rstrip() + "\n"


def reading_status_report(papers: list[Paper]) -> str:
    counts = Counter(paper.reading_status for paper in papers)
    lines = ["# Reading Status Report", "", "| Status | Papers |", "| --- | ---: |"]
    for status, count in sorted(counts.items()):
        lines.append(f"| {status} | {count} |")
    lines.extend(["", "## Unread or Partial", ""])
    for paper in papers:
        if paper.reading_status in {"unread", "skimmed", "partially_read"}:
            lines.append(f"- {paper.paper_id}: {paper.title} ({paper.reading_status})")
    return "\n".join(lines).rstrip() + "\n"


def papers_by_tag_report(papers: list[Paper]) -> str:
    counts = count_paper_tags(papers)
    lines = ["# Papers by Tag Report", "", "| Tag | Papers |", "| --- | ---: |"]
    for tag, count in sorted(counts.items()):
        lines.append(f"| {tag} | {count} |")
    lines.append("")
    for tag in sorted(counts):
        lines.append(f"## {tag}")
        for paper in papers:
            if tag in paper.tags:
                lines.append(f"- {paper.paper_id}: {paper.title}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def bibtex_audit_report(entries: list[BibTeXEntry], findings: list[ValidationFinding] | None = None) -> str:
    findings = findings if findings is not None else validate_bibtex(entries)
    lines = [
        "# BibTeX Audit Report",
        "",
        f"Entries parsed: {len(entries)}",
        "",
        "## Findings",
        "",
        _finding_rows(findings),
    ]
    return "\n".join(lines).rstrip() + "\n"


def claims_grouped_by_theme_report(claims: list[Claim], themes) -> str:
    grouped = group_claims_by_theme(claims, themes)
    theme_names = {theme.theme_id: theme.name for theme in themes}
    lines = ["# Claims Grouped by Theme", ""]
    for theme_id, theme_claims in sorted(grouped.items()):
        lines.append(f"## {theme_names.get(theme_id, theme_id)}")
        lines.append(f"Claims: {len(theme_claims)}")
        lines.append("")
        for claim in theme_claims:
            lines.append(f"- **{claim.claim_id}** ({claim.strength}, {claim.evidence_type}): {claim.claim_text}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def missing_notes_report(papers: list[Paper], notes: list[PaperNote]) -> str:
    note_ids = {note.paper_id for note in notes if note.paper_id}
    lines = ["# Missing Notes Report", ""]
    missing = [paper for paper in papers if paper.paper_id not in note_ids]
    lines.append(f"Papers missing parsed notes: {len(missing)}")
    lines.append("")
    for paper in missing:
        lines.append(f"- {paper.paper_id}: {paper.title}")
    return "\n".join(lines).rstrip() + "\n"


def weak_claims_report(claims: list[Claim]) -> str:
    weak = [claim for claim in claims if claim.strength in {"weak", "speculative"} or claim.confidence.lower() in {"low", "weak", "uncertain"}]
    lines = ["# Weak Claims Report", "", f"Weak or low-confidence claims: {len(weak)}", ""]
    for claim in weak:
        location = claim.section or claim.page or "missing location"
        lines.append(f"- **{claim.claim_id}** ({claim.strength}, {claim.confidence or 'no confidence'}; {location}): {claim.claim_text}")
    return "\n".join(lines).rstrip() + "\n"


def evidence_map_report(papers: list[Paper], claims: list[Claim], themes, notes: list[PaperNote] | None = None) -> str:
    grouped = group_claims_by_theme(claims, themes)
    paper_by_id = {paper.paper_id: paper for paper in papers}
    noted_ids = {note.paper_id for note in notes or [] if note.paper_id}
    tag_map = theme_by_tag(themes)
    lines = ["# Literature Review Evidence Map", ""]
    for theme in themes:
        theme_claims = grouped.get(theme.theme_id, [])
        paper_ids = sorted({claim.paper_id for claim in theme_claims if claim.paper_id})
        strong_claims = [claim for claim in theme_claims if claim.strength == "strong"]
        moderate_claims = [claim for claim in theme_claims if claim.strength == "moderate"]
        weak_claims = [claim for claim in theme_claims if claim.strength in {"weak", "speculative"}]
        missing_evidence = [claim for claim in theme_claims if not (claim.section or claim.page)]
        review_statements = [claim for claim in theme_claims if claim.evidence_type == EvidenceType.REVIEW_STATEMENT.value]
        primary_evidence = [
            claim
            for claim in theme_claims
            if claim.evidence_type
            in {
                EvidenceType.EXPERIMENTAL_RESULT.value,
                EvidenceType.METHOD_DESCRIPTION.value,
                EvidenceType.THEORY_OR_MECHANISM.value,
            }
        ]
        tagged_paper_ids = {
            paper.paper_id
            for paper in papers
            if any(tag in tag_map and tag_map[tag].theme_id == theme.theme_id for tag in paper.tags)
        }
        missing_notes = sorted(tagged_paper_ids - noted_ids)
        lines.extend(
            [
                f"## {theme.name}",
                "",
                f"- Papers: {len(paper_ids)}",
                f"- Claims: {len(theme_claims)}",
                f"- Strong claims: {len(strong_claims)}",
                f"- Moderate claims: {len(moderate_claims)}",
                f"- Weak/speculative claims: {len(weak_claims)}",
                f"- Claims missing evidence locations: {len(missing_evidence)}",
                f"- Review statements: {len(review_statements)}",
                f"- Primary/contextual evidence: {len(primary_evidence)}",
                f"- Minimum target claims: {theme.min_claims}",
                f"- Minimum target papers: {theme.min_papers}",
                "",
                "### Papers supporting the theme",
            ]
        )
        if paper_ids:
            for paper_id in paper_ids:
                paper = paper_by_id.get(paper_id)
                if paper:
                    lines.append(f"- {paper.paper_id}: {paper.title} ({paper.year})")
                else:
                    lines.append(f"- {paper_id}")
        else:
            lines.append("- None yet.")
        lines.extend(
            [
                "",
                "### Strongest claims",
            ]
        )
        if strong_claims:
            for claim in strong_claims:
                paper = paper_by_id.get(claim.paper_id)
                label = f"{paper.title} ({paper.year})" if paper else claim.paper_id
                lines.append(f"- {label}: {claim.claim_text}")
        else:
            lines.append("- None yet.")
        lines.extend(["", "### Moderate claims"])
        if moderate_claims:
            for claim in moderate_claims:
                lines.append(f"- {claim.claim_id}: {claim.claim_text}")
        else:
            lines.append("- None marked moderate.")
        lines.extend(["", "### Weakly supported claims"])
        if weak_claims:
            for claim in weak_claims:
                lines.append(f"- {claim.claim_id}: {claim.claim_text}")
        else:
            lines.append("- None marked weak/speculative.")
        lines.extend(["", "### Missing evidence"])
        if missing_evidence:
            for claim in missing_evidence:
                lines.append(f"- {claim.claim_id}: add a section/page/figure/table location.")
        else:
            lines.append("- No missing evidence locations in mapped claims.")
        lines.extend(["", "### Missing notes"])
        if missing_notes:
            for paper_id in missing_notes:
                lines.append(f"- {paper_id}: tagged for this theme but no parsed note.")
        else:
            lines.append("- No missing notes among papers tagged for this theme.")
        lines.extend(["", "### Suggested follow-up reading actions"])
        if len(theme_claims) < theme.min_claims:
            lines.append(f"- Add {theme.min_claims - len(theme_claims)} more verified claim(s) for this theme.")
        if len(paper_ids) < theme.min_papers:
            lines.append(f"- Add evidence from {theme.min_papers - len(paper_ids)} more paper(s) for this theme.")
        if missing_evidence:
            lines.append("- Re-open notes with missing evidence locations before citing them.")
        if review_statements and not primary_evidence:
            lines.append("- Find direct evidence; this theme currently relies on review statements.")
        if missing_notes:
            lines.append("- Add notes for tagged papers before treating theme coverage as complete.")
        if not theme_claims:
            lines.append("- Identify papers tagged for this theme and add structured claim blocks.")
        lines.append("")
    unmapped = grouped.get("unmapped", [])
    if unmapped:
        lines.extend(["## Unmapped Claims", ""])
        for claim in unmapped:
            lines.append(f"- {claim.claim_id}: {claim.claim_text}")
    return "\n".join(lines).rstrip() + "\n"


def citation_audit_report(findings: list[CitationAuditFinding]) -> str:
    lines = ["# Citation Audit Report", "", _finding_rows(findings)]
    return "\n".join(lines).rstrip() + "\n"


def theme_coverage_dashboard_report(papers: list[Paper], claims: list[Claim], themes, notes: list[PaperNote]) -> str:
    grouped = group_claims_by_theme(claims, themes)
    tag_map = theme_by_tag(themes)
    noted_ids = {note.paper_id for note in notes if note.paper_id}
    lines = [
        "# Theme Coverage Dashboard",
        "",
        "| Theme | Papers | Claims | Strong | Moderate | Weak | Missing evidence | Missing notes | Follow-up priority |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for theme in themes:
        theme_claims = grouped.get(theme.theme_id, [])
        paper_ids = {claim.paper_id for claim in theme_claims if claim.paper_id}
        tagged_papers = {
            paper.paper_id
            for paper in papers
            if any(tag in tag_map and tag_map[tag].theme_id == theme.theme_id for tag in paper.tags)
        }
        missing_notes = len([paper_id for paper_id in tagged_papers if paper_id not in noted_ids])
        strong = len([claim for claim in theme_claims if claim.strength == "strong"])
        moderate = len([claim for claim in theme_claims if claim.strength == "moderate"])
        weak = len([claim for claim in theme_claims if claim.strength in {"weak", "speculative"}])
        missing_evidence = len([claim for claim in theme_claims if not (claim.section or claim.page)])
        priority = "high" if len(theme_claims) < theme.min_claims or len(paper_ids) < theme.min_papers or missing_notes or missing_evidence else "normal"
        lines.append(f"| {theme.name} | {len(paper_ids)} | {len(theme_claims)} | {strong} | {moderate} | {weak} | {missing_evidence} | {missing_notes} | {priority} |")
    return "\n".join(lines).rstrip() + "\n"


def missing_evidence_report(claims: list[Claim]) -> str:
    missing = [claim for claim in claims if not (claim.section or claim.page)]
    lines = ["# Missing Evidence Report", "", f"Claims missing evidence locations: {len(missing)}", ""]
    for claim in missing:
        lines.append(f"- **{claim.claim_id}** ({claim.paper_id}): {claim.claim_text}")
    return "\n".join(lines).rstrip() + "\n"


def workspace_health_report(findings: list[ValidationFinding]) -> str:
    lines = ["# Workspace Health Report", "", _finding_rows(findings)]
    return "\n".join(lines).rstrip() + "\n"


def _theme_for_query(theme_query: str, themes: list[ProjectTheme]) -> ProjectTheme | None:
    wanted = normalize_tag(theme_query)
    for theme in themes:
        if theme.theme_id == wanted or normalize_tag(theme.name) == wanted:
            return theme
    return None


def section_outline_report(
    theme_query: str,
    papers: list[Paper],
    claims: list[Claim],
    themes: list[ProjectTheme],
    notes: list[PaperNote],
) -> str:
    theme = _theme_for_query(theme_query, themes)
    if theme is None:
        return f"# Literature Review Section Outline\n\nTheme not found: {theme_query}\n"
    grouped = group_claims_by_theme(claims, themes)
    theme_claims = grouped.get(theme.theme_id, [])
    paper_by_id = {paper.paper_id: paper for paper in papers}
    notes_by_id = {note.paper_id: note for note in notes if note.paper_id}
    strong = [claim for claim in theme_claims if claim.strength in {"strong", "moderate"}]
    weak = [claim for claim in theme_claims if claim.strength in {"weak", "speculative"}]
    methods = [claim for claim in theme_claims if claim.evidence_type == EvidenceType.METHOD_DESCRIPTION.value]
    limitations = [claim for claim in theme_claims if claim.evidence_type == EvidenceType.LIMITATION.value]
    missing = [claim for claim in theme_claims if not (claim.section or claim.page)]
    paper_ids = sorted({claim.paper_id for claim in theme_claims if claim.paper_id})
    lines = [
        f"# Literature Review Section Outline: {theme.name}",
        "",
        "This is an evidence outline, not a drafted literature-review section.",
        "",
        f"- Candidate subsection title: {theme.name}",
        f"- Supporting papers: {len(paper_ids)}",
        f"- Tracked claims: {len(theme_claims)}",
        "",
        "## Key Papers",
    ]
    if paper_ids:
        for paper_id in paper_ids:
            paper = paper_by_id.get(paper_id)
            if paper:
                citation = f" [{paper.bibtex_key}]" if paper.bibtex_key else " [missing BibTeX key]"
                lines.append(f"- {paper.paper_id}: {paper.title} ({paper.year}){citation}")
            else:
                lines.append(f"- {paper_id}")
    else:
        lines.append("- None yet.")
    lines.extend(["", "## Strongest Claims"])
    if strong:
        for claim in strong:
            evidence = claim.section or claim.page or "missing evidence location"
            lines.append(f"- {claim.claim_id} ({claim.strength}; {evidence}): {claim.claim_text}")
    else:
        lines.append("- None marked strong or moderate.")
    lines.extend(["", "## Methodological Evidence"])
    if methods:
        for claim in methods:
            lines.append(f"- {claim.claim_id}: {claim.claim_text}")
    else:
        lines.append("- No method-description claims mapped to this theme.")
    lines.extend(["", "## Limitations and Caveats"])
    if limitations:
        for claim in limitations:
            lines.append(f"- {claim.claim_id}: {claim.claim_text}")
    for paper_id in paper_ids:
        note = notes_by_id.get(paper_id)
        if note and note.limitations:
            lines.append(f"- {paper_id}: {note.limitations}")
    if len(lines) >= 2 and lines[-1] == "## Limitations and Caveats":
        lines.append("- None recorded.")
    lines.extend(["", "## Unresolved Questions"])
    questions: list[str] = []
    for paper_id in paper_ids:
        note = notes_by_id.get(paper_id)
        if note:
            questions.extend([f"{paper_id}: {question}" for question in note.user_questions])
    if questions:
        lines.extend(f"- {question}" for question in questions)
    else:
        lines.append("- None recorded.")
    lines.extend(["", "## Suggested Paragraph Order"])
    if strong:
        lines.append("- Start with the strongest direct evidence claims.")
    if methods:
        lines.append("- Follow with method-description claims that explain how evidence was produced.")
    if limitations or any(notes_by_id.get(paper_id) and notes_by_id[paper_id].limitations for paper_id in paper_ids):
        lines.append("- Close with limitations, caveats, and unresolved questions.")
    if not theme_claims:
        lines.append("- Add verified claims before drafting this subsection.")
    lines.extend(["", "## Citations to Include"])
    keys = [paper_by_id[paper_id].bibtex_key for paper_id in paper_ids if paper_id in paper_by_id and paper_by_id[paper_id].bibtex_key]
    if keys:
        lines.extend(f"- {key}" for key in sorted(set(keys)))
    else:
        lines.append("- None with BibTeX keys.")
    lines.extend(["", "## Too Weak to Use Confidently"])
    if weak:
        for claim in weak:
            lines.append(f"- {claim.claim_id} ({claim.strength}, {claim.confidence or 'no confidence'}): {claim.claim_text}")
    else:
        lines.append("- None marked weak/speculative.")
    lines.extend(["", "## Missing Evidence to Address Before Writing"])
    if missing:
        for claim in missing:
            lines.append(f"- {claim.claim_id}: add evidence location.")
    else:
        lines.append("- No mapped claims are missing evidence locations.")
    return "\n".join(lines).rstrip() + "\n"


def build_citation_audit_report(
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    entries: list[BibTeXEntry],
    themes,
    root: str | Path = ".",
) -> str:
    return citation_audit_report(citation_audit(papers, notes, claims, entries, themes, root=root))
