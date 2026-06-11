# Release Readiness v1.2

Date: 2026-06-11

## Verdict

v1.2 is usable as a local reading-session workflow layer on top of the existing
registry, notes, claims, themes, and audit reports.

## Features Added

- `paper_workbench.reading` with reading session, reading queue, follow-up
  action, and weekly reading review utilities.
- `paperwb reading queue` for transparent next-paper ranking.
- `paperwb reading start` for local session creation and safe note-template
  integration.
- `paperwb reading finish` for user-commanded status updates and session
  outcomes.
- `paperwb reading status` and `paperwb reading review` for session and weekly
  review reports.
- `paperwb followups list/export/done` for note/session follow-up actions
  without editing source notes.
- Synthetic v1.2 session fixture at
  `data/examples/reading_sessions_v1_2.jsonl`.
- Example script at `examples/reading_session_workflow.py`.

## Commands Checked

- `paperwb --help`
- `paperwb reading --help`
- `paperwb followups --help`
- `paperwb reading queue --project zis_photocatalysis`
- `paperwb reading start` on a temporary synthetic registry
- `paperwb reading finish` on a temporary synthetic registry
- `paperwb followups list/export` on temporary synthetic data
- `paperwb reading review` using synthetic v1.2 session data

## Reports Generated

- `reports/reading_queue_v1_2.md`
- `reports/reading_session_demo_v1_2.md`
- `reports/followups_v1_2.md`
- `reports/weekly_reading_review_v1_2.md`
- `reports/release_readiness_v1_2.md`
- `reports/v1_3_recommended_patch_plan.md`

## Tests

Validation performed:

- Focused v1.2 reading workflow tests passed.
- Full `pytest` suite passed after updating release metadata expectations.
- Representative CLI smoke tests passed.
- Notebook JSON structure check passed.
- Data-safety audit strict mode completed with 0 errors.

## Safety Assessment

- Reading sessions default to ignored `.paperwb/reading_sessions.jsonl` files.
- Follow-up completion state defaults to ignored `.paperwb/followups_state.json`.
- `reading start` preserves existing notes by default.
- Note overwrite requires explicit `--force-note`.
- `reading finish` updates reading status only when the user supplies a target
  status.
- The queue and review reports do not claim scientific truth or paper quality.

## Known Limitations

- Multiple active sessions for the same paper are allowed.
- Follow-up action IDs from notes depend on note action ordering.
- Queue ranking is simple and transparent, not adaptive.
- Weekly review periods are based on session timestamps only.
- Session storage is JSONL, not a transactional database.

## Recommended v1.3 Scope

- Harden duplicate/interrupted active session handling.
- Add richer follow-up filters and stable optional action labels.
- Add report diffs for reading reviews.
- Add optional CSV export for reading queues and follow-ups.
- Keep all reading workflows local and user-entered.
