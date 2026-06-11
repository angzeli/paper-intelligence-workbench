"""Reading-session and follow-up workflow helpers.

This module stores local reading workflow state in JSON/JSONL files. It does
not read papers, fabricate notes, or infer claims.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Iterable

from .notes import write_note_template
from .registry import normalize_title, save_registry, validate_reading_status, validate_registry
from .schema import Claim, Paper, PaperNote, ProjectTheme, ReadingStatus, dataclass_to_plain
from .tags import normalize_tag, theme_by_tag


SESSION_STATUS_ACTIVE = "active"
SESSION_STATUS_COMPLETED = "completed"
SESSION_STATUS_CANCELLED = "cancelled"
FOLLOWUP_STATUS_OPEN = "open"
FOLLOWUP_STATUS_DONE = "done"


@dataclass(slots=True)
class ReadingSession:
    session_id: str
    project: str
    paper_id: str
    started_at: str
    completed_at: str = ""
    duration_minutes: int = 0
    reading_goal: str = ""
    session_status: str = SESSION_STATUS_ACTIVE
    notes_created: bool = False
    claims_added: int = 0
    follow_up_actions: list[str] = field(default_factory=list)
    status_before: str = ""
    status_after: str = ""
    user_comment: str = ""
    note_path: str = ""


@dataclass(slots=True)
class ReadingQueueItem:
    paper_id: str
    title: str
    year: str = ""
    reading_status: str = ""
    priority: str = ""
    reading_priority: str = ""
    score: int = 0
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    bibtex_key: str = ""
    notes_path: str = ""


@dataclass(slots=True)
class FollowUpAction:
    action_id: str
    project: str
    paper_id: str
    text: str
    source: str
    status: str = FOLLOWUP_STATUS_OPEN
    theme: str = ""
    completed_at: str = ""


@dataclass(slots=True)
class WeeklyReadingReview:
    project: str
    period_days: int
    sessions: list[ReadingSession] = field(default_factory=list)
    queue: list[ReadingQueueItem] = field(default_factory=list)
    followups: list[FollowUpAction] = field(default_factory=list)
    theme_claim_counts: dict[str, int] = field(default_factory=dict)
    weak_theme_ids: list[str] = field(default_factory=list)


def default_reading_sessions_path(root: str | Path = ".") -> Path:
    return Path(root) / ".paperwb" / "reading_sessions.jsonl"


def default_followups_state_path(root: str | Path = ".") -> Path:
    return Path(root) / ".paperwb" / "followups_state.json"


def make_session_id(paper_id: str, now: datetime | None = None) -> str:
    current = now or datetime.now(timezone.utc)
    stamp = current.strftime("%Y%m%dT%H%M%SZ")
    safe_paper_id = normalize_title(paper_id).replace(" ", "_") or "paper"
    return f"read_{safe_paper_id}_{stamp}"


def make_unique_session_id(paper_id: str, existing_sessions: Iterable[ReadingSession], now: datetime | None = None) -> str:
    base = make_session_id(paper_id, now=now)
    existing_ids = {session.session_id for session in existing_sessions}
    if base not in existing_ids:
        return base
    counter = 2
    while f"{base}_{counter}" in existing_ids:
        counter += 1
    return f"{base}_{counter}"


def load_reading_sessions_with_warnings(path: str | Path) -> tuple[list[ReadingSession], list[str]]:
    target = Path(path)
    if not target.exists():
        return [], []
    sessions: list[ReadingSession] = []
    warnings: list[str] = []
    for line_number, line in enumerate(target.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            sessions.append(_session_from_dict(data))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            warnings.append(f"{target}: line {line_number} could not be parsed as a reading session; skipped. Detail: {exc}")
            continue
    return sessions, warnings


def load_reading_sessions(path: str | Path) -> list[ReadingSession]:
    sessions, _warnings = load_reading_sessions_with_warnings(path)
    return sessions


def save_reading_sessions(sessions: list[ReadingSession], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(dataclass_to_plain(session), ensure_ascii=False, sort_keys=True) for session in sessions]
    target.write_text("\n".join(lines).rstrip() + ("\n" if lines else ""), encoding="utf-8")
    return target


def append_reading_session(session: ReadingSession, path: str | Path) -> Path:
    sessions = load_reading_sessions(path)
    sessions.append(session)
    return save_reading_sessions(sessions, path)


def update_reading_session(session: ReadingSession, path: str | Path) -> Path:
    sessions = load_reading_sessions(path)
    updated = False
    for index, current in enumerate(sessions):
        if current.session_id == session.session_id:
            sessions[index] = session
            updated = True
            break
    if not updated:
        sessions.append(session)
    return save_reading_sessions(sessions, path)


def find_reading_session(session_id: str, path: str | Path) -> ReadingSession:
    for session in load_reading_sessions(path):
        if session.session_id == session_id:
            return session
    raise FileNotFoundError(f"reading session not found: {session_id}")


def _session_from_dict(data: dict) -> ReadingSession:
    return ReadingSession(
        session_id=str(data.get("session_id", "")),
        project=str(data.get("project", "")),
        paper_id=str(data.get("paper_id", "")),
        started_at=str(data.get("started_at", "")),
        completed_at=str(data.get("completed_at", "")),
        duration_minutes=int(data.get("duration_minutes") or 0),
        reading_goal=str(data.get("reading_goal", "")),
        session_status=str(data.get("session_status", SESSION_STATUS_ACTIVE)),
        notes_created=bool(data.get("notes_created", False)),
        claims_added=int(data.get("claims_added") or 0),
        follow_up_actions=[str(item) for item in data.get("follow_up_actions", [])],
        status_before=str(data.get("status_before", "")),
        status_after=str(data.get("status_after", "")),
        user_comment=str(data.get("user_comment", "")),
        note_path=str(data.get("note_path", "")),
    )


def _paper_by_id(papers: list[Paper]) -> dict[str, Paper]:
    return {paper.paper_id: paper for paper in papers}


def _notes_by_paper(notes: list[PaperNote]) -> dict[str, PaperNote]:
    return {note.paper_id: note for note in notes if note.paper_id}


def _claims_by_paper(claims: list[Claim]) -> dict[str, list[Claim]]:
    grouped: dict[str, list[Claim]] = defaultdict(list)
    for claim in claims:
        grouped[claim.paper_id].append(claim)
    return dict(grouped)


def _paper_matches_theme(paper: Paper, theme: ProjectTheme, claims: list[Claim]) -> bool:
    paper_tags = {normalize_tag(tag) for tag in paper.tags}
    theme_tags = {normalize_tag(tag) for tag in theme.tags}
    if normalize_tag(theme.theme_id) in paper_tags or theme_tags.intersection(paper_tags):
        return True
    for claim in claims:
        if claim.paper_id != paper.paper_id:
            continue
        if normalize_tag(claim.supports_theme) == normalize_tag(theme.theme_id):
            return True
        if theme_tags.intersection({normalize_tag(tag) for tag in claim.tags}):
            return True
    return False


def _theme_for_query(theme_query: str, themes: list[ProjectTheme]) -> ProjectTheme | None:
    wanted = normalize_tag(theme_query)
    for theme in themes:
        if normalize_tag(theme.theme_id) == wanted or normalize_tag(theme.name) == wanted:
            return theme
    return None


def weak_theme_ids(claims: list[Claim], themes: list[ProjectTheme]) -> set[str]:
    weak: set[str] = set()
    for theme in themes:
        theme_claims = [
            claim
            for claim in claims
            if normalize_tag(claim.supports_theme) == normalize_tag(theme.theme_id)
            or normalize_tag(theme.theme_id) in {normalize_tag(tag) for tag in claim.tags}
            or {normalize_tag(tag) for tag in claim.tags}.intersection({normalize_tag(tag) for tag in theme.tags})
        ]
        paper_ids = {claim.paper_id for claim in theme_claims if claim.paper_id}
        strong_claims = [claim for claim in theme_claims if claim.strength in {"strong", "moderate"}]
        missing_locations = [claim for claim in theme_claims if not (claim.section or claim.page)]
        if len(theme_claims) < theme.min_claims or len(paper_ids) < theme.min_papers or not strong_claims or missing_locations:
            weak.add(theme.theme_id)
    return weak


def build_reading_queue(
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    themes: list[ProjectTheme],
    *,
    theme: str = "",
    priority: str = "",
    limit: int = 0,
) -> list[ReadingQueueItem]:
    note_map = _notes_by_paper(notes)
    claims_map = _claims_by_paper(claims)
    weak_themes = weak_theme_ids(claims, themes)
    tag_to_theme = theme_by_tag(themes)
    selected_theme = _theme_for_query(theme, themes) if theme else None
    normalized_priority = priority.strip().lower()
    items: list[ReadingQueueItem] = []
    for paper in papers:
        if normalized_priority and normalized_priority not in {paper.priority.lower(), paper.reading_priority.lower()}:
            continue
        if selected_theme and not _paper_matches_theme(paper, selected_theme, claims):
            continue
        score = 0
        reasons: list[str] = []
        warnings: list[str] = []
        priority_score = {"critical": 70, "high": 55, "medium": 25, "low": 10}
        if paper.reading_priority.lower() in priority_score:
            score += priority_score[paper.reading_priority.lower()]
            reasons.append(f"reading_priority={paper.reading_priority}")
        if paper.priority.lower() in priority_score:
            score += priority_score[paper.priority.lower()]
            reasons.append(f"priority={paper.priority}")
        if paper.included_in_lit_review.strip().lower() in {"true", "yes", "1", "included"} and paper.paper_id not in note_map:
            score += 35
            reasons.append("included in lit review but missing parsed note")
        if paper.reading_status == ReadingStatus.UNREAD.value:
            score += 25
            reasons.append("unread")
        elif paper.reading_status == ReadingStatus.SKIMMED.value:
            score += 18
            reasons.append("skimmed")
        elif paper.reading_status == ReadingStatus.PARTIALLY_READ.value:
            score += 12
            reasons.append("partially read")
        if paper.paper_id not in note_map:
            score += 20
            reasons.append("missing note")
        elif not claims_map.get(paper.paper_id):
            score += 12
            reasons.append("note has no extracted claims")
        if selected_theme:
            score += 20
            reasons.append(f"matches theme {selected_theme.name}")
        paper_theme_ids = {tag_to_theme[normalize_tag(tag)].theme_id for tag in paper.tags if normalize_tag(tag) in tag_to_theme}
        for theme_id in sorted(paper_theme_ids.intersection(weak_themes)):
            score += 10
            reasons.append(f"supports weak theme {theme_id}")
        if paper.added_date:
            score += 3
            reasons.append("has added_date")
        if not paper.bibtex_key:
            warnings.append("missing BibTeX key")
        if not paper.notes_path:
            warnings.append("missing notes_path")
        if not reasons:
            reasons.append("lower-priority review candidate")
        items.append(
            ReadingQueueItem(
                paper_id=paper.paper_id,
                title=paper.title,
                year=paper.year,
                reading_status=paper.reading_status,
                priority=paper.priority,
                reading_priority=paper.reading_priority,
                score=score,
                reasons=reasons,
                warnings=warnings,
                tags=list(paper.tags),
                bibtex_key=paper.bibtex_key,
                notes_path=paper.notes_path,
            )
        )
    items.sort(key=lambda item: (-item.score, item.reading_status, item.year, item.paper_id))
    return items[:limit] if limit and limit > 0 else items


def reading_queue_report(items: list[ReadingQueueItem], *, title: str = "Reading Queue") -> str:
    lines = [
        f"# {title}",
        "",
        "This queue is ranked with transparent local metadata rules. It does not read papers or infer quality.",
        "",
        f"Items: {len(items)}",
        "",
        "| Rank | Score | Paper ID | Status | Priority | Title | Reasons | Warnings |",
        "| ---: | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    if not items:
        lines.append("| 0 | 0 |  |  |  | No papers matched. |  |  |")
    for index, item in enumerate(items, start=1):
        priority = item.reading_priority or item.priority
        lines.append(
            f"| {index} | {item.score} | {_escape(item.paper_id)} | {_escape(item.reading_status)} | {_escape(priority)} | {_escape(item.title)} | {_escape('; '.join(item.reasons))} | {_escape('; '.join(item.warnings))} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def _relative_to_root(path: Path, root: str | Path) -> str:
    try:
        return path.resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _resolve_note_path(paper: Paper, root: str | Path, notes_dir: str | Path) -> Path:
    if paper.notes_path:
        target = Path(paper.notes_path)
        return target if target.is_absolute() else Path(root) / target
    return Path(notes_dir) / f"{paper.paper_id}.md"


def start_reading_session(
    *,
    paper_id: str,
    project: str,
    root: str | Path,
    papers: list[Paper],
    registry_path: str | Path,
    notes_dir: str | Path,
    sessions_path: str | Path,
    reading_goal: str = "",
    user_comment: str = "",
    force_note: bool = False,
    now: datetime | None = None,
) -> tuple[ReadingSession, Path, bool, list[str]]:
    paper = _paper_by_id(papers).get(paper_id)
    if paper is None:
        raise ValueError(f"unknown paper_id: {paper_id}")
    warnings: list[str] = []
    if not paper.bibtex_key:
        warnings.append("Paper has no BibTeX key.")
    for finding in validate_registry(papers):
        if finding.code in {"duplicate_doi", "duplicate_title"} and paper.paper_id in finding.message:
            warnings.append(f"{finding.code}: {finding.message}")
    note_path = _resolve_note_path(paper, root, notes_dir)
    note_exists = note_path.exists()
    if note_exists and not force_note:
        notes_created = False
    else:
        write_note_template(paper, output_path=note_path, force=force_note)
        notes_created = not note_exists
    changed_registry = False
    if not paper.notes_path:
        paper.notes_path = _relative_to_root(note_path, root)
        changed_registry = True
    if changed_registry:
        save_registry(papers, registry_path)
    existing_sessions = load_reading_sessions(sessions_path)
    session = ReadingSession(
        session_id=make_unique_session_id(paper_id, existing_sessions, now=now),
        project=project,
        paper_id=paper_id,
        started_at=(now or datetime.now(timezone.utc)).isoformat(),
        reading_goal=reading_goal,
        session_status=SESSION_STATUS_ACTIVE,
        notes_created=notes_created,
        status_before=paper.reading_status,
        user_comment=user_comment,
        note_path=_relative_to_root(note_path, root),
    )
    save_reading_sessions(existing_sessions + [session], sessions_path)
    return session, note_path, notes_created, warnings


def finish_reading_session(
    *,
    session_id: str,
    project: str,
    papers: list[Paper],
    registry_path: str | Path,
    sessions_path: str | Path,
    status: str,
    duration_minutes: int = 0,
    summary: str = "",
    follow_up_actions: Iterable[str] = (),
    claims_added: int = 0,
    now: datetime | None = None,
) -> ReadingSession:
    session = find_reading_session(session_id, sessions_path)
    target_status = validate_reading_status(status)
    paper = _paper_by_id(papers).get(session.paper_id)
    if paper is None:
        raise ValueError(f"session paper_id is not in registry: {session.paper_id}")
    current_time = now or datetime.now(timezone.utc)
    session.project = session.project or project
    session.completed_at = current_time.isoformat()
    session.session_status = SESSION_STATUS_COMPLETED
    session.status_after = target_status
    session.duration_minutes = duration_minutes or _duration_minutes(session.started_at, session.completed_at)
    session.user_comment = summary or session.user_comment
    session.claims_added = int(claims_added or 0)
    session.follow_up_actions.extend(str(action).strip() for action in follow_up_actions if str(action).strip())
    paper.reading_status = target_status
    paper.last_reviewed_date = current_time.date().isoformat()
    save_registry(papers, registry_path)
    update_reading_session(session, sessions_path)
    return session


def _duration_minutes(started_at: str, completed_at: str) -> int:
    try:
        start = datetime.fromisoformat(started_at)
        end = datetime.fromisoformat(completed_at)
    except ValueError:
        return 0
    return max(0, int((end - start).total_seconds() // 60))


def reading_session_report(session: ReadingSession, paper: Paper | None = None, warnings: list[str] | None = None) -> str:
    lines = [
        "# Reading Session",
        "",
        f"Session ID: {session.session_id}",
        f"Project: {session.project or 'default'}",
        f"Paper ID: {session.paper_id}",
    ]
    if paper:
        lines.append(f"Title: {paper.title}")
        lines.append(f"BibTeX key: {paper.bibtex_key or '[missing]'}")
    lines.extend(
        [
            f"Started at: {session.started_at}",
            f"Completed at: {session.completed_at or '[active]'}",
            f"Duration minutes: {session.duration_minutes}",
            f"Goal: {session.reading_goal or '[none]'}",
            f"Status: {session.session_status}",
            f"Status before: {session.status_before or '[unknown]'}",
            f"Status after: {session.status_after or '[pending]'}",
            f"Note path: {session.note_path or '[none]'}",
            f"Notes created: {str(session.notes_created).lower()}",
            f"Claims added: {session.claims_added}",
            "",
            "## Reading Checklist",
            "",
            "- [ ] Verify metadata and BibTeX key.",
            "- [ ] Record one-sentence summary in the structured note.",
            "- [ ] Record methods, key findings, limitations, and usefulness.",
            "- [ ] Add only claims directly supported by the paper.",
            "- [ ] Add section/page/figure/table locations for evidence.",
            "- [ ] Add follow-up actions for unresolved checks.",
            "",
            "## Follow-up Actions",
            "",
        ]
    )
    if session.follow_up_actions:
        lines.extend(f"- {action}" for action in session.follow_up_actions)
    else:
        lines.append("- None recorded in this session.")
    if session.user_comment:
        lines.extend(["", "## Session Comment", "", session.user_comment])
    if warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
    return "\n".join(lines).rstrip() + "\n"


def session_status_report(sessions: list[ReadingSession]) -> str:
    counts = Counter(session.session_status for session in sessions)
    lines = [
        "# Reading Session Status",
        "",
        f"Sessions: {len(sessions)}",
        "",
        "| Status | Count |",
        "| --- | ---: |",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"| {status} | {count} |")
    lines.extend(["", "## Sessions", "", "| Session ID | Project | Paper ID | Status | Started | Completed | After |", "| --- | --- | --- | --- | --- | --- | --- |"])
    for session in sessions:
        lines.append(
            f"| {_escape(session.session_id)} | {_escape(session.project)} | {_escape(session.paper_id)} | {_escape(session.session_status)} | {_escape(session.started_at)} | {_escape(session.completed_at)} | {_escape(session.status_after)} |"
        )
    if not sessions:
        lines.append("|  |  |  | none |  |  |  |")
    return "\n".join(lines).rstrip() + "\n"


def load_followup_state(path: str | Path) -> dict[str, dict[str, str]]:
    state, _warnings = load_followup_state_with_warnings(path)
    return state


def load_followup_state_with_warnings(path: str | Path) -> tuple[dict[str, dict[str, str]], list[str]]:
    target = Path(path)
    if not target.exists():
        return {}, []
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"{target}: follow-up completion state is not valid JSON; ignored. Detail: {exc}"]
    if not isinstance(data, dict):
        return {}, [f"{target}: follow-up completion state must be a JSON object; ignored."]
    state: dict[str, dict[str, str]] = {}
    warnings: list[str] = []
    for key, value in data.items():
        if not isinstance(value, dict):
            warnings.append(f"{target}: follow-up state for {key!r} is not an object; ignored.")
            continue
        state[str(key)] = {str(item_key): str(item_value) for item_key, item_value in value.items()}
    return state, warnings


def action_ids(actions: Iterable[FollowUpAction]) -> set[str]:
    return {action.action_id for action in actions}


def save_followup_state(state: dict[str, dict[str, str]], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def mark_followup_done(action_id: str, path: str | Path, *, now: datetime | None = None) -> dict[str, dict[str, str]]:
    state = load_followup_state(path)
    state[action_id] = {"status": FOLLOWUP_STATUS_DONE, "completed_at": (now or datetime.now(timezone.utc)).isoformat()}
    save_followup_state(state, path)
    return state


def collect_followups(
    *,
    project: str,
    papers: list[Paper],
    notes: list[PaperNote],
    sessions: list[ReadingSession],
    themes: list[ProjectTheme],
    state: dict[str, dict[str, str]] | None = None,
) -> list[FollowUpAction]:
    state = state or {}
    paper_map = _paper_by_id(papers)
    actions: list[FollowUpAction] = []
    for note in notes:
        theme_id = _theme_for_paper(paper_map.get(note.paper_id), themes)
        for index, text in enumerate(note.follow_up_actions, start=1):
            action_id = f"note:{note.paper_id}:{index}"
            entry = state.get(action_id, {})
            actions.append(
                FollowUpAction(
                    action_id=action_id,
                    project=project,
                    paper_id=note.paper_id,
                    text=text,
                    source=note.source_path,
                    status=entry.get("status", FOLLOWUP_STATUS_OPEN),
                    theme=theme_id,
                    completed_at=entry.get("completed_at", ""),
                )
            )
    for session in sessions:
        theme_id = _theme_for_paper(paper_map.get(session.paper_id), themes)
        for index, text in enumerate(session.follow_up_actions, start=1):
            action_id = f"session:{session.session_id}:{index}"
            entry = state.get(action_id, {})
            actions.append(
                FollowUpAction(
                    action_id=action_id,
                    project=session.project or project,
                    paper_id=session.paper_id,
                    text=text,
                    source=session.session_id,
                    status=entry.get("status", FOLLOWUP_STATUS_OPEN),
                    theme=theme_id,
                    completed_at=entry.get("completed_at", ""),
                )
            )
    return actions


def _theme_for_paper(paper: Paper | None, themes: list[ProjectTheme]) -> str:
    if paper is None:
        return ""
    tag_map = theme_by_tag(themes)
    for tag in paper.tags:
        mapped = tag_map.get(normalize_tag(tag))
        if mapped:
            return mapped.theme_id
    return ""


def filter_followups(actions: list[FollowUpAction], *, theme: str = "", include_done: bool = False) -> list[FollowUpAction]:
    result = actions
    if theme:
        wanted = normalize_tag(theme)
        result = [action for action in result if normalize_tag(action.theme) == wanted]
    if not include_done:
        result = [action for action in result if action.status != FOLLOWUP_STATUS_DONE]
    return result


def followups_report(actions: list[FollowUpAction], *, title: str = "Follow-up Actions", base_path: str | Path | None = None) -> str:
    lines = [
        f"# {title}",
        "",
        f"Actions: {len(actions)}",
        "",
        "| Status | Action ID | Paper ID | Theme | Source | Action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    if not actions:
        lines.append("|  |  |  |  |  | No follow-up actions matched. |")
    for action in actions:
        source = _display_source(action.source, base_path)
        lines.append(
            f"| {_escape(action.status)} | {_escape(action.action_id)} | {_escape(action.paper_id)} | {_escape(action.theme)} | {_escape(source)} | {_escape(action.text)} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def build_weekly_review(
    *,
    project: str,
    papers: list[Paper],
    notes: list[PaperNote],
    claims: list[Claim],
    themes: list[ProjectTheme],
    sessions: list[ReadingSession],
    followups: list[FollowUpAction],
    period_days: int = 7,
    as_of: datetime | None = None,
) -> WeeklyReadingReview:
    current_time = as_of or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)
    cutoff = current_time.timestamp() - max(period_days, 0) * 24 * 60 * 60
    recent_sessions = [session for session in sessions if _session_timestamp(session) >= cutoff]
    theme_counts: dict[str, int] = {}
    for theme in themes:
        theme_counts[theme.theme_id] = len(
            [
                claim
                for claim in claims
                if normalize_tag(claim.supports_theme) == normalize_tag(theme.theme_id)
                or {normalize_tag(tag) for tag in claim.tags}.intersection({normalize_tag(tag) for tag in theme.tags})
            ]
        )
    queue = build_reading_queue(papers, notes, claims, themes, limit=5)
    return WeeklyReadingReview(
        project=project,
        period_days=period_days,
        sessions=recent_sessions,
        queue=queue,
        followups=[action for action in followups if action.status != FOLLOWUP_STATUS_DONE],
        theme_claim_counts=theme_counts,
        weak_theme_ids=sorted(weak_theme_ids(claims, themes)),
    )


def _session_timestamp(session: ReadingSession) -> float:
    value = session.completed_at or session.started_at
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return 0.0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def weekly_reading_review_report(review: WeeklyReadingReview) -> str:
    status_after = Counter(session.status_after for session in review.sessions if session.status_after)
    lines = [
        "# Weekly Reading Review",
        "",
        f"Project: {review.project}",
        f"Period days: {review.period_days}",
        f"Sessions completed or active in period: {len(review.sessions)}",
        f"Papers marked read/deeply read: {status_after.get('read', 0) + status_after.get('deeply_read', 0)}",
        f"Papers skimmed: {status_after.get('skimmed', 0)}",
        f"Notes created: {sum(1 for session in review.sessions if session.notes_created)}",
        f"Claims added: {sum(session.claims_added for session in review.sessions)}",
        "",
        "## Sessions",
        "",
        "| Session ID | Paper ID | Status after | Duration | Follow-ups |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    if not review.sessions:
        lines.append("|  |  | none | 0 | 0 |")
    for session in review.sessions:
        lines.append(f"| {_escape(session.session_id)} | {_escape(session.paper_id)} | {_escape(session.status_after)} | {session.duration_minutes} | {len(session.follow_up_actions)} |")
    lines.extend(["", "## Themes", "", "| Theme | Claims | Weak or incomplete |", "| --- | ---: | --- |"])
    if not review.theme_claim_counts:
        lines.append("|  | 0 | no themes loaded |")
    for theme_id, count in sorted(review.theme_claim_counts.items()):
        lines.append(f"| {_escape(theme_id)} | {count} | {str(theme_id in review.weak_theme_ids).lower()} |")
    lines.extend(["", "## Open Follow-up Actions", ""])
    if review.followups:
        for action in review.followups[:20]:
            lines.append(f"- [{action.paper_id}] {action.text}")
    else:
        lines.append("- No open follow-up actions.")
    lines.extend(["", "## Next Recommended Papers", "", reading_queue_report(review.queue, title="Next Reading Queue").split("\n", 4)[-1].rstrip()])
    return "\n".join(lines).rstrip() + "\n"


def _escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _display_source(source: str, base_path: str | Path | None) -> str:
    if not base_path or not source:
        return source
    source_path = Path(source)
    if not source_path.is_absolute():
        return source
    return _relative_to_root(source_path, base_path)
