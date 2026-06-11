# Hostile Maintainer Review: v1.2 Current Repository

Date: 2026-06-11

## Release Verdict

**Verdict: do not ship v1.2 to external users until the new reading-session
write-path blockers are fixed.**

The repository is substantially more mature than the older v1.1 hostile review
suggested. The previous `paperwb report all` blockers are fixed: output paths
are preflighted and `report all --out` is rejected cleanly. The package remains
local-first, has no runtime dependencies, and the full test suite currently
passes.

The current release blocker is narrower but serious: `paperwb reading start`
and `paperwb reading finish` can mutate user data before failing on an existing
`--out` report path. That violates the safe-write contract and is especially
bad because `reading finish` updates the authoritative registry reading status.

Validation performed during this review:

- `git status --short --branch --ignored=matching`: tracked worktree clean;
  ignored IDE/cache/build/scratch artifacts present.
- `python -m pytest -q`: passed.
- `python -m pytest --collect-only -q`: collected the current suite across 22
  test modules.
- `python scripts/check_notebooks.py`: passed; 8 notebooks checked
  structurally.
- `python scripts/data_safety_audit.py --out scratch/hostile_review_data_safety.md --strict`:
  passed with 0 errors and 11 warnings.
- `paperwb --help`: passed.
- `paperwb reading --help`: passed.
- `paperwb draft audit drafts/synthetic_photocorrosion_section.md --project zis_photocatalysis --out scratch/hostile_draft_audit.md --force`:
  passed.
- `paperwb report all` with a seeded later output collision: failed before
  writing partial reports, as expected.
- `paperwb report all --out ...`: returned exit code 2 and wrote nothing, as
  expected.
- `paperwb reading start` and `paperwb reading finish` output-collision probes:
  both revealed partial writes before failure.

## Release Blockers

### 1. `paperwb reading start --out EXISTING` mutates state before failing

Probe setup used a scratch-only registry and pre-existing output file:

```bash
paperwb reading start probe \
  --registry scratch/hostile_reading_probe/registry.csv \
  --notes-dir scratch/hostile_reading_probe/notes \
  --sessions scratch/hostile_reading_probe/sessions.jsonl \
  --out scratch/hostile_reading_probe/existing.md
```

Observed behavior:

- exit code: `2`
- error: output report already exists
- nevertheless, the command created:
  - `scratch/hostile_reading_probe/notes/probe.md`
  - `scratch/hostile_reading_probe/sessions.jsonl`
- it also updated `notes_path` in the registry.

Why this blocks release:

- A failed command should not silently start a reading session.
- A failed command should not create a note or update registry metadata.
- This breaks the documented no-overwrite/safe-write model.

Required fix:

- Preflight `--out` before calling `start_reading_session()`.
- Add a regression test that seeds an existing `--out`, runs `reading start`,
  and asserts the registry, note directory, and session log remain unchanged.

### 2. `paperwb reading finish --out EXISTING` updates registry/session state before failing

Probe:

```bash
paperwb reading finish read_probe_20260611T163128Z \
  --registry scratch/hostile_reading_probe/registry.csv \
  --sessions scratch/hostile_reading_probe/sessions.jsonl \
  --status read \
  --out scratch/hostile_reading_probe/existing.md
```

Observed behavior:

- exit code: `2`
- error: output report already exists
- nevertheless, the session was marked completed in the JSONL log
- the registry `reading_status` changed from `unread` to `read`
- `last_reviewed_date` was set.

Why this blocks release:

- This is an authoritative data mutation hidden behind a failed report write.
- A user can reasonably retry the command and create inconsistent or duplicate
  outcomes.
- It contradicts the project's data-integrity positioning.

Required fix:

- Preflight `--out` before calling `finish_reading_session()`.
- Add a regression test that asserts an output collision leaves the registry
  and session log byte-for-byte unchanged.

## High-Priority Issues

### 1. Weekly reading reports are time-dependent without an `--as-of` control

`build_weekly_review()` uses `datetime.now(timezone.utc)` internally. The
committed synthetic v1.2 session fixture is dated 2026-06-08 and 2026-06-09.
The generated `reports/weekly_reading_review_v1_2.md` is reproducible only
while those dates fall inside the default 7-day window.

Why this matters:

- Generated reports are supposed to be reproducible from local inputs.
- Regenerating v1.2 reports after the fixture ages out will change counts to
  zero unless `--days` is expanded manually.

Required fix:

- Add an explicit `--as-of YYYY-MM-DD` or equivalent deterministic clock input
  for `paperwb reading review`.
- Regenerate v1.2 reports using that deterministic date.
- Add a test for deterministic review-window behavior.

### 2. Reading session IDs can collide for same-paper starts in the same second

`make_session_id()` uses `paper_id` plus a UTC timestamp with second
precision. Two starts for the same paper in the same second produce identical
IDs. `finish_reading_session()` then finds the first matching session, so a
duplicate ID can update the wrong record.

Required fix:

- Add a collision-resistant suffix or retry loop.
- Add a test that starts two same-paper sessions with the same injected time.

### 3. Corrupt reading-session and follow-up state is silently ignored

`load_reading_sessions()` skips invalid JSONL lines without surfacing a warning.
`load_followup_state()` returns `{}` on invalid JSON. That avoids crashes, but
it can make status/review/follow-up reports silently undercount user state.

Required fix:

- Return parse warnings, or add diagnostic commands that report corrupted local
  reading/follow-up state.
- Add failure-path CLI tests for malformed session JSONL and follow-up state.

### 4. `paperwb followups done ACTION_ID` accepts arbitrary action IDs

