# Architecture Review v1.8

Date: 2026-06-11

## Scope

This review inspected the repository after v1.7 with the goal of finding safe
internal cleanup opportunities without changing public CLI behavior or adding
major new features.

## Findings

### Modules Doing Too Much

- `paper_workbench/cli.py` is the clearest pressure point at roughly 2,900
  lines. It owns parser construction, command handlers, path resolution,
  output preflighting, audit-log wiring, and many report writes.
- `paper_workbench/rules.py`, `paper_workbench/index.py`,
  `paper_workbench/reading.py`, `paper_workbench/sync.py`, and
  `paper_workbench/authoring.py` are large, but mostly cohesive around their
  domains.

### Duplicated Parsing And Normalization

- Theme ID normalization appeared in several places as ad hoc
  `strip/lower/replace` logic.
- v1.8 added `normalize_theme_id` in `paper_workbench.tags` and moved
  theme-aware exports and checklist filtering onto that shared helper.

### Duplicated Path Display

- Relative path rendering had near-identical local implementations in search,
  indexed search, import reports, and report indexes.
- v1.8 added `display_path` in `paper_workbench.paths` and made those callers
  use the shared helper while preserving the existing `paper_workbench.index.display_path`
  compatibility function used by the CLI.

### Duplicated Report Generation

- The report-writing pattern is still repeated in `cli.py`, but the current
  no-overwrite behavior is covered by tests. Larger extraction should be done
  only with dedicated CLI contract coverage.

### Tests That Are Brittle

- Historical release-hygiene tests still assert exact current release report
  groupings. That is useful as a release gate, but it requires updating with
  each new release report set.
- Absolute-path warning tests intentionally include platform path strings; they
  are acceptable but should remain isolated from generated release reports.

### Docs That Overlap

- `docs/CLI_REFERENCE.md`, `docs/cli-reference.md`, `docs/CLI_SURFACE.md`, and
  `docs/COMMAND_CONTRACTS.md` overlap. Keep `CLI_SURFACE.md` and
  `COMMAND_CONTRACTS.md` as stability docs, and keep the references as user
  walkthroughs.
- API docs now clarify that low-level path helpers are shared internals rather
  than a broad plugin surface.

### Generated Reports That Are Stale

- The reports directory intentionally keeps historical reports. Current release
  navigation depends on `reports/index.md`; stale or misclassified current
  reports should be fixed through report-index tests rather than manual edits.

### Public APIs To Mark Internal

- The stable external interface remains the `paperwb` CLI plus documented local
  file formats.
- `paper_workbench.cli`, `paper_workbench.io`, and most low-level path helpers
  remain internal implementation details.
- `paper_workbench.index.display_path` is retained as a compatibility wrapper,
  but new internal callers should use `paper_workbench.paths.display_path`.

## Safe Refactors Implemented

- Added shared `paper_workbench.paths.display_path`.
- Reused shared path display in search, indexed search, import reports, and
  report-index rendering.
- Added `paper_workbench.tags.normalize_theme_id`.
- Reused theme normalization in theme claim exports, Obsidian theme pages, and
  CLI checklist filtering.
- Updated API/CLI surface docs to v1.8.
- Added focused regression tests for shared path display, theme normalization,
  theme-claim export, and v1.8 report-index grouping.

## Deferred Work

- Split `paper_workbench/cli.py` into command-group modules after adding more
  command-contract coverage.
- Introduce a common report-write helper only if it can preserve all existing
  overwrite and audit-log behavior.
- Consolidate historical docs after a separate docs de-duplication review.
- Avoid moving parser internals without adversarial fixture coverage.
