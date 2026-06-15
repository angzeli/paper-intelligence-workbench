"""Claim lifecycle and contradiction review utilities.

The lifecycle layer is a sidecar over user-entered notes and extracted claims.
It never auto-verifies claims or decides scientific truth; it only records
explicit local review state and produces conservative review queues.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from . import __version__
from .schema import Claim, Paper, ProjectTheme
from .tags import normalize_tag, theme_by_tag


CLAIM_STATUSES = {
    "newly_extracted",
    "needs_evidence_location",
    "needs_rereading",
    "verified",
    "ready_for_draft_use",
    "used_in_draft",
    "deprecated",
    "contradicted",
    "too_weak_to_use",
}
REVIEW_STATUSES = {"unreviewed", "needs_review", "reviewed", "blocked"}
READY_STATUSES = {"verified", "ready_for_draft_use"}
NOT_READY_STATUSES = {
    "newly_extracted",
    "needs_evidence_location",
    "needs_rereading",
    "deprecated",
    "contradicted",
    "too_weak_to_use",
}
LOW_READING_STATUS = {"unread", "skimmed"}
LOW_CONFIDENCE = {"low", "weak", "uncertain", "speculative", "needs-check", "needs_check"}
WEAK_STRENGTH = {"weak", "speculative"}


@dataclass(slots=True)
class ClaimLifecycleRecord:
    claim_id: str
    claim_status: str = "newly_extracted"
    review_status: str = "unreviewed"
    verification_date: str = ""
    deprecated_reason: str = ""
    contradiction_group: str = ""
    needs_reread: bool = False
    used_in_draft: bool = False
    reviewed_by: str = ""
    review_comment: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class ClaimReviewItem:
    claim_id: str
    paper_id: str
    claim_text: str
    theme: str = ""
    status: str = "newly_extracted"
    priority: str = "medium"
    score: int = 0
    reasons: list[str] = field(default_factory=list)
    suggested_action: str = ""


@dataclass(slots=True)
class ContradictionGroup:
    group_id: str
    theme: str = ""
    description: str = ""
    claim_ids: list[str] = field(default_factory=list)
    status: str = "open"
    user_comment: str = ""
    resolution_notes: str = ""
    created_at: str = ""
    updated_at: str = ""


def default_claim_lifecycle_path(root: str | Path = ".") -> Path:
    return Path(root) / "claim_lifecycle.json"


def default_contradictions_path(root: str | Path = ".") -> Path:
    return Path(root) / "contradictions.json"


def load_claim_lifecycle(path: str | Path) -> dict[str, ClaimLifecycleRecord]:
    target = Path(path)
    if not target.exists():
        return {}
    data = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"claim lifecycle file must be a JSON object: {target}")
    raw_records = data.get("claims", data)
    if not isinstance(raw_records, dict):
        raise ValueError(f"claim lifecycle file field 'claims' must be an object: {target}")
    records: dict[str, ClaimLifecycleRecord] = {}
    for claim_id, raw in raw_records.items():
        if not isinstance(raw, dict):
            continue
        records[str(claim_id)] = _record_from_dict(str(claim_id), raw)
    return records


def save_claim_lifecycle(path: str | Path, records: Mapping[str, ClaimLifecycleRecord]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "2.2",
        "updated_at": _now_iso(),
        "claims": {claim_id: asdict(record) for claim_id, record in sorted(records.items())},
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def load_contradiction_groups(path: str | Path) -> dict[str, ContradictionGroup]:
    target = Path(path)
    if not target.exists():
        return {}
    data = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"contradictions file must be a JSON object: {target}")
    raw_groups = data.get("groups", data)
    if not isinstance(raw_groups, dict):
        raise ValueError(f"contradictions file field 'groups' must be an object: {target}")
    groups: dict[str, ContradictionGroup] = {}
    for group_id, raw in raw_groups.items():
        if not isinstance(raw, dict):
            continue
        groups[str(group_id)] = _group_from_dict(str(group_id), raw)
    return groups


def save_contradiction_groups(path: str | Path, groups: Mapping[str, ContradictionGroup]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "2.2",
        "updated_at": _now_iso(),
        "groups": {group_id: asdict(group) for group_id, group in sorted(groups.items())},
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def lifecycle_status_for_claim(claim: Claim, records: Mapping[str, ClaimLifecycleRecord] | None = None) -> str:
    record = (records or {}).get(claim.claim_id)
    if record and record.claim_status:
        return record.claim_status
    if not (claim.section or claim.page):
        return "needs_evidence_location"
    if claim.strength in WEAK_STRENGTH or claim.confidence.strip().lower() in LOW_CONFIDENCE:
        return "too_weak_to_use"
    return "newly_extracted"


def build_claim_review_queue(
    claims: list[Claim],
    papers: list[Paper],
    themes: list[ProjectTheme],
    records: Mapping[str, ClaimLifecycleRecord] | None = None,
    *,
    theme: str = "",
    limit: int = 50,
    include_ready: bool = False,
) -> list[ClaimReviewItem]:
    papers_by_id = {paper.paper_id: paper for paper in papers}
    theme_lookup = theme_by_tag(themes)
    wanted = normalize_tag(theme) if theme else ""
    items: list[ClaimReviewItem] = []
    for claim in claims:
        claim_theme = _claim_theme(claim, theme_lookup)
        if wanted and wanted not in {normalize_tag(claim_theme), normalize_tag(claim.supports_theme), *{normalize_tag(tag) for tag in claim.tags}}:
            continue
        status = lifecycle_status_for_claim(claim, records)
        if not include_ready and status in READY_STATUSES:
            continue
        paper = papers_by_id.get(claim.paper_id)
        reasons: list[str] = []
        score = 0
        if claim.strength in {"strong", "moderate"} and not (claim.section or claim.page):
            score += 40
            reasons.append("strong/moderate claim has no section or page evidence location")
        elif not (claim.section or claim.page):
            score += 25
            reasons.append("claim has no section or page evidence location")
        record = (records or {}).get(claim.claim_id)
        if record and record.used_in_draft and status not in READY_STATUSES:
            score += 35
            reasons.append("claim is marked used in a draft but is not verified")
        if claim.confidence.strip().lower() in LOW_CONFIDENCE:
            score += 20
            reasons.append(f"claim confidence is {claim.confidence or 'low/unclear'}")
        if claim.strength in WEAK_STRENGTH:
            score += 18
            reasons.append(f"claim strength is {claim.strength}")
        if claim.evidence_type == "review_statement":
            score += 18
            reasons.append("claim is supported only as a review statement")
        if paper and paper.reading_status in LOW_READING_STATUS:
            score += 15
            reasons.append(f"paper reading status is {paper.reading_status}")
        if status in {"deprecated", "contradicted", "too_weak_to_use"}:
            score += 30
            reasons.append(f"claim lifecycle status is {status}")
        if status == "needs_rereading" or (record and record.needs_reread):
            score += 25
            reasons.append("claim is marked for rereading")
        if not reasons:
            score += 5
            reasons.append("claim has not been explicitly verified for draft use")
        items.append(
            ClaimReviewItem(
                claim_id=claim.claim_id,
                paper_id=claim.paper_id,
                claim_text=claim.claim_text,
                theme=claim_theme,
                status=status,
                priority=_priority_for_score(score),
                score=score,
                reasons=reasons,
                suggested_action=_suggested_action(status, reasons),
            )
        )
    items.sort(key=lambda item: (-item.score, item.claim_id))
    return items[:limit]


def mark_claim_status(
    records: dict[str, ClaimLifecycleRecord],
    claims: list[Claim],
    claim_id: str,
    *,
    status: str,
    reason: str = "",
    reviewed_by: str = "",
    comment: str = "",
    verification_date: str = "",
    needs_reread: bool | None = None,
    used_in_draft: bool | None = None,
    review_status: str = "",
) -> ClaimLifecycleRecord:
    if status not in CLAIM_STATUSES:
        raise ValueError(f"unsupported claim status {status!r}; use one of: {', '.join(sorted(CLAIM_STATUSES))}")
    if status == "deprecated" and not reason:
        raise ValueError("marking a claim deprecated requires --reason")
    known_claims = {claim.claim_id for claim in claims}
    if claim_id not in known_claims:
        raise ValueError(f"claim ID not found in parsed notes: {claim_id}")
    record = records.get(claim_id) or ClaimLifecycleRecord(claim_id=claim_id)
    record.claim_status = status
    if review_status:
        if review_status not in REVIEW_STATUSES:
            raise ValueError(f"unsupported review status {review_status!r}; use one of: {', '.join(sorted(REVIEW_STATUSES))}")
        record.review_status = review_status
    elif status in READY_STATUSES:
        record.review_status = "reviewed"
    elif status in {"deprecated", "contradicted", "too_weak_to_use", "needs_evidence_location", "needs_rereading"}:
        record.review_status = "needs_review"
    if status in READY_STATUSES:
        record.verification_date = verification_date or record.verification_date or _today()
    if reason:
        record.deprecated_reason = reason
    if reviewed_by:
        record.reviewed_by = reviewed_by
    if comment:
        record.review_comment = comment
    if needs_reread is not None:
        record.needs_reread = needs_reread
    if used_in_draft is not None:
        record.used_in_draft = used_in_draft
    if status == "needs_rereading":
        record.needs_reread = True
    if status == "used_in_draft":
        record.used_in_draft = True
    record.updated_at = _now_iso()
    records[claim_id] = record
    return record


def create_contradiction_group(
    groups: dict[str, ContradictionGroup],
    *,
    theme: str = "",
    description: str = "",
    status: str = "open",
    user_comment: str = "",
    group_id: str = "",
) -> ContradictionGroup:
    group_key = group_id or _next_group_id(groups, theme)
    if group_key in groups:
        raise ValueError(f"contradiction group already exists: {group_key}")
    now = _now_iso()
    group = ContradictionGroup(
        group_id=group_key,
        theme=theme,
        description=description,
        status=status,
        user_comment=user_comment,
        created_at=now,
        updated_at=now,
    )
    groups[group_key] = group
    return group


def add_claim_to_contradiction_group(
    groups: dict[str, ContradictionGroup],
    claims: list[Claim],
    group_id: str,
    claim_id: str,
) -> ContradictionGroup:
    if group_id not in groups:
        raise ValueError(f"contradiction group not found: {group_id}")
    if claim_id not in {claim.claim_id for claim in claims}:
        raise ValueError(f"claim ID not found in parsed notes: {claim_id}")
    group = groups[group_id]
    if claim_id not in group.claim_ids:
        group.claim_ids.append(claim_id)
        group.claim_ids.sort()
    group.updated_at = _now_iso()
    return group


def suggest_tension_candidates(claims: list[Claim], themes: list[ProjectTheme]) -> list[tuple[str, str, str]]:
    theme_lookup = theme_by_tag(themes)
    by_theme: dict[str, list[Claim]] = {}
    for claim in claims:
        theme = _claim_theme(claim, theme_lookup)
        if theme:
            by_theme.setdefault(theme, []).append(claim)
    suggestions: list[tuple[str, str, str]] = []
    opposing_tags = [
        ({"limitation", "photocorrosion", "unstable", "degradation"}, {"improvement", "stability", "stable"}),
        ({"increase", "enhanced", "improves"}, {"decrease", "suppressed", "reduces"}),
    ]
    for theme, theme_claims in by_theme.items():
        for index, left in enumerate(theme_claims):
            left_tags = {normalize_tag(tag) for tag in left.tags}
            for right in theme_claims[index + 1 :]:
                right_tags = {normalize_tag(tag) for tag in right.tags}
                if any((left_tags & a and right_tags & b) or (left_tags & b and right_tags & a) for a, b in opposing_tags):
                    suggestions.append((theme, left.claim_id, right.claim_id))
    return suggestions


def claim_review_queue_report(items: list[ClaimReviewItem], *, project: str = "default", title: str = f"Claim Review Queue v{__version__}") -> str:
    lines = [
        f"# {title}",
        "",
        "Boundary: this report prioritizes local claim review work. It does not verify claims, decide scientific truth, or infer contradictions semantically.",
        "",
        f"Project: {project}",
        f"Queued claims: {len(items)}",
        "",
        "| Priority | Score | Claim ID | Paper | Status | Theme | Reasons | Suggested action |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    if items:
        for item in items:
            lines.append(
                f"| {item.priority} | {item.score} | `{_escape(item.claim_id)}` | `{_escape(item.paper_id)}` | {_escape(item.status)} | {_escape(item.theme or 'unmapped')} | {_escape('; '.join(item.reasons))} | {_escape(item.suggested_action)} |"
            )
    else:
        lines.append("| none | 0 |  |  |  |  | No claims need review under the current filters. |  |")
    return "\n".join(lines).rstrip() + "\n"


def lifecycle_claims_report(
    claims: list[Claim],
    records: Mapping[str, ClaimLifecycleRecord],
    *,
    project: str = "default",
    status_filter: set[str],
    title: str,
) -> str:
    rows = [(claim, records.get(claim.claim_id)) for claim in claims if lifecycle_status_for_claim(claim, records) in status_filter]
    lines = [
        f"# {title}",
        "",
        "Boundary: lifecycle state is explicit local review metadata. It is not a scientific truth assessment.",
        "",
        f"Project: {project}",
        f"Matching claims: {len(rows)}",
        "",
        "| Claim ID | Paper | Status | Review status | Verification date | Reason/comment | Claim |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    if rows:
        for claim, record in rows:
            status = lifecycle_status_for_claim(claim, records)
            reason = ""
            if record:
                reason = record.deprecated_reason or record.review_comment
            lines.append(
                f"| `{_escape(claim.claim_id)}` | `{_escape(claim.paper_id)}` | {_escape(status)} | {_escape(record.review_status if record else '')} | {_escape(record.verification_date if record else '')} | {_escape(reason)} | {_escape(claim.claim_text)} |"
            )
    else:
        lines.append("| none |  |  |  |  |  | No matching claims. |")
    return "\n".join(lines).rstrip() + "\n"


def claims_used_in_drafts_report(
    claims: list[Claim],
    records: Mapping[str, ClaimLifecycleRecord],
    *,
    project: str = "default",
    title: str = f"Claims Used in Drafts v{__version__}",
) -> str:
    rows = [(claim, records.get(claim.claim_id)) for claim in claims if (records.get(claim.claim_id) and records[claim.claim_id].used_in_draft) or lifecycle_status_for_claim(claim, records) == "used_in_draft"]
    lines = [
        f"# {title}",
        "",
        "Boundary: draft-use state is explicit local review metadata. This report does not infer whether the draft usage is correct.",
        "",
        f"Project: {project}",
        f"Draft-used claims: {len(rows)}",
        "",
        "| Claim ID | Paper | Status | Verified? | Comment | Claim |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    if rows:
        for claim, record in rows:
            status = lifecycle_status_for_claim(claim, records)
            verified = "yes" if status in READY_STATUSES else "no"
            lines.append(
                f"| `{_escape(claim.claim_id)}` | `{_escape(claim.paper_id)}` | {_escape(status)} | {verified} | {_escape(record.review_comment if record else '')} | {_escape(claim.claim_text)} |"
            )
    else:
        lines.append("| none |  |  |  |  | No claims are marked as used in drafts. |")
    return "\n".join(lines).rstrip() + "\n"


def contradictions_report(
    groups: Mapping[str, ContradictionGroup],
    claims: list[Claim],
    themes: list[ProjectTheme],
    *,
    project: str = "default",
    title: str = f"Contradictions and Tensions v{__version__}",
) -> str:
    claim_by_id = {claim.claim_id: claim for claim in claims}
    suggestions = suggest_tension_candidates(claims, themes)
    lines = [
        f"# {title}",
        "",
        "Boundary: contradiction groups are user-managed review aids. Heuristic suggestions are possible tensions only, not scientific conclusions.",
        "",
        f"Project: {project}",
        f"Manual groups: {len(groups)}",
        "",
        "## Manual Groups",
        "",
    ]
    if groups:
        for group in sorted(groups.values(), key=lambda item: item.group_id):
            lines.extend(
                [
                    f"### {group.group_id}",
                    "",
                    f"- Theme: {group.theme or 'unmapped'}",
                    f"- Status: {group.status}",
                    f"- Description: {group.description or '[none]'}",
                    f"- User comment: {group.user_comment or '[none]'}",
                    "",
                    "| Claim ID | Paper | Claim |",
                    "| --- | --- | --- |",
                ]
            )
            for claim_id in group.claim_ids:
                claim = claim_by_id.get(claim_id)
                if claim:
                    lines.append(f"| `{_escape(claim.claim_id)}` | `{_escape(claim.paper_id)}` | {_escape(claim.claim_text)} |")
                else:
                    lines.append(f"| `{_escape(claim_id)}` |  | Missing from parsed notes. |")
            lines.append("")
    else:
        lines.append("No manual contradiction groups have been created.")
        lines.append("")
    lines.extend(["## Heuristic Possible Tensions", ""])
    if suggestions:
        lines.extend(["| Theme | Claim A | Claim B |", "| --- | --- | --- |"])
        for theme, left, right in suggestions:
            lines.append(f"| {_escape(theme)} | `{_escape(left)}` | `{_escape(right)}` |")
    else:
        lines.append("No simple tag-based tension candidates were detected.")
    return "\n".join(lines).rstrip() + "\n"


def _record_from_dict(claim_id: str, raw: Mapping[str, Any]) -> ClaimLifecycleRecord:
    return ClaimLifecycleRecord(
        claim_id=str(raw.get("claim_id", claim_id) or claim_id),
        claim_status=str(raw.get("claim_status", "newly_extracted") or "newly_extracted"),
        review_status=str(raw.get("review_status", "unreviewed") or "unreviewed"),
        verification_date=str(raw.get("verification_date", "") or ""),
        deprecated_reason=str(raw.get("deprecated_reason", "") or ""),
        contradiction_group=str(raw.get("contradiction_group", "") or ""),
        needs_reread=bool(raw.get("needs_reread", False)),
        used_in_draft=bool(raw.get("used_in_draft", False)),
        reviewed_by=str(raw.get("reviewed_by", "") or ""),
        review_comment=str(raw.get("review_comment", "") or ""),
        updated_at=str(raw.get("updated_at", "") or ""),
    )


def _group_from_dict(group_id: str, raw: Mapping[str, Any]) -> ContradictionGroup:
    return ContradictionGroup(
        group_id=str(raw.get("group_id", group_id) or group_id),
        theme=str(raw.get("theme", "") or ""),
        description=str(raw.get("description", "") or ""),
        claim_ids=[str(item) for item in raw.get("claim_ids", []) if str(item)],
        status=str(raw.get("status", "open") or "open"),
        user_comment=str(raw.get("user_comment", "") or ""),
        resolution_notes=str(raw.get("resolution_notes", "") or ""),
        created_at=str(raw.get("created_at", "") or ""),
        updated_at=str(raw.get("updated_at", "") or ""),
    )


def _claim_theme(claim: Claim, theme_lookup: Mapping[str, ProjectTheme]) -> str:
    if claim.supports_theme:
        return claim.supports_theme
    for tag in claim.tags:
        theme = theme_lookup.get(normalize_tag(tag))
        if theme:
            return theme.theme_id
    return ""


def _priority_for_score(score: int) -> str:
    if score >= 55:
        return "high"
    if score >= 25:
        return "medium"
    return "low"


def _suggested_action(status: str, reasons: list[str]) -> str:
    if status == "deprecated":
        return "Avoid this claim in drafts unless manually reinstated."
    if status == "contradicted":
        return "Review the contradiction group before using this claim."
    if any("evidence location" in reason for reason in reasons):
        return "Add or verify a page/section evidence location in the note."
    if any("reread" in reason or "reading status" in reason for reason in reasons):
        return "Reread the paper and update the structured note."
    if any("review statement" in reason for reason in reasons):
        return "Check whether primary evidence is needed before draft use."
    return "Review the note and mark the claim verified only after checking it."


def _next_group_id(groups: Mapping[str, ContradictionGroup], theme: str) -> str:
    stem = normalize_tag(theme or "general") or "general"
    index = 1
    while f"contradiction_{stem}_{index}" in groups:
        index += 1
    return f"contradiction_{stem}_{index}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()
