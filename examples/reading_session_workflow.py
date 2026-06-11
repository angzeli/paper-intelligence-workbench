"""Synthetic reading-session workflow example.

Run from the repository root:

    python examples/reading_session_workflow.py

The script uses temporary synthetic data only. It does not read papers,
fabricate claims, or modify committed project notes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from paper_workbench.reading import (
    build_reading_queue,
    build_weekly_review,
    collect_followups,
    finish_reading_session,
    followups_report,
    load_reading_sessions,
    reading_queue_report,
    start_reading_session,
    weekly_reading_review_report,
)
from paper_workbench.registry import load_registry, save_registry
from paper_workbench.schema import Author, Claim, Paper, PaperNote, ProjectTheme


def main() -> int:
    with TemporaryDirectory(prefix="paperwb_reading_") as workspace:
        root = Path(workspace)
        registry = root / "registry.csv"
        notes_dir = root / "notes"
        sessions_path = root / ".paperwb" / "reading_sessions.jsonl"

        papers = [
            Paper(
                paper_id="synthetic_reading_a",
                title="Synthetic Reading Queue Probe A",
                authors=[Author(raw_name="Synthetic Author")],
                year="2026",
                bibtex_key="syntheticReadingA2026",
                tags=["photocorrosion"],
                reading_status="unread",
                priority="high",
                reading_priority="critical",
                included_in_lit_review="true",
                added_date="2026-06-01",
            )
        ]
        themes = [ProjectTheme(theme_id="photocorrosion", name="Photocorrosion", tags=["photocorrosion"], min_claims=2)]
        existing_note = PaperNote(
            paper_id="synthetic_reading_a",
            claims=[
                Claim(
                    claim_id="synthetic_reading_a_c1",
                    paper_id="synthetic_reading_a",
                    claim_text="Synthetic weak claim that still needs a page location.",
                    supports_theme="photocorrosion",
                    strength="weak",
                )
            ],
            follow_up_actions=["Add exact evidence location before citing."],
        )

        save_registry(papers, registry)
        queue = build_reading_queue(papers, [existing_note], existing_note.claims, themes)
        print(reading_queue_report(queue), end="")

        session, _note_path, _created, warnings = start_reading_session(
            paper_id="synthetic_reading_a",
            project="synthetic_demo",
            root=root,
            papers=load_registry(registry),
            registry_path=registry,
            notes_dir=notes_dir,
            sessions_path=sessions_path,
            reading_goal="Check whether the weak claim has a usable evidence location.",
            now=datetime(2026, 6, 10, 9, 0, tzinfo=timezone.utc),
        )
        if warnings:
            print("Warnings:", "; ".join(warnings))

        finish_reading_session(
            session_id=session.session_id,
            project="synthetic_demo",
            papers=load_registry(registry),
            registry_path=registry,
            sessions_path=sessions_path,
            status="read",
            duration_minutes=35,
            follow_up_actions=["Find a second primary-evidence paper."],
            claims_added=0,
            now=datetime(2026, 6, 10, 9, 35, tzinfo=timezone.utc),
        )

        sessions = load_reading_sessions(sessions_path)
        followups = collect_followups(
            project="synthetic_demo",
            papers=load_registry(registry),
            notes=[existing_note],
            sessions=sessions,
            themes=themes,
        )
        print(followups_report(followups), end="")

        review = build_weekly_review(
            project="synthetic_demo",
            papers=load_registry(registry),
            notes=[existing_note],
            claims=existing_note.claims,
            themes=themes,
            sessions=sessions,
            followups=followups,
        )
        print(weekly_reading_review_report(review), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
