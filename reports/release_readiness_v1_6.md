# Release Readiness v1.6

Date: 2026-06-11

## Verdict

v1.6 is usable as a local terminal-dashboard release candidate after the
validation listed below. The dashboard is read-only except for explicit
Markdown report writes with `--out`.

## Features Added

- `paperwb dashboard` command for terminal summaries.
- Project-aware dashboard aggregation for registry, notes, claims, BibTeX,
  citation audit, workspace health, rules, reading queue, follow-ups, audit
  log, reports, and optional manuscript QA warnings.
- `--view full`, `--view next-actions`, and `--view health`.
- `--no-audit-log` for deterministic dashboard reports that omit ignored local
  audit-log state.
- Positive `--limit` validation for dashboard row counts.
- Markdown exports for dashboard, next actions, and project-health summary.
- Explainable next-action generation with priority, reason, command
  suggestion, and related paper/claim/rule/workspace item.
- Next-action deduplication for repeated missing-evidence findings surfaced by
  workspace health, citation audit, and rule adapters.

## Commands Checked

- `python -m paper_workbench.cli --help`
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --limit 3 --no-audit-log`
- `python -m paper_workbench.cli dashboard --limit 3`
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --limit 0`
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --limit -1`
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --view health --manuscript drafts/synthetic_unknown_citations.md --limit 3 --no-audit-log`
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --out reports/dashboard_v1_6.md --force --no-audit-log`
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --view next-actions --out reports/next_actions_v1_6.md --force --no-audit-log`
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --view health --manuscript drafts/synthetic_unknown_citations.md --out reports/project_health_summary_v1_6.md --force --no-audit-log`

## Tests Run

- `python -m pytest tests/test_dashboard_v1_6.py -q`
- `python -m pytest tests/test_dashboard_v1_6.py tests/test_release_engineering_v0_8.py tests/test_release_hygiene.py -q`
- `python scripts/smoke_cli_workflow.py --quick --out <tmp>/paperwb_smoke_quick_v1_6.md`
- Full-suite `python -m pytest -q` was run before final response for this release.

## Reports Generated

- `reports/dashboard_v1_6.md`
- `reports/next_actions_v1_6.md`
- `reports/project_health_summary_v1_6.md`
- `reports/release_readiness_v1_6.md`
- `reports/v1_7_recommended_patch_plan.md`

## Dashboard Limitations

- The dashboard is plain text and not a full TUI.
- Next actions are heuristic workflow suggestions based on local findings; they
  are not automatically executed.
- Dashboard issue counts can still be noisy when built-in rule adapters and
  citation audits report overlapping evidence gaps, but next actions collapse
  repeated missing-evidence suggestions for the same claim.
- Manuscript QA warnings appear only when a draft is passed with
  `--manuscript`.

## Data Safety

- No cloud APIs, LLM APIs, browser, scraping, or network access are used.
- The dashboard does not write registry rows, notes, BibTeX files, drafts,
  session logs, follow-up state, or rule files.
- Existing overwrite protection applies to `--out` Markdown reports.
- Use `--no-audit-log` for release-facing reports to avoid including ignored
  mutable local audit-log events.

## Recommended v1.7 Scope

- Add optional dashboard filters by theme, tag, status, and priority.
- Add compact terminal output for narrow panes.
- Add optional CSV/JSON export for next actions.
- Consider read-only interactive selection only if it remains dependency-light
  and non-destructive.
