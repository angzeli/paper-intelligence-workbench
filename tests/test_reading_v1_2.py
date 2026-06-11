from __future__ import annotations

from datetime import datetime, timezone
import json
import subprocess
import sys

from conftest import ROOT
from paper_workbench.reading import (
    ReadingSession,
    build_reading_queue,
    build_weekly_review,
    collect_followups,
    filter_followups,
    followups_report,
    load_followup_state,
    load_reading_sessions,
    mark_followup_done,
    reading_queue_report,
    start_reading_session,
    weekly_reading_review_report,
)
from paper_workbench.registry import load_registry, save_registry
from paper_workbench.schema import Author, Claim, Paper, PaperNote, ProjectTheme, ReadingStatus


def run_cli(*args: str):
    return subprocess.run([sys.executable, "-m", "paper_workbench.cli", *args], cwd=ROOT, check=False, text=True, capture_output=True)


def _paper(
    paper_id: str,
    *,
    status: str = "unread",
    priority: str = "",
    reading_priority: str = "",
    tags: list[str] | None = None,
    notes_path: str = "",
    bibtex_key: str = "key2026",
    included: str = "",
) -> Paper:
    return Paper(
        paper_id=paper_id,
        title=f"Synthetic {paper_id} Study",
        authors=[Author(given="Synthetic", family="Author", raw_name="Synthetic Author")],
        year="2026",
        journal="Synthetic Journal",
        bibtex_key=bibtex_key,
        tags=tags or [],
        reading_status=status,
        notes_path=notes_path,
        priority=priority,
        reading_priority=reading_priority,
        included_in_lit_review=included,
        added_date="2026-06-01",
    )


def test_reading_queue_ranks_local_gaps_and_theme_filter():
    papers = [
        _paper("low_read", status="read", priority="low", reading_priority="low", tags=["charge-separation"], notes_path="notes/low.md"),
        _paper("high_gap", status="unread", priority="high", reading_priority="critical", tags=["photocorrosion"], included="true"),
    ]
    notes = [PaperNote(paper_id="low_read", claims=[Claim(claim_id="c1", paper_id="low_read", claim_text="Charge separation changed.", supports_theme="charge-separation", strength="strong")])]
    claims = [claim for note in notes for claim in note.claims]
    themes = [
        ProjectTheme(theme_id="charge-separation", name="Charge separation", tags=["charge-separation"], min_claims=1, min_papers=1),
        ProjectTheme(theme_id="photocorrosion", name="Photocorrosion", tags=["photocorrosion"], min_claims=2, min_papers=1),
    ]

    queue = build_reading_queue(papers, notes, claims, themes)
    assert queue[0].paper_id == "high_gap"
    assert any("missing note" in reason for reason in queue[0].reasons)

    filtered = build_reading_queue(papers, notes, claims, themes, theme="charge-separation")
    assert [item.paper_id for item in filtered] == ["low_read"]
    assert "Reading Queue" in reading_queue_report(queue)


def test_start_reading_session_creates_template_and_preserves_existing_notes(tmp_path):
    registry = tmp_path / "registry.csv"
    notes_dir = tmp_path / "notes"
    sessions = tmp_path / "sessions.jsonl"
    papers = [_paper("session_probe", bibtex_key="", status=ReadingStatus.UNREAD.value)]
    save_registry(papers, registry)

    session, note_path, notes_created, warnings = start_reading_session(
        paper_id="session_probe",
        project="default",
        root=tmp_path,
        papers=load_registry(registry),
        registry_path=registry,
        notes_dir=notes_dir,
        sessions_path=sessions,
        reading_goal="Check method details",
        now=datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc),
    )

    assert session.session_status == "active"
    assert notes_created is True
    assert note_path.exists()
    assert "Paper has no BibTeX key." in warnings
    assert load_registry(registry)[0].notes_path == "notes/session_probe.md"

    note_path.write_text("preserve existing note\n", encoding="utf-8")
    second, _note_path, notes_created_again, _warnings = start_reading_session(
        paper_id="session_probe",
        project="default",
        root=tmp_path,
        papers=load_registry(registry),
        registry_path=registry,
        notes_dir=notes_dir,
        sessions_path=sessions,
        now=datetime(2026, 6, 10, 13, 0, tzinfo=timezone.utc),
    )
    assert second.session_id != session.session_id
    assert notes_created_again is False
    assert note_path.read_text(encoding="utf-8") == "preserve existing note\n"


