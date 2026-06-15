"""Terminal dashboard and next-action aggregation.

The dashboard is a read-only view over local project data. It summarizes
existing registry, note, claim, citation, rule, reading, and audit-log state;
it does not infer paper content or modify user data.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from . import __version__
from .claim_lifecycle import ClaimReviewItem
from .reading import FollowUpAction, ReadingQueueItem
from .schema import BibTeXEntry, CitationAuditFinding, Claim, Paper, PaperNote, ProjectProfile, ProjectTheme, ValidationFinding


PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
LOW_CONFIDENCE = {"low", "weak", "uncertain", "speculative", "needs-check", "needs_check"}


@dataclass(slots=True)
class NextAction:
    action_id: str
    project: str
    priority: str
    reason: str
    command: str = ""
    related: str = ""


@dataclass(slots=True)
class Dashboard:
    project: str
    root: str
    project_names: list[str] = field(default_factory=list)
    paper_count: int = 0
    note_count: int = 0
    claim_count: int = 0
    bibtex_count: int = 0
    theme_count: int = 0
    reading_status_counts: dict[str, int] = field(default_factory=dict)
    missing_note_papers: list[Paper] = field(default_factory=list)
    weak_claims: list[Claim] = field(default_factory=list)
    missing_evidence_claims: list[Claim] = field(default_factory=list)
    bibtex_findings: list[ValidationFinding] = field(default_factory=list)
    citation_findings: list[CitationAuditFinding] = field(default_factory=list)
    health_findings: list[ValidationFinding] = field(default_factory=list)
    rule_findings: list[Any] = field(default_factory=list)
    manuscript_findings: list[Any] = field(default_factory=list)
    reading_queue: list[ReadingQueueItem] = field(default_factory=list)
    followups: list[FollowUpAction] = field(default_factory=list)
    audit_events: list[dict[str, object]] = field(default_factory=list)
    report_paths: list[str] = field(default_factory=list)
    graph_orphan_papers: list[str] = field(default_factory=list)
    graph_isolated_themes: list[str] = field(default_factory=list)
    graph_review_heavy_themes: list[str] = field(default_factory=list)
    graph_central_papers: list[tuple[str, str, int]] = field(default_factory=list)
    claim_review_queue: list[ClaimReviewItem] = field(default_factory=list)
    next_actions: list[NextAction] = field(default_factory=list)


def build_dashboard(
    *,
    project: str,
    root: str | Path,
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    bibtex_entries: list[BibTeXEntry],
    themes: list[ProjectTheme],
    project_profiles: Iterable[ProjectProfile] = (),
    bibtex_findings: list[ValidationFinding] | None = None,
    citation_findings: list[CitationAuditFinding] | None = None,
    health_findings: list[ValidationFinding] | None = None,
    rule_findings: list[Any] | None = None,
    manuscript_findings: list[Any] | None = None,
    reading_queue: list[ReadingQueueItem] | None = None,
    followups: list[FollowUpAction] | None = None,
    audit_events: list[dict[str, object]] | None = None,
    report_paths: Iterable[str | Path] = (),
    graph_analytics: Any | None = None,
    claim_review_queue: list[ClaimReviewItem] | None = None,
    limit: int = 10,
) -> Dashboard:
    note_ids = {note.paper_id for note in notes if note.paper_id}
    missing_note_papers = [paper for paper in papers if paper.paper_id not in note_ids]
    weak_claims = [
        claim
        for claim in claims
        if claim.strength in {"weak", "speculative"} or claim.confidence.strip().lower() in LOW_CONFIDENCE
    ]
    missing_evidence_claims = [claim for claim in claims if not (claim.section or claim.page)]
    dashboard = Dashboard(
        project=project,
        root=str(root),
        project_names=[profile.name for profile in project_profiles],
        paper_count=len(papers),
        note_count=len(notes),
        claim_count=len(claims),
        bibtex_count=len(bibtex_entries),
        theme_count=len(themes),
        reading_status_counts=dict(Counter(paper.reading_status for paper in papers)),
        missing_note_papers=missing_note_papers,
        weak_claims=weak_claims,
        missing_evidence_claims=missing_evidence_claims,
        bibtex_findings=list(bibtex_findings or []),
        citation_findings=list(citation_findings or []),
        health_findings=list(health_findings or []),
        rule_findings=list(rule_findings or []),
        manuscript_findings=list(manuscript_findings or []),
        reading_queue=list(reading_queue or []),
        followups=list(followups or []),
        audit_events=list(audit_events or []),
        report_paths=[str(path) for path in report_paths],
        graph_orphan_papers=list(getattr(graph_analytics, "orphan_papers", []) if graph_analytics else []),
        graph_isolated_themes=list(getattr(graph_analytics, "isolated_themes", []) if graph_analytics else []),
        graph_review_heavy_themes=list(getattr(graph_analytics, "review_paper_heavy_themes", []) if graph_analytics else []),
        graph_central_papers=list(getattr(graph_analytics, "central_papers", []) if graph_analytics else []),
        claim_review_queue=list(claim_review_queue or []),
    )
    dashboard.next_actions = build_next_actions(dashboard, limit=limit)
    return dashboard


def build_next_actions(dashboard: Dashboard, *, limit: int = 10) -> list[NextAction]:
    actions: list[NextAction] = []
    project_flag = _project_flag(dashboard.project)
    for finding in _filter_severity(dashboard.health_findings, "error")[:3]:
        actions.append(
            NextAction(
                action_id=f"health:{_code(finding)}:{_identifier(finding)}",
                project=dashboard.project,
                priority="critical",
                reason=f"Workspace health error: {_message(finding)}",
                command=f"paperwb doctor{project_flag}",
                related=_identifier(finding),
            )
        )
    for finding in _filter_severity(dashboard.rule_findings, "error")[:3]:
        actions.append(
            NextAction(
                action_id=f"rule:{_rule_id(finding)}:{_identifier(finding)}",
                project=dashboard.project,
                priority="high",
                reason=f"Rule violation: {_message(finding)}",
                command=f"paperwb rules report{project_flag}",
                related=_identifier(finding),
            )
        )
    for item in dashboard.claim_review_queue[:5]:
        actions.append(
            NextAction(
                action_id=f"claim_review:{item.claim_id}",
                project=dashboard.project,
                priority=item.priority,
                reason=f"{item.claim_id} needs claim review: {'; '.join(item.reasons[:2])}.",
                command=f"paperwb claim-review queue{project_flag}",
                related=item.claim_id,
            )
        )
    for paper in dashboard.missing_note_papers[:5]:
        priority = "high" if paper.included_in_lit_review.strip().lower() in {"true", "yes", "1", "included"} else "medium"
        actions.append(
            NextAction(
                action_id=f"missing_note:{paper.paper_id}",
                project=dashboard.project,
                priority=priority,
                reason=f"{paper.paper_id} has no parsed structured note.",
                command=f"paperwb note-template {paper.paper_id}{project_flag}",
                related=paper.paper_id,
            )
        )
    for claim in dashboard.missing_evidence_claims[:5]:
        actions.append(
            NextAction(
                action_id=f"missing_evidence:{claim.claim_id}",
                project=dashboard.project,
                priority="high",
                reason=f"{claim.claim_id} has no section/page evidence location.",
                command=f"paperwb report citation-audit{project_flag}",
                related=claim.claim_id,
            )
        )
    for finding in _filter_severity(dashboard.bibtex_findings, "error")[:3]:
        actions.append(
            NextAction(
                action_id=f"bibtex:{_code(finding)}:{_identifier(finding)}",
                project=dashboard.project,
                priority="high",
                reason=f"BibTeX issue: {_message(finding)}",
                command=_validate_bib_command(dashboard.project),
                related=_identifier(finding),
            )
        )
    for finding in dashboard.citation_findings[:5]:
        code = _code(finding)
        if code not in {"theme_under_supported", "theme_too_few_papers", "theme_only_review_statements", "included_paper_with_weak_evidence"}:
            continue
        actions.append(
            NextAction(
                action_id=f"citation:{code}:{_identifier(finding)}",
                project=dashboard.project,
                priority="medium",
                reason=f"Citation audit warning: {_message(finding)}",
                command=f"paperwb report evidence-map{project_flag}",
                related=_identifier(finding),
            )
        )
    for paper_id in dashboard.graph_orphan_papers[:3]:
        actions.append(
            NextAction(
                action_id=f"graph_orphan_paper:{paper_id}",
                project=dashboard.project,
                priority="medium",
                reason=f"{paper_id} has no note, claim, or theme connection in the evidence graph.",
                command=f"paperwb graph summary{project_flag}",
                related=paper_id,
            )
        )
    for theme_id in dashboard.graph_isolated_themes[:3]:
        actions.append(
            NextAction(
                action_id=f"graph_isolated_theme:{theme_id}",
                project=dashboard.project,
                priority="medium",
                reason=f"{theme_id} has no paper or claim connection in the evidence graph.",
                command=f"paperwb graph summary{project_flag}",
                related=theme_id,
            )
        )
    for claim in dashboard.weak_claims[:3]:
        actions.append(
            NextAction(
                action_id=f"weak_claim:{claim.claim_id}",
                project=dashboard.project,
                priority="medium",
                reason=f"{claim.claim_id} is weak/speculative or low-confidence.",
                command=f"paperwb report weak-claims{project_flag}",
                related=claim.claim_id,
            )
        )
    for finding in dashboard.manuscript_findings[:5]:
        actions.append(
            NextAction(
                action_id=f"manuscript:{_code(finding)}:{_identifier(finding)}",
                project=dashboard.project,
                priority="medium",
                reason=f"Manuscript QA warning: {_message(finding)}",
                command=f"paperwb manuscript qa DRAFT.md{project_flag}",
                related=_identifier(finding),
            )
        )
    for followup in dashboard.followups[:5]:
        actions.append(
            NextAction(
                action_id=f"followup:{followup.action_id}",
                project=dashboard.project,
                priority="medium",
                reason=followup.text,
                command=f"paperwb followups list{project_flag}",
                related=followup.paper_id,
            )
        )
    for item in dashboard.reading_queue[:5]:
        actions.append(
            NextAction(
                action_id=f"read:{item.paper_id}",
                project=dashboard.project,
                priority="low",
                reason=f"Read next: {item.title} ({'; '.join(item.reasons[:3])}).",
                command=f"paperwb reading start {item.paper_id}{project_flag}",
                related=item.paper_id,
            )
        )
    actions.append(
        NextAction(
            action_id="maintenance:backup",
            project=dashboard.project,
            priority="low",
            reason="Create a local backup before major imports, sync applies, migrations, or restore tests.",
            command=f"paperwb backup create{project_flag}",
            related="workspace",
        )
    )
    return _dedupe_actions(actions)[:limit]


def dashboard_terminal(dashboard: Dashboard, *, view: str = "full", limit: int = 10) -> str:
    if view == "next-actions":
        return _terminal_next_actions(dashboard.next_actions[:limit])
    if view == "health":
        return _terminal_health(dashboard)
    lines = [
        f"Paper Workbench Dashboard - {dashboard.project}",
        "=" * (28 + len(dashboard.project)),
        f"Papers: {dashboard.paper_count} | Notes: {dashboard.note_count} | Claims: {dashboard.claim_count} | BibTeX: {dashboard.bibtex_count} | Themes: {dashboard.theme_count}",
        f"Projects: {', '.join(dashboard.project_names) if dashboard.project_names else '[none found]'}",
        "",
        "Reading status:",
    ]
    for status, count in sorted(dashboard.reading_status_counts.items()):
        lines.append(f"  - {status}: {count}")
    if not dashboard.reading_status_counts:
        lines.append("  - no papers loaded")
    lines.extend(
        [
            "",
            "Issue summary:",
            f"  - Missing parsed notes: {len(dashboard.missing_note_papers)}",
            f"  - Weak/low-confidence claims: {len(dashboard.weak_claims)}",
            f"  - Claims missing evidence locations: {len(dashboard.missing_evidence_claims)}",
            f"  - Claim review queue: {len(dashboard.claim_review_queue)}",
            f"  - BibTeX findings: {_severity_summary(dashboard.bibtex_findings)}",
            f"  - Citation audit findings: {_severity_summary(dashboard.citation_findings)}",
            f"  - Workspace health findings: {_severity_summary(dashboard.health_findings)}",
            f"  - Rule findings: {_severity_summary(dashboard.rule_findings)}",
            f"  - Manuscript QA findings: {_severity_summary(dashboard.manuscript_findings)}",
            f"  - Graph orphan papers: {len(dashboard.graph_orphan_papers)}",
            f"  - Graph isolated themes: {len(dashboard.graph_isolated_themes)}",
            "",
            "Top next actions:",
        ]
    )
    lines.extend(_terminal_action_lines(dashboard.next_actions[:limit]))
    lines.extend(["", "Reading queue:"])
    if dashboard.reading_queue:
        for item in dashboard.reading_queue[:limit]:
            lines.append(f"  - {item.paper_id} [{item.score}]: {item.title}")
    else:
        lines.append("  - No reading queue items matched.")
    lines.extend(["", "Open follow-ups:"])
    if dashboard.followups:
        for action in dashboard.followups[:limit]:
            lines.append(f"  - {action.action_id}: {action.text}")
    else:
        lines.append("  - No open follow-up actions.")
    return "\n".join(lines).rstrip() + "\n"


def dashboard_markdown(dashboard: Dashboard, *, title: str = f"Terminal Dashboard v{__version__}", limit: int = 20) -> str:
    lines = [
        f"# {title}",
        "",
        "This dashboard summarizes local project state only. It does not modify user data, use cloud services, or infer paper content.",
        "",
        f"Project: {dashboard.project}",
        f"Root: `{_escape(dashboard.root)}`",
        f"Projects discovered: {len(dashboard.project_names)}",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Papers | {dashboard.paper_count} |",
        f"| Notes | {dashboard.note_count} |",
        f"| Claims | {dashboard.claim_count} |",
        f"| BibTeX entries | {dashboard.bibtex_count} |",
        f"| Themes | {dashboard.theme_count} |",
        f"| Missing parsed notes | {len(dashboard.missing_note_papers)} |",
        f"| Weak/low-confidence claims | {len(dashboard.weak_claims)} |",
        f"| Claims missing evidence locations | {len(dashboard.missing_evidence_claims)} |",
        f"| Claim review queue | {len(dashboard.claim_review_queue)} |",
        f"| Graph orphan papers | {len(dashboard.graph_orphan_papers)} |",
        f"| Graph isolated themes | {len(dashboard.graph_isolated_themes)} |",
        f"| Graph review-heavy themes | {len(dashboard.graph_review_heavy_themes)} |",
        "",
        "## Reading Status",
        "",
        "| Status | Papers |",
        "| --- | ---: |",
    ]
    if dashboard.reading_status_counts:
        for status, count in sorted(dashboard.reading_status_counts.items()):
            lines.append(f"| {_escape(status)} | {count} |")
    else:
        lines.append("| none | 0 |")
    lines.extend(["", "## Issue Counts", "", _finding_count_table(dashboard)])
    lines.extend(["", "## Next Actions", "", next_actions_table(dashboard.next_actions[:limit])])
    lines.extend(["", "## Reading Queue", "", _reading_queue_table(dashboard.reading_queue[:limit])])
    lines.extend(["", "## Open Follow-ups", "", _followups_table(dashboard.followups[:limit])])
    lines.extend(["", "## Recent Audit Events", "", _audit_events_table(dashboard.audit_events[:limit])])
    lines.extend(["", "## Generated Reports", ""])
    if dashboard.report_paths:
        for path in dashboard.report_paths[:limit]:
            lines.append(f"- `{_escape(path)}`")
    else:
        lines.append("- No Markdown reports found.")
    return "\n".join(lines).rstrip() + "\n"


def next_actions_markdown(actions: list[NextAction], *, title: str = f"Next Actions v{__version__}") -> str:
    return "\n".join([f"# {title}", "", next_actions_table(actions)]).rstrip() + "\n"


def project_health_summary_markdown(dashboard: Dashboard, *, title: str = f"Project Health Summary v{__version__}") -> str:
    lines = [
        f"# {title}",
        "",
        f"Project: {dashboard.project}",
        "",
        "## Counts",
        "",
        "| Area | Errors | Warnings | Info |",
        "| --- | ---: | ---: | ---: |",
        _severity_row("BibTeX", dashboard.bibtex_findings),
        _severity_row("Citation audit", dashboard.citation_findings),
        _severity_row("Workspace health", dashboard.health_findings),
        _severity_row("Rules", dashboard.rule_findings),
        _severity_row("Manuscript QA", dashboard.manuscript_findings),
        "",
        "## Gaps",
        "",
        f"- Missing parsed notes: {len(dashboard.missing_note_papers)}",
        f"- Weak/low-confidence claims: {len(dashboard.weak_claims)}",
        f"- Claims missing evidence locations: {len(dashboard.missing_evidence_claims)}",
        f"- Graph orphan papers: {len(dashboard.graph_orphan_papers)}",
        f"- Graph isolated themes: {len(dashboard.graph_isolated_themes)}",
        f"- Graph review-heavy themes: {len(dashboard.graph_review_heavy_themes)}",
        "",
        "## Highest Priority Actions",
        "",
        next_actions_table(dashboard.next_actions[:10]),
    ]
    return "\n".join(lines).rstrip() + "\n"


def next_actions_table(actions: list[NextAction]) -> str:
    lines = ["| Priority | Action ID | Reason | Command | Related |", "| --- | --- | --- | --- | --- |"]
    if not actions:
        lines.append("|  |  | No next actions generated. |  |  |")
    for action in actions:
        lines.append(
            f"| {_escape(action.priority)} | `{_escape(action.action_id)}` | {_escape(action.reason)} | `{_escape(action.command)}` | {_escape(action.related)} |"
        )
    return "\n".join(lines)


def _terminal_next_actions(actions: list[NextAction]) -> str:
    lines = ["Next Actions", "============"]
    lines.extend(_terminal_action_lines(actions))
    return "\n".join(lines).rstrip() + "\n"


def _terminal_health(dashboard: Dashboard) -> str:
    lines = [
        f"Project Health - {dashboard.project}",
        "=" * (17 + len(dashboard.project)),
        f"BibTeX: {_severity_summary(dashboard.bibtex_findings)}",
        f"Citation audit: {_severity_summary(dashboard.citation_findings)}",
        f"Workspace health: {_severity_summary(dashboard.health_findings)}",
        f"Rules: {_severity_summary(dashboard.rule_findings)}",
        f"Manuscript QA: {_severity_summary(dashboard.manuscript_findings)}",
        f"Missing notes: {len(dashboard.missing_note_papers)}",
        f"Weak claims: {len(dashboard.weak_claims)}",
        f"Missing evidence locations: {len(dashboard.missing_evidence_claims)}",
        f"Graph orphan papers: {len(dashboard.graph_orphan_papers)}",
        f"Graph isolated themes: {len(dashboard.graph_isolated_themes)}",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _terminal_action_lines(actions: list[NextAction]) -> list[str]:
    if not actions:
        return ["  - No next actions generated."]
    return [f"  - [{action.priority}] {action.action_id}: {action.reason} ({action.command})" for action in actions]


def _finding_count_table(dashboard: Dashboard) -> str:
    lines = ["| Source | Errors | Warnings | Info |", "| --- | ---: | ---: | ---: |"]
    lines.append(_severity_row("BibTeX", dashboard.bibtex_findings))
    lines.append(_severity_row("Citation audit", dashboard.citation_findings))
    lines.append(_severity_row("Workspace health", dashboard.health_findings))
    lines.append(_severity_row("Rules", dashboard.rule_findings))
    lines.append(_severity_row("Manuscript QA", dashboard.manuscript_findings))
    return "\n".join(lines)


def _severity_row(label: str, findings: Iterable[Any]) -> str:
    counts = Counter(_severity(finding) for finding in findings)
    return f"| {_escape(label)} | {counts.get('error', 0)} | {counts.get('warning', 0)} | {counts.get('info', 0)} |"


def _reading_queue_table(items: list[ReadingQueueItem]) -> str:
    lines = ["| Rank | Score | Paper ID | Status | Title | Reasons |", "| ---: | ---: | --- | --- | --- | --- |"]
    if not items:
        lines.append("| 0 | 0 |  |  | No reading queue items matched. |  |")
    for index, item in enumerate(items, start=1):
        lines.append(f"| {index} | {item.score} | {_escape(item.paper_id)} | {_escape(item.reading_status)} | {_escape(item.title)} | {_escape('; '.join(item.reasons))} |")
    return "\n".join(lines)


def _followups_table(actions: list[FollowUpAction]) -> str:
    lines = ["| Action ID | Paper ID | Theme | Action |", "| --- | --- | --- | --- |"]
    if not actions:
        lines.append("|  |  |  | No open follow-up actions. |")
    for action in actions:
        lines.append(f"| `{_escape(action.action_id)}` | {_escape(action.paper_id)} | {_escape(action.theme)} | {_escape(action.text)} |")
    return "\n".join(lines)


def _audit_events_table(events: list[dict[str, object]]) -> str:
    lines = ["| Timestamp | Action | Success | Summary |", "| --- | --- | --- | --- |"]
    if not events:
        lines.append("|  | none | true | No audit events found. |")
    for event in events:
        lines.append(
            "| {timestamp} | {action} | {success} | {summary} |".format(
                timestamp=_escape(event.get("timestamp", "")),
                action=_escape(event.get("action", "")),
                success=_escape(event.get("success", "")),
                summary=_escape(event.get("summary", "")),
            )
        )
    return "\n".join(lines)


def _filter_severity(findings: Iterable[Any], severity: str) -> list[Any]:
    return [finding for finding in findings if _severity(finding) == severity]


def _severity_summary(findings: Iterable[Any]) -> str:
    counts = Counter(_severity(finding) for finding in findings)
    return f"{counts.get('error', 0)} error(s), {counts.get('warning', 0)} warning(s), {counts.get('info', 0)} info"


def _severity(finding: Any) -> str:
    return str(getattr(finding, "severity", "") or "").lower()


def _message(finding: Any) -> str:
    return str(getattr(finding, "message", "") or "")


def _identifier(finding: Any) -> str:
    for field_name in ("identifier", "paper_id", "claim_id", "theme", "citation_key", "paragraph_id"):
        value = getattr(finding, field_name, "")
        if value:
            return str(value)
    return ""


def _code(finding: Any) -> str:
    return str(getattr(finding, "code", "") or getattr(finding, "rule_id", "") or "")


def _rule_id(finding: Any) -> str:
    return str(getattr(finding, "rule_id", "") or _code(finding))


def _project_flag(project: str) -> str:
    return "" if project == "default" else f" --project {project}"


def _validate_bib_command(project: str) -> str:
    if project == "default":
        return "paperwb validate-bib data/bibtex/library.bib --registry data/registries/papers.csv"
    return f"paperwb validate-bib projects/{project}/bibtex/library.bib --registry projects/{project}/registry.csv"


def _dedupe_actions(actions: list[NextAction]) -> list[NextAction]:
    seen: set[str] = set()
    unique: list[NextAction] = []
    for action in sorted(actions, key=lambda item: (PRIORITY_ORDER.get(item.priority, 9), item.action_id)):
        dedupe_key = _action_dedupe_key(action)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        unique.append(action)
    return unique


def _action_dedupe_key(action: NextAction) -> str:
    action_text = f"{action.action_id} {action.reason}".lower()
    related = action.related or action.action_id
    if (
        "claim_missing_evidence_location" in action_text
        or "missing_evidence" in action.action_id
        or "no section/page evidence location" in action_text
        or "has no section or page evidence location" in action_text
    ):
        return f"missing_evidence_location:{related}"
    return f"action:{action.action_id}"


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")
