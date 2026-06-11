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
- Markdown exports for dashboard, next actions, and project-health summary.
- Explainable next-action generation with priority, reason, command
  suggestion, and related paper/claim/rule/workspace item.

## Commands Checked

- `python -m paper_workbench.cli --help`
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --limit 3`
- `python -m paper_workbench.cli dashboard --limit 3`
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --view health --manuscript drafts/synthetic_unknown_citations.md --limit 3`
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --out reports/dashboard_v1_6.md --force`
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --view next-actions --out reports/next_actions_v1_6.md --force`
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --view health --manuscript drafts/synthetic_unknown_citations.md --out reports/project_health_summary_v1_6.md --force`

## Tests Run

- `python -m pytest tests/test_dashboard_v1_6.py -q`
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
- The dashboard can be noisy when built-in rule adapters and citation audits
  report overlapping evidence gaps.
- Manuscript QA warnings appear only when a draft is passed with
  `--manuscript`.

## Data Safety

- No cloud APIs, LLM APIs, browser, scraping, or network access are used.
- The dashboard does not write registry rows, notes, BibTeX files, drafts,
  session logs, follow-up state, or rule files.
- Existing overwrite protection applies to `--out` Markdown reports.

## Recommended v1.7 Scope

- Add optional dashboard filters by theme, tag, status, and priority.
- Add compact terminal output for narrow panes.
- Add optional CSV/JSON export for next actions.
- Consider read-only interactive selection only if it remains dependency-light
  and non-destructive.

