# v0.3 Recommended Patch Plan

## High Priority

- Add a non-destructive workspace migration report for moving legacy `data/` files into project profiles.
- Improve BibTeX macro/string handling while keeping warnings conservative.
- Add citation-key suggestions using `FirstAuthorYearShortTitle`, with no automatic changes.
- Add note diagnostics that point to malformed claim fields and missing required metadata.

## Medium Priority

- Add optional local HTML export for Markdown reports.
- Add filters to reports for tags, reading status, priority, and inclusion status.
- Add project-level summary output with unread papers, missing notes, weak claims, and next actions.
- Add a report index generator that links all reports in a profile or legacy workspace.

## Low Priority

- Add SQLite FTS as an optional local-only backend for larger projects.
- Add CSV import helpers for common Zotero-style exports.
- Add richer author normalization and initials handling.
- Add configurable evidence-type weights per project.

## Not Worth Doing Yet

- Full CSL citation formatting.
- Publisher scraping.
- Cloud sync.
- Semantic embeddings.
- LLM-based summarization.
- A web app.

## Possible Future Integrations

- Local Zotero BibTeX export/import workflows.
- Local PDF text extraction for user-owned PDFs only.
- Editor snippets for structured note templates.
- Static HTML report export.

## Overengineering Risks

- Turning the tool into a database-first citation manager too early.
- Building a perfect BibTeX parser instead of transparent validation.
- Adding semantic search before the local data model is stable.
- Making project profiles too configurable for small literature-review projects.
