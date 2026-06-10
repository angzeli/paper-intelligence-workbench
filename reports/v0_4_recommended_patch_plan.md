# v0.4 Recommended Patch Plan

## High Priority

- Add a report-diff helper that explains golden snapshot changes section by section.
- Add synthetic fixture-size profiles such as `small`, `medium`, and `large`.
- Add a note diagnostics report that groups malformed claim blocks by repair action.
- Add report filters for theme, tag, reading status, and severity.
- Add a stable machine-readable summary output for `doctor` and citation audit.

## Medium Priority

- Add citation-key suggestion commands using a safe `FirstAuthorYearShortTitle` style.
- Add optional local HTML export for Markdown reports.
- Add additional BibTeX macro and concatenation edge fixtures.
- Add stress tests for project names with hyphens and underscores.
- Add a report index generator for stress and release artifacts.

## Low Priority

- Add richer reading-priority dashboards.
- Add local-only fuzzy title matching.
- Add optional CSV-to-project import helpers.
- Add a small terminal summary command for next reading actions.

## Not Worth Doing Yet

- Full CSL formatting.
- A web app.
- Cloud synchronization.
- LLM or embedding search.
- Publisher scraping.
- A mandatory database backend.

## Possible Future Integrations

- Optional Zotero export/import workflow using local files.
- Optional SQLite or SQLite FTS backend for larger projects.
- Optional static HTML report publishing from generated Markdown.

## Overengineering Risks

- Turning the conservative Markdown parser into a fragile custom language.
- Letting golden snapshots become a substitute for semantic report assertions.
- Adding dependencies before the standard library approach has clear limits.
- Treating synthetic stress data as realistic scientific evidence.

