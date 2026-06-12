# Release Notes v2.0rc

Version: `2.0.0rc1`

## Purpose

v2.0rc is a stabilization release candidate. It does not introduce broad new
features. It classifies supported surfaces, refreshes release documentation,
and verifies that the project is safe for local dogfooding.

## Capability Summary

### Registry And BibTeX

- CSV registry loading, saving, filtering, and validation.
- Lightweight BibTeX parsing and validation.
- Duplicate DOI, title, BibTeX key, missing field, and linkage audits.

### Notes And Claims

- Structured Markdown note templates.
- Conservative note parsing.
- Claim extraction from user-entered structured fields.
- Weak, low-confidence, and missing-evidence reports.

### Project Profiles

- Legacy `data/` workflow remains supported.
- Project-profile layout under `projects/<name>/` remains the recommended
  dogfooding path.
- Reusable project templates create empty scaffolds only.

### Reports And Evidence Maps

- Markdown reports for inventory, reading status, BibTeX audit, citation audit,
  evidence maps, theme dashboards, missing notes, weak claims, and workspace
  health.
- Authoring reports remain planning aids, not final prose.

### Authoring And Manuscript QA

- Draft and manuscript audit commands extract citation keys and compare text to
  local notes and claims using transparent heuristics.
- Reports flag unknown citations, weak evidence, review-only support, and
  overconfident wording.

### Imports And Exports

- Local imports from Zotero-style CSV, generic CSV, BibTeX, and RIS.
- Local exports to claims/registry CSV or JSON, reading lists, Obsidian-style
  Markdown vaults, backup bundles, project summaries, and report indexes.

### Reading Sessions

- Reading queues, session start/finish, follow-up actions, and weekly reading
  review reports.

### Sync And Conflict Resolution

- Dry-run sync plans for local import sources and Obsidian-style vaults.
- Safe registry apply remains conservative and conflict-aware.

### Local Search

- Substring search is stable.
- Optional SQLite index is rebuildable and remains an experimental cache.

### Backups, Migration, Integrity

- Workspace integrity checks.
- Local backup snapshots.
- Restore dry-run and forced restore workflow.
- Legacy-to-project migration planning and copy-only migration.

### Templates And Dashboard

- Project templates for photocatalysis, finance/valuation, ML methods, and
  generic literature-review projects.
- Read-only terminal dashboard and next-action summaries.

### Data-Safety Boundaries

- No cloud APIs.
- No LLM APIs.
- No publisher scraping.
- No copyrighted PDFs or copied full text.
- No fabricated real paper metadata, citations, claims, quotes, or summaries.
- No silent overwrite of user data.

