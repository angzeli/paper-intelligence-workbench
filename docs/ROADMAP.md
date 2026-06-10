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

## v0.5 Completed

- Optional local SQLite search index.
- FTS5-backed retrieval when available, with table-scan fallback.
- Project-aware indexed search.
- Registry, BibTeX, note, claim, theme, tag, and sidecar indexing.
- Stale-index diagnostics using content hashes.
- Synthetic full-text sidecar fixtures.

## Near-Term Patches for v0.6

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

CSV, JSON, Markdown, and BibTeX remain the authoritative source files. The v0.5 SQLite index is a rebuildable cache for larger-project search, not an authoritative database.

## Search

Default search remains substring-based. Indexed search is opt-in and local-only. Future local-only improvements could include richer field filters, better snippet highlighting, and report diff search. Embeddings and remote semantic APIs are out of scope for this project boundary.

## Review Workflows

Possible future commands:

- theme-specific checklist exports
- report diffing between review drafts
- note completeness scoring
- unresolved question summaries
- safer BibTeX key normalization commands
