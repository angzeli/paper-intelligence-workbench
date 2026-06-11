# v1.7 Recommended Patch Plan

## High Priority

- Add dashboard filters for `--theme`, `--tag`, `--status`, and
  `--priority`.
- Add report-regression checks for dashboard Markdown sections and count
  tables.

## Medium Priority

- Add CSV and JSON exports for next actions.
- Add a compact terminal view for small panes.
- Add current-feature notebook or script coverage for the dashboard workflow.
- Add severity/category filters for rule findings before dashboard aggregation.
- Add grouped issue-count summaries so duplicated workspace, citation-audit,
  and rule-adapter findings are easier to interpret.

## Low Priority

- Add optional read-only interactive selection for showing sections such as
  projects, next actions, missing notes, weak claims, and reading queue.
- Add colorized terminal output only if it can be done without a required
  runtime dependency.

## Explicitly Not Worth Doing Yet

- Do not add a web dashboard.
- Do not add a heavy TUI framework.
- Do not auto-run next actions from the dashboard.
- Do not use LLMs to rank or explain actions.
