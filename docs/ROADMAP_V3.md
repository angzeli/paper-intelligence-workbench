# Roadmap v3

## v3.3 Quality Gate Patch

- Add a local quality-gate runner for tests, lint, format check, script type
  check, CLI smoke, notebook validation, data-safety audit, and package build.
- Keep ruff and mypy as optional development tooling, not runtime dependencies.
- Keep package-wide typing and broad formatting as future stabilization work.

## v3.2 Compatibility Patch

- Add historical workspace fixtures for legacy data, early project profiles,
  v2.0 dogfood scaffolds, v3.0rc projects, malformed workspaces, partial
  migrations, path escapes, and extra-column registries.
- Add read-only compatibility inspection and matrix commands.
- Keep migration dry-run first and copy-based.

## v3.1 Support Bundle Patch

- Add safe-by-default support bundles for sanitized local diagnostics.
- Keep diagnostic exports free of PDFs, full notes, full drafts, cache DBs,
  backups, raw audit logs, secrets, and private comments.
- Keep verbose diagnostic output local-only and clearly labelled.

## v3 Stable Surface

- Keep `init`, `project`, `template`, `dogfood`, registry/BibTeX validation,
  note templates, claim extraction, core reports, doctor, dashboard, and support
  diagnostics stable.
- Keep manuscript QA, sync apply, workflow recipes, evidence graph exports,
  review packets, indexed search, claim lifecycle, and rebuild metadata
  experimental until real dogfooding confirms their contracts.
- Avoid major feature expansion before more real dogfooding.

## Before A Public v3 Release

- Run a real 10-15 paper dogfood project.
- Confirm docs match the commands a new user actually runs.
- Refresh `reports/index.md`.
- Re-run full tests, notebook validation, data-safety audit, and smoke CLI.
- Decide whether any experimental sidecars need a migration note.

## After Public v3 Stabilization

- Split `paper_workbench/cli.py` only with command-contract coverage in place.
- Reduce overlapping docs and archive stale generated reports.
- Dogfood evidence graph, workflow runner, review packets, and claim lifecycle
  before marking any of them stable.
- Dogfood support bundles on one real project before recommending external
  issue sharing.

## Not In Scope

- Cloud sync.
- LLM summarization.
- Publisher scraping.
- Web application UI.
- Automatic PDF text extraction.
- Scientific truth evaluation.
