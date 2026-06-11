# v0.8 Recommended Patch Plan

## High Priority

- Add explicit CSV/JSON export for the local file registry audit.
- Add report regression tests for v0.7 local-file reports.
- Add advisory PDF metadata extraction only if a lightweight optional dependency is justified.
- Add safer conflict previews before replacing existing `local_pdf_path` values.
- Add project-profile configuration for custom scan folders.

## Medium Priority

- Add optional recursive text-sidecar indexing controls shared by `files` and `index`.
- Add file-registry cleanup reports for stale links.
- Add reading-list filters for papers with missing local files.
- Add Obsidian export links to local file registry records.
- Add local-file audit summaries to `paperwb doctor`.

## Low Priority

- Add local-only HTML versions of file audit reports.
- Add checksum verification for backup bundles.
- Add optional file-size threshold profiles for different storage environments.

## Not Worth Doing Yet

- Do not add OCR.
- Do not parse full PDF text by default.
- Do not download PDFs.
- Do not scrape publisher websites.
- Do not move local files into managed storage without an explicit user request.

## Overengineering Risks

- Turning the file registry into source-of-truth storage would make recovery harder than the current CSV/Markdown workflow.
- Automatic metadata reconciliation can overwrite careful user-entered metadata if not kept advisory.
- Recursive full-text ingestion can accidentally capture copyrighted material unless the boundary remains explicit.