def test_start_reading_session_generates_unique_ids_for_same_second(tmp_path):
    registry = tmp_path / "registry.csv"
    notes_dir = tmp_path / "notes"
    sessions = tmp_path / "sessions.jsonl"
    save_registry([_paper("collision_probe")], registry)
    now = datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc)

    first, _note_path, _created, _warnings = start_reading_session(
        paper_id="collision_probe",
        project="default",
        root=tmp_path,
        papers=load_registry(registry),
        registry_path=registry,
        notes_dir=notes_dir,
        sessions_path=sessions,
        now=now,
    )
    second, _note_path, _created, _warnings = start_reading_session(
        paper_id="collision_probe",
        project="default",
        root=tmp_path,
        papers=load_registry(registry),
        registry_path=registry,
        notes_dir=notes_dir,
        sessions_path=sessions,
        now=now,
    )

    assert first.session_id == "read_collision_probe_20260610T120000Z"
    assert second.session_id == "read_collision_probe_20260610T120000Z_2"


def test_followups_collect_filter_and_done_state(tmp_path):
    note = PaperNote(paper_id="paper_a", follow_up_actions=["Add page number", "Check limitation"], source_path="notes/paper_a.md")
    paper = _paper("paper_a", tags=["photocorrosion"])
    themes = [ProjectTheme(theme_id="photocorrosion", name="Photocorrosion", tags=["photocorrosion"])]
    actions = collect_followups(project="demo", papers=[paper], notes=[note], sessions=[], themes=themes)
    assert [action.action_id for action in actions] == ["note:paper_a:1", "note:paper_a:2"]

    state_path = tmp_path / "followups.json"
    mark_followup_done("note:paper_a:1", state_path, now=datetime(2026, 6, 10, tzinfo=timezone.utc))
    actions = collect_followups(project="demo", papers=[paper], notes=[note], sessions=[], themes=themes, state=load_followup_state(state_path))
    assert [action.action_id for action in filter_followups(actions)] == ["note:paper_a:2"]
    assert "note:paper_a:1" in followups_report(filter_followups(actions, include_done=True))


def test_followups_report_can_relativize_source_paths(tmp_path):
    note_path = tmp_path / "notes" / "paper_a.md"
    note_path.parent.mkdir()
    note_path.write_text("# synthetic\n", encoding="utf-8")
    note = PaperNote(paper_id="paper_a", follow_up_actions=["Check source path"], source_path=str(note_path))
    paper = _paper("paper_a", tags=["photocorrosion"])
    themes = [ProjectTheme(theme_id="photocorrosion", name="Photocorrosion", tags=["photocorrosion"])]

    report = followups_report(
        collect_followups(project="demo", papers=[paper], notes=[note], sessions=[], themes=themes),
        base_path=tmp_path,
    )

    assert "notes/paper_a.md" in report
    assert str(tmp_path) not in report


