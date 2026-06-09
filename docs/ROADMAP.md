# Roadmap

The MVP is intentionally CLI-first, dependency-light, and local-only.

## Near-Term Patches

- Add more robust BibTeX string and macro handling.
- Add optional HTML export for Markdown reports.
- Add safer citation-key suggestions such as `FirstAuthorYearShortTitle`.
- Add richer report filters for specific tags, statuses, and themes.
- Add note repair diagnostics for malformed claim blocks.

## Project Profiles

A future version can support multiple literature-review projects in one workspace:

```text
projects/zis_photocatalysis/
projects/finance_reading/
projects/ml_methods/
```

Each profile could keep separate registries, notes, themes, and reports.

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
