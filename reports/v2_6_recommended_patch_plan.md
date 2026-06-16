# v2.6 Recommended Patch Plan

## Goal

Use v2.6 as an internal architecture stabilization pass before another release
candidate cycle.

## Recommended Scope

- Consolidate duplicated project/path/output handling in CLI helpers.
- Review report-generation helpers and reduce repeated Markdown table logic.
- Clarify public versus internal Python APIs.
- Add behavior-preservation tests for any refactored stable command.
- Keep rebuild metadata experimental until it has been dogfooded on a real
  project.

## Do Not Expand

- Do not add cloud sync, LLM summarization, PDF scraping, or web UI features.
- Do not turn workflow recipes into arbitrary command runners.
- Do not make rebuild metadata a stable schema until real projects validate the
  target granularity.

## Validation Before v2.6 Completion

- Run full pytest.
- Run representative stable CLI smoke tests.
- Run `paperwb rebuild plan/status` on a synthetic project.
- Confirm no cache, stress, backup, audit, PDF, or SQLite files are staged.
