# v1.3 Recommended Patch Plan

## High Priority

- Add warnings when starting a new active session for a paper that already has
  an active session.
- Add a non-destructive `reading cancel SESSION_ID` command.
- Add optional `--since` and `--until` filters for `reading review`.
- Add tests for malformed reading-session JSONL recovery.

## Medium Priority

- Add CSV exports for reading queue and follow-up reports.
- Add stable user-provided follow-up labels so note action IDs survive
  reordering.
- Add draft-aware queue reasons for papers cited in drafts but missing notes.
- Add reading review diff reports between weeks.

## Low Priority

- Add compact terminal table output for weekly reading reviews.
- Add optional project-specific reading-goal templates.
- Add a local-only calendar-style Markdown summary.

## Explicitly Not Worth Doing Yet

- No interactive TUI dependency.
- No calendar integration.
- No automatic paper reading.
- No LLM-generated session summaries or notes.
- No remote sync.