The command writes completion state for any string without verifying that the
action currently exists in notes or session logs. A typo can create a "done"
record that does not correspond to any action and is not obvious to the user.

Required fix:

- Validate the action ID against collected follow-ups when registry/notes/session
  context is available, or at least warn when marking an unknown action.
- Add a CLI failure-path test.

### 5. Tracked historical reports still contain local absolute paths

Examples found by scan:

- `reports/import_zotero_csv_v0_4.md`
- `reports/import_generic_csv_v0_4.md`
- `reports/import_bibtex_v0_4.md`
- `reports/import_ris_v0_4.md`
- `reports/stress_workspace_health_v0_3.md`

Why this matters:

- They are not secrets, but they leak maintainer machine paths and look
  unprofessional in a public release.
- They undermine recent work to relativize report paths.

Required fix:

- Regenerate or normalize historical generated reports that remain in the
  public report gallery/index.
- Add a report hygiene test that flags `/Users/`, `/private/tmp`, and similar
  paths in active generated reports, allowing explicitly historical simulation
  reports only when labelled.

## Medium-Priority Issues

- `paper_workbench/cli.py` is still a very large command orchestration file.
  It is now carrying init, project, validation, import, export, report,
  authoring, draft, file, backup, migration, search, reading, and follow-up
  behavior in one module.
- `paperwb reading start` permits multiple active sessions for the same paper
  without warning. That may be acceptable, but it should be explicit.
- The reading queue currently ranks already `deeply_read` papers highly when
  they have high priority and weak-theme signals. That is transparent but
  surprising for a "what to read next" workflow.
- Draft citation matching remains lexical and useful, but it still has known
  false-positive/false-negative risks around tables, footnotes, and unusual
  Markdown structures.
- BibTeX parsing is intentionally lightweight; macro/string handling and broken
  entry recovery are still limited.
- Local file link/unlink workflows touch multiple metadata files. I did not see
  write-failure simulation proving they cannot leave partially updated state.
- Notebook validation is structural only. The project has notebook examples,
  but CI/release validation does not execute them by default.
- Some generated release reports are historical but live beside active release
  reports with little separation.

## Low-Priority Polish

- CLI help still embeds old version labels in places, for example "v0.7
  local-file audit reports" and "v0.9 workspace integrity checks".
- `docs/index.md` still says "No site generator is required for v0.8", which is
  stale wording in a v1.2 repository.
- Uppercase reference docs and lowercase docs-site pages overlap heavily.
- `reports/` is crowded enough that new users can easily open stale risk or
  readiness reports.
- Ignored build artifacts are present locally, including a stale
  `dist/paper_intelligence_workbench-1.1.0.tar.gz`; it is ignored and untracked
  but should not be included in any release archive.

## Missing Tests

- `reading start` output-collision no-mutation regression.
- `reading finish` output-collision no-mutation regression.
- duplicate reading-session ID handling.
- duplicate active-session warning or documented behavior.
- malformed reading-session JSONL diagnostics.
- malformed follow-up state diagnostics.
- `followups done` unknown action behavior.
- deterministic `reading review` window behavior.
- report hygiene checks for absolute local paths in active generated reports.
- write-failure simulation for multi-file local-file link/unlink metadata
  updates.

## Documentation Mismatches

- `docs/index.md` has stale v0.8 wording.
- `docs/CLI_SURFACE.md` and `docs/COMMAND_CONTRACTS.md` describe no-overwrite
  behavior broadly, but `reading start/finish` currently violate it when `--out`
  collides.
- The report directory contains historical release-readiness reports that
  disagree with the current v1.2 risk state unless the reader knows to treat
  `hostile_review_latest.md` as canonical.
- The reading workflow docs correctly warn about no fabrication and note
  preservation, but they do not warn that session logs currently lack malformed
  state diagnostics.

## CLI Usability Problems

- `reading start` and `reading finish` report output collisions only after
  state mutation.
- `followups done` can succeed for a typo.
- `reading review` has no deterministic clock option.
- `reading queue` can recommend already deeply read papers without a clear
  "why still recommended" distinction.
- Some command help labels still reference old version milestones rather than
  feature names.

## Data-Safety Risks

- No tracked PDFs, SQLite caches, pyc files, `.paperwb` caches, backup archives,
  or IDE files were found.
- Runtime dependencies remain empty and there is no evidence of cloud/LLM API
  dependencies.
- Ignored local artifacts are present and should be excluded from release
  archives.
- Tracked generated reports still contain local absolute paths.
- The reading-finish output-collision bug can silently change authoritative
  registry state despite a failed command.

## Overengineering Risks

- The tool has grown into many workflows while keeping all orchestration in one
  CLI module. More feature growth without modular command groups will make
  safety reviews harder.
- There are many generated reports and overlapping docs. More reports without a
  clearer active/historical split will increase user confusion.
- Reading workflows should stay simple and local; avoid turning them into a TUI,
  scheduler, or automatic recommendation engine before the current safe-write
  issues are fixed.

## Recommended Fix Sequence

1. Fix `reading start` and `reading finish` by preflighting `--out` before any
   note, session, or registry mutation.
2. Add regression tests proving output collisions leave all source files
   unchanged.
3. Add deterministic `reading review --as-of` support and regenerate v1.2
   reading reports with it.
4. Add duplicate session ID protection and tests.
5. Add warnings or diagnostics for malformed reading/follow-up state files.
6. Validate or warn on unknown `followups done` IDs.
7. Normalize local absolute paths in active generated reports and add a report
   hygiene test.
8. Clean stale ignored build artifacts before any public source archive or tag.

