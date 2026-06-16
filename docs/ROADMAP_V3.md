# Roadmap v3

## v3.0rc Freeze

- Keep `init`, `project`, `template`, `dogfood`, registry/BibTeX validation,
  note templates, claim extraction, core reports, doctor, and dashboard stable.
- Keep manuscript QA, sync apply, workflow recipes, evidence graph exports,
  review packets, indexed search, claim lifecycle, and rebuild metadata
  experimental until real dogfooding confirms their contracts.
- Avoid major feature expansion before the actual v3.0.0 tag.

## Before v3.0.0

- Run a real 10-15 paper dogfood project.
- Confirm docs match the commands a new user actually runs.
- Refresh `reports/index.md`.
- Re-run full tests, notebook validation, data-safety audit, and smoke CLI.
- Decide whether any experimental sidecars need a migration note.

## After v3.0.0

- Split `paper_workbench/cli.py` only with command-contract coverage in place.
- Reduce overlapping docs and archive stale generated reports.
- Dogfood evidence graph, workflow runner, review packets, and claim lifecycle
  before marking any of them stable.

## Not In Scope

- Cloud sync.
- LLM summarization.
- Publisher scraping.
- Web application UI.
- Automatic PDF text extraction.
- Scientific truth evaluation.
