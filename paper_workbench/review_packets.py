"""Local file-based collaboration review packets.

Review packets are export artifacts for manual review. Imported reviewer
comments are stored as separate sidecar metadata and never rewrite registry
rows, notes, claims, or evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Iterable

from . import __version__
from .authoring import (
    build_claim_bank,
    build_citation_bank,
    build_evidence_matrix,
    citation_bank_report,
    claim_bank_report,
    evidence_matrix_report,
)
from .drafts import draft_audit_markdown, parse_markdown_draft
from .io import load_json, read_csv_rows, write_csv_rows, write_json, write_text
from .paths import display_path
from .reporting import missing_evidence_report
from .schema import BibTeXEntry, Claim, Paper, PaperNote, ProjectTheme, dataclass_to_plain
from .tags import normalize_tag, parse_tags, theme_by_tag, themes_for_tags


REVIEW_ITEM_TYPES = {"paper", "claim", "theme", "paragraph", "citation", "evidence_gap"}
REVIEW_STATUSES = {"open", "resolved", "needs_reread", "needs_citation_check", "weak_evidence", "accepted", "rejected"}
COMMENT_FIELDS = [
    "comment_id",
    "item_id",
    "item_type",
    "reviewer",
    "status",
    "comment",
    "recommendation",
    "requires_reread",
    "requires_citation_check",
    "weak_evidence",
    "created_at",
]


@dataclass(slots=True)
class ReviewItem:
    item_id: str
    item_type: str
    label: str
    paper_id: str = ""
    claim_id: str = ""
    theme: str = ""
    citation_key: str = ""
    evidence_status: str = ""
    review_prompt: str = ""


@dataclass(slots=True)
class ReviewPacket:
    packet_id: str
    project: str
    created_at: str
    output_dir: str
    theme: str = ""
    draft_path: str = ""
    items: list[ReviewItem] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ReviewerComment:
    comment_id: str
    item_id: str
    item_type: str
    reviewer: str = ""
    status: str = "open"
    comment: str = ""
    recommendation: str = ""
    requires_reread: bool = False
    requires_citation_check: bool = False
    weak_evidence: bool = False
    created_at: str = ""
    source_path: str = ""


@dataclass(slots=True)
class ReviewImportResult:
    project: str
    comments: list[ReviewerComment] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    dry_run: bool = True
    output_path: str = ""


@dataclass(slots=True)
class ReviewResponse:
    project: str
    comments: list[ReviewerComment] = field(default_factory=list)
    unknown_item_comments: list[ReviewerComment] = field(default_factory=list)

    @property
    def unresolved(self) -> list[ReviewerComment]:
        return [comment for comment in self.comments if comment.status not in {"resolved", "accepted", "rejected"}]

    @property
    def reread(self) -> list[ReviewerComment]:
        return [comment for comment in self.comments if comment.requires_reread or comment.status == "needs_reread"]

    @property
    def citation_checks(self) -> list[ReviewerComment]:
        return [comment for comment in self.comments if comment.requires_citation_check or comment.status == "needs_citation_check"]

    @property
    def weak_evidence(self) -> list[ReviewerComment]:
        return [comment for comment in self.comments if comment.weak_evidence or comment.status == "weak_evidence"]


def default_review_comments_path(root: str | Path) -> Path:
    return Path(root) / ".paperwb" / "reviewer_comments.json"


def create_review_packet(
    *,
    project: str,
    output_dir: str | Path,
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    entries: list[BibTeXEntry],
    themes: list[ProjectTheme],
    theme: str = "",
    draft_path: str = "",
    force: bool = False,
) -> ReviewPacket:
    if not theme and not draft_path:
        raise ValueError("review packet creation requires --theme or --draft")
    target = Path(output_dir)
    if target.exists() and any(target.iterdir()) and not force:
        raise FileExistsError(f"{target} already exists and is not empty")
    target.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    packet_id = _packet_id(project, theme=theme, draft_path=draft_path, created_at=now)
    items, warnings = build_review_items(papers, notes, claims, themes, entries, theme=theme, draft_path=draft_path)
    packet = ReviewPacket(
        packet_id=packet_id,
        project=project,
        created_at=now,
        output_dir=display_path(target),
        theme=theme,
        draft_path=display_path(draft_path) if draft_path else "",
        items=items,
        warnings=warnings,
    )
    files: list[str] = []

    def write_file(name: str, content: str) -> None:
        path = write_text(target / name, content, force=force)
        files.append(name)

    write_comment_template(items, target / "comments.csv", force=force)
    files.append("comments.csv")
    write_file("review_instructions.md", review_instructions_markdown(packet))

    if theme:
        matrix = build_evidence_matrix(theme, papers, claims, themes, notes, project=project)
        claim_bank = build_claim_bank(theme, claims, themes, project=project)
        citation_bank = build_citation_bank(theme, papers, claims, themes, notes, entries, project=project)
        write_file("evidence_matrix.md", evidence_matrix_report(matrix))
        write_file("claim_bank.md", claim_bank_report(claim_bank))
        write_file("citation_bank.md", citation_bank_report(citation_bank, claims))
        write_file("missing_evidence.md", missing_evidence_report(claims))
    if draft_path:
        document = parse_markdown_draft(draft_path)
        write_file("draft_parse.md", _draft_parse_summary(document.sections, document.paragraphs))
        from .drafts import audit_draft

        draft_audit = audit_draft(document, papers, notes, claims, entries, themes, project=project)
        write_file("draft_audit.md", draft_audit_markdown(draft_audit))

    packet.files = ["overview.md", *files, "manifest.json"]
    write_text(target / "overview.md", review_packet_overview(packet), force=force)
    write_json(target / "manifest.json", review_packet_to_dict(packet), force=force)
    return packet


def build_review_items(
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    themes: list[ProjectTheme],
    entries: list[BibTeXEntry],
    *,
    theme: str = "",
    draft_path: str = "",
) -> tuple[list[ReviewItem], list[str]]:
    items: list[ReviewItem] = []
    warnings: list[str] = []
    note_ids = {note.paper_id for note in notes}
    entry_keys = {entry.key for entry in entries}
    selected_theme = _find_theme(theme, themes) if theme else None
    selected_theme_id = selected_theme.theme_id if selected_theme else normalize_tag(theme) if theme else ""
    selected_claims = _claims_for_theme(claims, selected_theme_id, themes) if selected_theme_id else list(claims)
    selected_paper_ids = {claim.paper_id for claim in selected_claims if claim.paper_id}
    if selected_theme:
        selected_paper_ids.update(_paper_ids_for_theme(papers, selected_theme, themes))
        items.append(
            ReviewItem(
                item_id=f"theme:{selected_theme.theme_id}",
                item_type="theme",
                label=selected_theme.name,
                theme=selected_theme.theme_id,
                evidence_status=f"min_papers={selected_theme.min_papers}; min_claims={selected_theme.min_claims}",
                review_prompt="Does this theme have enough local evidence to support writing?",
            )
        )
    elif theme:
        warnings.append(f"Theme not found: {theme}")

    paper_by_id = {paper.paper_id: paper for paper in papers}
    for paper_id in sorted(selected_paper_ids):
        paper = paper_by_id.get(paper_id)
        if paper is None:
            continue
        missing = []
        if paper.paper_id not in note_ids:
            missing.append("missing note")
        if not paper.bibtex_key or paper.bibtex_key not in entry_keys:
            missing.append("missing BibTeX")
        items.append(
            ReviewItem(
                item_id=f"paper:{paper.paper_id}",
                item_type="paper",
                label=paper.title or paper.paper_id,
                paper_id=paper.paper_id,
                theme=selected_theme_id,
                citation_key=paper.bibtex_key,
                evidence_status="; ".join(missing) or "tracked",
                review_prompt="Is this paper being used appropriately for the packet theme or draft?",
            )
        )

    for claim in selected_claims:
        status = []
        if not (claim.section or claim.page):
            status.append("missing evidence location")
        if claim.strength in {"weak", "speculative"}:
            status.append(f"strength={claim.strength}")
        if claim.evidence_type == "review_statement":
            status.append("review statement")
        items.append(
            ReviewItem(
                item_id=f"claim:{claim.claim_id}",
                item_type="claim",
                label=claim.claim_text,
                paper_id=claim.paper_id,
                claim_id=claim.claim_id,
                theme=claim.supports_theme or selected_theme_id,
                evidence_status="; ".join(status) or "tracked",
                review_prompt="Should this claim be kept, weakened, reread, or excluded from writing?",
            )
        )
        if not (claim.section or claim.page):
            items.append(
                ReviewItem(
                    item_id=f"gap:{claim.claim_id}",
                    item_type="evidence_gap",
                    label=f"Missing evidence location for {claim.claim_id}",
                    paper_id=claim.paper_id,
                    claim_id=claim.claim_id,
                    theme=claim.supports_theme or selected_theme_id,
                    evidence_status="missing evidence location",
                    review_prompt="What page, section, or note evidence is needed before this claim is used?",
                )
            )

    if draft_path:
        document = parse_markdown_draft(draft_path)
        for paragraph in document.paragraphs:
            item_id = f"paragraph:{paragraph.paragraph_id}"
            items.append(
                ReviewItem(
                    item_id=item_id,
                    item_type="paragraph",
                    label=paragraph.text[:160],
                    theme=selected_theme_id,
                    evidence_status=f"citations={len(paragraph.citation_keys)}",
                    review_prompt="Does this paragraph have enough local citation and evidence support?",
                )
            )
            for citation_key in paragraph.citation_keys:
                items.append(
                    ReviewItem(
                        item_id=f"citation:{citation_key}",
                        item_type="citation",
                        label=citation_key,
                        citation_key=citation_key,
                        evidence_status="present in draft",
                        review_prompt="Does this citation support the sentence or paragraph where it appears?",
                    )
                )

    return _dedupe_items(items), warnings


def write_comment_template(items: list[ReviewItem], path: str | Path, *, force: bool = True) -> Path:
    rows = []
    for item in items:
        rows.append(
            {
                "comment_id": "",
                "item_id": item.item_id,
                "item_type": item.item_type,
                "reviewer": "",
                "status": "open",
                "comment": "",
                "recommendation": "",
                "requires_reread": "",
                "requires_citation_check": "",
                "weak_evidence": "",
                "created_at": "",
            }
        )
    if not rows:
        rows.append({field: "" for field in COMMENT_FIELDS})
    return write_csv_rows(path, rows, COMMENT_FIELDS, force=force)


def import_reviewer_comments(
    comments_csv: str | Path,
    *,
    project: str,
    output_path: str | Path,
    known_items: Iterable[ReviewItem] = (),
    manifest_path: str | Path | None = None,
    dry_run: bool = True,
    force: bool = False,
) -> ReviewImportResult:
    known_ids = _known_item_ids(known_items, manifest_path=manifest_path)
    rows = read_csv_rows(comments_csv)
    if not rows:
        return ReviewImportResult(project=project, dry_run=dry_run, output_path=display_path(output_path), warnings=["No comment rows found."])
    missing_fields = [field for field in COMMENT_FIELDS if field not in rows[0]]
    result = ReviewImportResult(project=project, dry_run=dry_run, output_path=display_path(output_path))
    if missing_fields:
        result.errors.append(f"Missing required comment field(s): {', '.join(missing_fields)}")
        return result

    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=2):
        if not any(str(row.get(field, "") or "").strip() for field in ("comment_id", "item_id", "comment", "recommendation")):
            continue
        try:
            comment = _comment_from_row(row, source_path=display_path(comments_csv), row_number=index)
        except ValueError as exc:
            result.errors.append(str(exc))
            continue
        if comment.comment_id in seen_ids:
            result.errors.append(f"Row {index}: duplicate comment_id {comment.comment_id!r}.")
            continue
        seen_ids.add(comment.comment_id)
        if known_ids and comment.item_id not in known_ids:
            result.errors.append(f"Row {index}: unknown review item {comment.item_id!r}.")
        result.comments.append(comment)

    if result.errors or dry_run:
        return result

    existing = load_reviewer_comments(output_path)
    merged = {comment.comment_id: comment for comment in existing}
    for comment in result.comments:
        merged[comment.comment_id] = comment
    save_reviewer_comments(output_path, list(merged.values()), force=force)
    return result


def load_reviewer_comments(path: str | Path) -> list[ReviewerComment]:
    target = Path(path)
    if not target.exists():
        return []
    data = load_json(target)
    raw_comments = data.get("comments", []) if isinstance(data, dict) else []
    comments: list[ReviewerComment] = []
    for raw in raw_comments:
        if isinstance(raw, dict):
            comments.append(_comment_from_mapping(raw))
    return comments


def save_reviewer_comments(path: str | Path, comments: list[ReviewerComment], *, force: bool = True) -> Path:
    data = {
        "schema": "paperwb-review-comments-v1",
        "comments": [reviewer_comment_to_dict(comment) for comment in sorted(comments, key=lambda item: item.comment_id)],
    }
    return write_json(path, data, force=force)


def build_review_response(
    comments: list[ReviewerComment],
    *,
    project: str,
    known_items: Iterable[ReviewItem] = (),
) -> ReviewResponse:
    known = {item.item_id for item in known_items}
    unknown = [comment for comment in comments if known and comment.item_id not in known]
    return ReviewResponse(project=project, comments=comments, unknown_item_comments=unknown)


def reviewer_comments_report(comments: list[ReviewerComment], *, project: str) -> str:
    lines = [
        f"# Reviewer Comments v{__version__}",
        "",
        "Boundary: reviewer comments are imported as separate local review metadata. They do not change claims, notes, registry rows, or evidence.",
        "",
        f"Project: {project}",
        f"Comments: {len(comments)}",
        "",
        "| Comment ID | Item | Type | Reviewer | Status | Comment | Recommendation | Flags |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not comments:
        lines.append("|  | No imported reviewer comments. |  |  |  |  |  |  |")
    for comment in sorted(comments, key=lambda item: item.comment_id):
        lines.append(_comment_table_row(comment))
    return "\n".join(lines).rstrip() + "\n"


def response_to_review_report(response: ReviewResponse) -> str:
    lines = [
        f"# Response to Review v{__version__}",
        "",
        "This report turns imported comments into a manual response checklist. It does not accept reviewer comments as truth or edit evidence automatically.",
        "",
        f"Project: {response.project}",
        f"Comments received: {len(response.comments)}",
        f"Unresolved comments: {len(response.unresolved)}",
        f"Comments requiring reread: {len(response.reread)}",
        f"Comments requiring citation check: {len(response.citation_checks)}",
        f"Weak-evidence comments: {len(response.weak_evidence)}",
        f"Unknown linked items: {len(response.unknown_item_comments)}",
        "",
        "## Proposed User Actions",
        "",
    ]
    actions = review_followup_actions(response)
    if actions:
        lines.extend(f"- [ ] {action}" for action in actions)
    else:
        lines.append("- No open reviewer follow-up actions.")
    lines.extend(["", "## Comments", "", "| Comment ID | Item | Status | Action |", "| --- | --- | --- | --- |"])
    if not response.comments:
        lines.append("|  | No imported comments. |  |  |")
    for comment in sorted(response.comments, key=lambda item: item.comment_id):
        action = _action_for_comment(comment)
        lines.append(f"| `{_escape(comment.comment_id)}` | `{_escape(comment.item_id)}` | {_escape(comment.status)} | {_escape(action)} |")
    return "\n".join(lines).rstrip() + "\n"


def review_followups_report(response: ReviewResponse) -> str:
    lines = [
        f"# Review Follow-ups v{__version__}",
        "",
        "These follow-ups are derived from imported reviewer comments. They are manual tasks, not automatic evidence edits.",
        "",
        f"Project: {response.project}",
        "",
    ]
    actions = review_followup_actions(response)
    if not actions:
        lines.append("- No open review follow-ups.")
    else:
        lines.extend(f"- [ ] {action}" for action in actions)
    return "\n".join(lines).rstrip() + "\n"


def review_import_report(result: ReviewImportResult) -> str:
    lines = [
        f"# Reviewer Comment Import v{__version__}",
        "",
        "Boundary: comment import validates and stores reviewer comments separately. It never rewrites claims, notes, or registry metadata.",
        "",
        f"Project: {result.project}",
        f"Dry run: `{str(result.dry_run).lower()}`",
        f"Valid comments: {len(result.comments)}",
        f"Errors: {len(result.errors)}",
        f"Warnings: {len(result.warnings)}",
        f"Output sidecar: `{_escape(result.output_path)}`",
        "",
    ]
    if result.errors:
        lines.extend(["## Errors", "", *[f"- {_escape(error)}" for error in result.errors], ""])
    if result.warnings:
        lines.extend(["## Warnings", "", *[f"- {_escape(warning)}" for warning in result.warnings], ""])
    lines.extend(["## Imported Comment Preview", "", "| Comment ID | Item | Type | Reviewer | Status | Comment | Recommendation | Flags |", "| --- | --- | --- | --- | --- | --- | --- | --- |"])
    if not result.comments:
        lines.append("|  | No valid comments. |  |  |  |  |  |  |")
    for comment in result.comments:
        lines.append(_comment_table_row(comment))
    return "\n".join(lines).rstrip() + "\n"


def review_packet_overview(packet: ReviewPacket) -> str:
    lines = [
        f"# Review Packet: {packet.packet_id}",
        "",
        "This packet is a local manual-review export. It does not include PDFs by default, does not contact cloud services, and does not change project evidence.",
        "",
        f"Project: {packet.project}",
        f"Theme: {packet.theme or '[not theme-specific]'}",
        f"Draft: {packet.draft_path or '[none]'}",
        f"Created: {packet.created_at}",
        f"Review items: {len(packet.items)}",
        "",
        "## Included Files",
        "",
    ]
    lines.extend(f"- `{filename}`" for filename in packet.files or ["manifest.json"])
    if packet.warnings:
        lines.extend(["", "## Warnings", "", *[f"- {_escape(warning)}" for warning in packet.warnings]])
    lines.extend(
        [
            "",
            "## Review Items",
            "",
            "| Item ID | Type | Label | Evidence status | Review prompt |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    if not packet.items:
        lines.append("|  | No review items were generated. |  |  |  |")
    for item in packet.items:
        lines.append(
            f"| `{_escape(item.item_id)}` | {_escape(item.item_type)} | {_escape(item.label)} | {_escape(item.evidence_status)} | {_escape(item.review_prompt)} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def review_instructions_markdown(packet: ReviewPacket) -> str:
    return "\n".join(
        [
            f"# Review Instructions: {packet.packet_id}",
            "",
            "Please add comments in `comments.csv` only.",
            "",
            "Do not edit the evidence reports in this packet as if they were source data.",
            "Use `item_id` values exactly as provided so comments can be imported safely.",
            "Suggested statuses: `open`, `resolved`, `needs_reread`, `needs_citation_check`, `weak_evidence`, `accepted`, `rejected`.",
            "",
            "Reviewer comments are advice for the project owner. They are not automatically treated as scientific truth.",
        ]
    ).rstrip() + "\n"


def review_packet_to_dict(packet: ReviewPacket) -> dict[str, object]:
    data = dataclass_to_plain(packet)
    data["schema"] = "paperwb-review-packet-v1"
    data["tool_version"] = __version__
    data["includes_pdfs"] = False
    data["boundary"] = "local manual review export; comments do not mutate evidence"
    return data


def reviewer_comment_to_dict(comment: ReviewerComment) -> dict[str, object]:
    return dataclass_to_plain(comment)


def load_review_packet_manifest(path: str | Path) -> ReviewPacket:
    data = load_json(path)
    items = [ReviewItem(**item) for item in data.get("items", []) if isinstance(item, dict)]
    return ReviewPacket(
        packet_id=str(data.get("packet_id", "")),
        project=str(data.get("project", "")),
        created_at=str(data.get("created_at", "")),
        output_dir=str(data.get("output_dir", "")),
        theme=str(data.get("theme", "")),
        draft_path=str(data.get("draft_path", "")),
        items=items,
        files=[str(item) for item in data.get("files", [])],
        warnings=[str(item) for item in data.get("warnings", [])],
    )


def review_followup_actions(response: ReviewResponse) -> list[str]:
    actions: list[str] = []
    for comment in sorted(response.unresolved, key=lambda item: item.comment_id):
        actions.append(_action_for_comment(comment))
    if response.unknown_item_comments:
        actions.append("Review comments linked to unknown item IDs; the packet may be stale or from another project.")
    return _dedupe_text(actions)


def _comment_from_row(row: dict[str, str], *, source_path: str, row_number: int) -> ReviewerComment:
    item_id = str(row.get("item_id", "") or "").strip()
    item_type = str(row.get("item_type", "") or "").strip()
    if not item_id:
        raise ValueError(f"Row {row_number}: item_id is required.")
    if item_type not in REVIEW_ITEM_TYPES:
        raise ValueError(f"Row {row_number}: unsupported item_type {item_type!r}.")
    status = str(row.get("status", "") or "open").strip() or "open"
    if status not in REVIEW_STATUSES:
        raise ValueError(f"Row {row_number}: unsupported status {status!r}.")
    comment_text = str(row.get("comment", "") or "").strip()
    recommendation = str(row.get("recommendation", "") or "").strip()
    if not comment_text and not recommendation:
        raise ValueError(f"Row {row_number}: comment or recommendation is required.")
    comment_id = str(row.get("comment_id", "") or "").strip() or _comment_id(item_id, row_number)
    return ReviewerComment(
        comment_id=comment_id,
        item_id=item_id,
        item_type=item_type,
        reviewer=str(row.get("reviewer", "") or "").strip(),
        status=status,
        comment=comment_text,
        recommendation=recommendation,
        requires_reread=_parse_bool(row.get("requires_reread", "")),
        requires_citation_check=_parse_bool(row.get("requires_citation_check", "")),
        weak_evidence=_parse_bool(row.get("weak_evidence", "")),
        created_at=str(row.get("created_at", "") or "").strip() or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        source_path=source_path,
    )


def _comment_from_mapping(raw: dict[str, object]) -> ReviewerComment:
    return ReviewerComment(
        comment_id=str(raw.get("comment_id", "")),
        item_id=str(raw.get("item_id", "")),
        item_type=str(raw.get("item_type", "")),
        reviewer=str(raw.get("reviewer", "")),
        status=str(raw.get("status", "open") or "open"),
        comment=str(raw.get("comment", "")),
        recommendation=str(raw.get("recommendation", "")),
        requires_reread=bool(raw.get("requires_reread", False)),
        requires_citation_check=bool(raw.get("requires_citation_check", False)),
        weak_evidence=bool(raw.get("weak_evidence", False)),
        created_at=str(raw.get("created_at", "")),
        source_path=str(raw.get("source_path", "")),
    )


def _known_item_ids(items: Iterable[ReviewItem], *, manifest_path: str | Path | None = None) -> set[str]:
    known = {item.item_id for item in items}
    if manifest_path and Path(manifest_path).exists():
        known.update(item.item_id for item in load_review_packet_manifest(manifest_path).items)
    return known


def _packet_id(project: str, *, theme: str = "", draft_path: str = "", created_at: str) -> str:
    label = theme or Path(draft_path).stem or "review"
    stamp = re.sub(r"[^0-9A-Za-z]+", "", created_at)[:15]
    return f"review_{_safe_slug(project)}_{_safe_slug(label)}_{stamp}"


def _comment_id(item_id: str, row_number: int) -> str:
    return f"comment_{_safe_slug(item_id)}_{row_number}"


def _safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("_") or "item"


def _find_theme(theme_query: str, themes: list[ProjectTheme]) -> ProjectTheme | None:
    wanted = normalize_tag(theme_query)
    for theme in themes:
        if theme.theme_id == wanted or normalize_tag(theme.name) == wanted:
            return theme
    return None


def _claims_for_theme(claims: list[Claim], theme_id: str, themes: list[ProjectTheme]) -> list[Claim]:
    if not theme_id:
        return list(claims)
    mapping = theme_by_tag(themes)
    selected: list[Claim] = []
    for claim in claims:
        claim_themes = {normalize_tag(claim.supports_theme)} if claim.supports_theme else set()
        for tag in parse_tags(claim.tags):
            if tag in mapping:
                claim_themes.add(mapping[tag].theme_id)
            claim_themes.add(normalize_tag(tag))
        if theme_id in claim_themes:
            selected.append(claim)
    return selected


def _paper_ids_for_theme(papers: list[Paper], theme: ProjectTheme, themes: list[ProjectTheme]) -> set[str]:
    ids: set[str] = set()
    for paper in papers:
        if any(item.theme_id == theme.theme_id for item in themes_for_tags(paper.tags, themes)):
            ids.add(paper.paper_id)
    return ids


def _dedupe_items(items: list[ReviewItem]) -> list[ReviewItem]:
    deduped: dict[str, ReviewItem] = {}
    for item in items:
        deduped.setdefault(item.item_id, item)
    return list(deduped.values())


def _dedupe_text(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _parse_bool(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "done", "x"}


def _escape(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def _comment_table_row(comment: ReviewerComment) -> str:
    flags = []
    if comment.requires_reread:
        flags.append("reread")
    if comment.requires_citation_check:
        flags.append("citation check")
    if comment.weak_evidence:
        flags.append("weak evidence")
    return (
        f"| `{_escape(comment.comment_id)}` | `{_escape(comment.item_id)}` | {_escape(comment.item_type)} | "
        f"{_escape(comment.reviewer)} | {_escape(comment.status)} | {_escape(comment.comment)} | {_escape(comment.recommendation)} | {_escape('; '.join(flags) or 'none')} |"
    )


def _action_for_comment(comment: ReviewerComment) -> str:
    if comment.requires_reread or comment.status == "needs_reread":
        return f"Reread local evidence for `{comment.item_id}` before changing any claim."
    if comment.requires_citation_check or comment.status == "needs_citation_check":
        return f"Check citation support for `{comment.item_id}` against local notes and BibTeX."
    if comment.weak_evidence or comment.status == "weak_evidence":
        return f"Review whether `{comment.item_id}` needs stronger evidence or softer draft use."
    return f"Review comment `{comment.comment_id}` on `{comment.item_id}` and decide a manual response."


def _draft_parse_summary(sections, paragraphs) -> str:
    lines = [
        f"# Draft Parse Summary v{__version__}",
        "",
        "This summary lists draft structure for manual review. It does not rewrite prose.",
        "",
        f"Sections: {len(sections)}",
        f"Paragraphs: {len(paragraphs)}",
        "",
        "| Paragraph ID | Section | Citations | Preview |",
        "| --- | --- | --- | --- |",
    ]
    if not paragraphs:
        lines.append("|  | No paragraphs found. |  |  |")
    for paragraph in paragraphs:
        lines.append(
            f"| `{_escape(paragraph.paragraph_id)}` | {_escape(paragraph.section_title)} | {_escape('; '.join(paragraph.citation_keys))} | {_escape(paragraph.text[:160])} |"
        )
    return "\n".join(lines).rstrip() + "\n"
