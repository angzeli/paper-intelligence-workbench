# Historical v0.6 Recommended Patch Plan

This report is retained as a historical v0.5 search/indexing follow-up plan. It is not the current next-step plan for the v0.6 authoring-workbench release. See `v0_7_recommended_patch_plan.md` for the active recommended patch plan.

## High Priority

- Add field filters for indexed search, such as `--source-type`, `--paper-id`, `--year`, and `--tag`.
- Improve snippets with simple matched-term highlighting in Markdown.
- Add a stale-index repair workflow that prints the exact rebuild command.
- Add report diff tooling for generated Markdown reports.
- Add tests for recursive sidecar discovery if that behavior is introduced.

## Medium Priority

- Add optional recursive sidecar indexing behind an explicit flag.
- Add search-result CSV or JSON export.
- Add richer index metadata, such as source file counts and skipped sidecars.
- Add cache migration checks if index schema changes.
- Add project summary links to index status and search demo reports.

## Low Priority

- Add local-only HTML export for search reports.
- Add interactive conflict previews for imports.
- Add optional note-repair suggestions for malformed claim blocks.
- Add citation-key suggestions without auto-changing user data.

## Not Worth Doing Yet

- Do not add embeddings.
- Do not add remote semantic search.
- Do not parse PDFs by default.
- Do not replace the CSV/Markdown/BibTeX source-of-truth workflow with SQLite.

## Overengineering Risks

- Turning the rebuildable cache into an authoritative database would make user data recovery harder.
- Adding background file watchers would increase complexity without clear v0.6 value.
- Sophisticated ranking can become misleading unless it remains explainable.