def test_weekly_reading_review_report_summarizes_sessions(tmp_path):
    papers = [_paper("paper_a", tags=["photocorrosion"], status="read")]
    note = PaperNote(
        paper_id="paper_a",
        claims=[Claim(claim_id="c1", paper_id="paper_a", claim_text="A weak tracked claim.", supports_theme="photocorrosion", strength="weak")],
        follow_up_actions=["Find primary evidence"],
    )
    sessions_path = tmp_path / "sessions.jsonl"
    registry = tmp_path / "registry.csv"
    save_registry(papers, registry)
    start_reading_session(
        paper_id="paper_a",
        project="demo",
        root=tmp_path,
        papers=papers,
        registry_path=registry,
        notes_dir=tmp_path / "notes",
        sessions_path=sessions_path,
        now=datetime.now(timezone.utc),
    )
    sessions = load_reading_sessions(sessions_path)
    sessions[0].completed_at = datetime.now(timezone.utc).isoformat()
    sessions[0].status_after = "read"
    sessions[0].duration_minutes = 30
    sessions[0].claims_added = 1
    followups = collect_followups(project="demo", papers=papers, notes=[note], sessions=sessions, themes=[ProjectTheme(theme_id="photocorrosion", name="Photocorrosion", tags=["photocorrosion"])])

    review = build_weekly_review(
        project="demo",
        papers=papers,
        notes=[note],
        claims=note.claims,
        themes=[ProjectTheme(theme_id="photocorrosion", name="Photocorrosion", tags=["photocorrosion"], min_claims=2)],
        sessions=sessions,
        followups=followups,
    )
    report = weekly_reading_review_report(review)
    assert "Papers marked read/deeply read: 1" in report
    assert "Find primary evidence" in report


def test_weekly_reading_review_accepts_deterministic_as_of_date():
    papers = [_paper("paper_a", status="read")]
    sessions = [
        ReadingSession(
            session_id="recent",
            project="demo",
            paper_id="paper_a",
            started_at="2026-06-08T10:00:00+00:00",
            completed_at="2026-06-08T10:30:00+00:00",
            status_after="read",
        )
    ]

    included = build_weekly_review(
        project="demo",
        papers=papers,
        notes=[],
        claims=[],
        themes=[],
        sessions=sessions,
        followups=[],
        period_days=7,
        as_of=datetime(2026, 6, 11, 23, 59, tzinfo=timezone.utc),
    )
    excluded = build_weekly_review(
        project="demo",
        papers=papers,
        notes=[],
        claims=[],
        themes=[],
        sessions=sessions,
        followups=[],
        period_days=7,
        as_of=datetime(2026, 6, 20, 23, 59, tzinfo=timezone.utc),
    )

    assert [session.session_id for session in included.sessions] == ["recent"]
    assert excluded.sessions == []


def test_reading_cli_start_finish_and_followups(tmp_path):
    registry = tmp_path / "papers.csv"
    notes_dir = tmp_path / "notes"
    sessions = tmp_path / "sessions.jsonl"
    reports = tmp_path / "reports"
    reports.mkdir()
    save_registry([_paper("cli_probe", status="unread", tags=["photocorrosion"])], registry)

    start = run_cli(
        "reading",
        "start",
        "cli_probe",
        "--registry",
        str(registry),
        "--notes-dir",
        str(notes_dir),
        "--sessions",
        str(sessions),
        "--goal",
        "Fill structured note gaps",
    )
    assert start.returncode == 0, start.stderr
    assert "Reading Checklist" in start.stdout
    note_path = notes_dir / "cli_probe.md"
    assert note_path.exists()
    note_path.write_text(note_path.read_text(encoding="utf-8") + "\n- Add section/page evidence\n", encoding="utf-8")

    session_id = json.loads(sessions.read_text(encoding="utf-8").splitlines()[0])["session_id"]
    finish = run_cli(
        "reading",
        "finish",
        session_id,
        "--registry",
        str(registry),
        "--sessions",
        str(sessions),
        "--status",
        "read",
        "--duration-minutes",
        "42",
        "--claims-added",
        "1",
        "--follow-up",
        "Check one missing citation",
    )
    assert finish.returncode == 0, finish.stderr
    assert load_registry(registry)[0].reading_status == "read"

    status = run_cli("reading", "status", "--sessions", str(sessions))
    assert status.returncode == 0, status.stderr
    assert session_id in status.stdout

    followups = run_cli("followups", "list", "--registry", str(registry), "--notes-dir", str(notes_dir), "--sessions", str(sessions))
    assert followups.returncode == 0, followups.stderr
    assert "Check one missing citation" in followups.stdout

    review_path = reports / "review.md"
    review = run_cli(
        "reading",
        "review",
        "--registry",
        str(registry),
        "--notes-dir",
        str(notes_dir),
        "--sessions",
        str(sessions),
        "--out",
        str(review_path),
    )
    assert review.returncode == 0, review.stderr
    assert "Weekly Reading Review" in review_path.read_text(encoding="utf-8")

    exported = reports / "followups.md"
    export = run_cli("followups", "export", "--registry", str(registry), "--notes-dir", str(notes_dir), "--sessions", str(sessions), "--out", str(exported))
    assert export.returncode == 0, export.stderr
    assert "Follow-up Actions" in exported.read_text(encoding="utf-8")


