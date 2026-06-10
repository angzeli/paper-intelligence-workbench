# v0.5 Recommended Patch Plan

## High Priority

- Add an import preview table with side-by-side source and matched registry rows.
- Add conflict-resolution commands for ambiguous DOI/title/BibTeX-key matches.
- Add report diff tooling for golden report snapshot changes.
- Add note repair diagnostics for malformed claim blocks.
- Add importer-specific summary JSON for automation.

## Medium Priority

- Add citation-key suggestion commands without auto-changing keys.
- Add optional local HTML export for Markdown reports.
- Add richer RIS field coverage with explicit limitations.
- Add BibTeX import handling for more macro and concatenation cases.
- Add backup bundle restore validation without destructive restore.

## Low Priority

- Add spreadsheet-friendly XLSX exports if a lightweight dependency is justified.
- Add local-only fuzzy matching for duplicate title detection.
- Add custom Obsidian frontmatter templates.
- Add configurable reading-list sorting.

## Not Worth Doing Yet

- Cloud synchronization.
- Publisher scraping.
- LLM summarization.
- Full Zotero replacement behavior.
- Mandatory SQLite backend.

## Overengineering Risks

- Making importers silently "fix" metadata.
- Adding interactive conflict resolution before report-based workflows are stable.
- Treating Obsidian export as a web app or knowledge-graph replacement.
- Including PDFs in backups by default.
