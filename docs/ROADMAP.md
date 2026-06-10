# Roadmap

The MVP is intentionally CLI-first, dependency-light, and local-only.

## v0.3 Completed

- Deterministic synthetic corpus generation.
- Checked-in multi-project stress workspace fixtures.
- Parser edge-case fixtures for structured notes and BibTeX.
- Golden report snapshots for stress reports.
- CLI stress tests and performance sanity reporting.

## v0.4 Completed

- Local import subsystem for Zotero-style CSV, generic CSV mapping, BibTeX, and RIS.
- Import reports with duplicate, warning, dry-run, and unmapped-field summaries.
- Obsidian-friendly Markdown vault export.
- Local backup bundle export with manifest and no PDFs by default.
- Richer reading-list filters and CSV output.
- Round-trip import/export tests.

## Near-Term Patches for v0.5

- Add report diff tooling that explains golden snapshot changes.
- Add optional fixture-size profiles such as small, medium, and large.
- Add more robust BibTeX string and macro handling.
- Add optional HTML export for Markdown reports.
- Add safer citation-key suggestions such as `FirstAuthorYearShortTitle`.
- Add richer report filters for specific tags, statuses, and themes.
- Add note repair diagnostics for malformed claim blocks.
- Add non-destructive workspace migration reports for moving legacy `data/` work into profiles.
- Add import preview tables and conflict-resolution commands for ambiguous matches.

## Project Profiles

v0.2 supports multiple literature-review projects in one workspace:

```text
projects/zis_photocatalysis/
projects/finance_reading/
projects/ml_methods/
```

Each profile keeps separate registries, notes, themes, BibTeX files, and reports.

## Storage

CSV, JSON, Markdown, and BibTeX are enough for v1. A lightweight SQLite backend could be useful later for larger projects, but should remain optional and locally reproducible.

## Search

Search is substring-based in v1. Future local-only improvements could include fielded search, trigram matching, or SQLite FTS. Embeddings and remote semantic APIs are out of scope for this project boundary.

## Review Workflows

Possible future commands:

- theme-specific checklist exports
- report diffing between review drafts
- note completeness scoring
- unresolved question summaries
- safer BibTeX key normalization commands
