# v1.4 Recommended Patch Plan

## High Priority

- Add an explicit sync patch file format for manually approved non-empty field
  updates.
- Add tests for high-risk sync plans that combine create, fill, and conflict
  actions across multiple import formats.
- Add report diff tooling for sync plans and conflict reports.
- Add clearer grouping of conflicts by DOI, title, BibTeX key, and paper ID.

## Medium Priority

- Add project-to-project registry sync planning.
- Add optional CSV export for sync actions and conflicts.
- Add note-conflict detail reports that link directly to local/exported files.
- Add richer Obsidian vault validation for missing index pages and tag pages.

## Low Priority

- Add terminal summary formatting for sync plans.
- Add a local-only command to scaffold a sync review checklist.
- Add optional compressed backup archives while preserving inspectable
  manifests.

## Not Worth Doing Yet

- Remote/cloud sync.
- Automatic note merging.
- Automatic replacement of non-empty metadata fields.
- Publisher metadata lookup.
- LLM-based conflict resolution.