def test_reading_start_out_collision_does_not_mutate_sources(tmp_path):
    registry = tmp_path / "papers.csv"
    notes_dir = tmp_path / "notes"
    sessions = tmp_path / "sessions.jsonl"
    out = tmp_path / "existing.md"
    save_registry([_paper("safe_start_probe", status="unread")], registry)
    before_registry = registry.read_text(encoding="utf-8")
    out.write_text("keep\n", encoding="utf-8")

    result = run_cli(
        "reading",
        "start",
        "safe_start_probe",
        "--registry",
        str(registry),
        "--notes-dir",
        str(notes_dir),
        "--sessions",
        str(sessions),
        "--out",
        str(out),
    )

    assert result.returncode == 2
    assert registry.read_text(encoding="utf-8") == before_registry
    assert not notes_dir.exists()
    assert not sessions.exists()
    assert out.read_text(encoding="utf-8") == "keep\n"


def test_reading_finish_out_collision_does_not_mutate_sources(tmp_path):
    registry = tmp_path / "papers.csv"
    sessions = tmp_path / "sessions.jsonl"
    out = tmp_path / "existing.md"
    save_registry([_paper("safe_finish_probe", status="unread")], registry)
    sessions.write_text(
        json.dumps(
            {
                "session_id": "session_safe_finish",
                "project": "default",
                "paper_id": "safe_finish_probe",
                "started_at": "2026-06-10T12:00:00+00:00",
                "session_status": "active",
                "status_before": "unread",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    before_registry = registry.read_text(encoding="utf-8")
    before_sessions = sessions.read_text(encoding="utf-8")
    out.write_text("keep\n", encoding="utf-8")

    result = run_cli(
        "reading",
        "finish",
        "session_safe_finish",
        "--registry",
        str(registry),
        "--sessions",
        str(sessions),
        "--status",
        "read",
        "--out",
        str(out),
    )

    assert result.returncode == 2
    assert registry.read_text(encoding="utf-8") == before_registry
    assert sessions.read_text(encoding="utf-8") == before_sessions
    assert out.read_text(encoding="utf-8") == "keep\n"


def test_reading_cli_reports_malformed_session_and_followup_state(tmp_path):
    registry = tmp_path / "papers.csv"
    notes_dir = tmp_path / "notes"
    sessions = tmp_path / "sessions.jsonl"
    state = tmp_path / "followups.json"
    save_registry([_paper("malformed_probe")], registry)
    notes_dir.mkdir()
    sessions.write_text("{bad json\n", encoding="utf-8")
    state.write_text("{bad json", encoding="utf-8")

    status = run_cli("reading", "status", "--sessions", str(sessions))
    assert status.returncode == 0
    assert "could not be parsed as a reading session" in status.stderr

    followups = run_cli("followups", "list", "--registry", str(registry), "--notes-dir", str(notes_dir), "--sessions", str(sessions), "--state", str(state))
    assert followups.returncode == 0
    assert "follow-up completion state is not valid JSON" in followups.stderr


def test_followups_done_rejects_unknown_action_id(tmp_path):
    registry = tmp_path / "papers.csv"
    notes_dir = tmp_path / "notes"
    sessions = tmp_path / "sessions.jsonl"
    state = tmp_path / "followups.json"
    save_registry([_paper("unknown_followup_probe")], registry)
    notes_dir.mkdir()

    result = run_cli(
        "followups",
        "done",
        "note:missing:1",
        "--registry",
        str(registry),
        "--notes-dir",
        str(notes_dir),
        "--sessions",
        str(sessions),
        "--state",
        str(state),
    )

    assert result.returncode == 2
    assert "Unknown follow-up action" in result.stderr
    assert not state.exists()
