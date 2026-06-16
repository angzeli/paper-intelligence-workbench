# Release Notes v3.0rc

Release label: v3.0rc  
Package metadata: 3.0.0rc1

## Summary

v3.0rc is a stabilization release candidate for local dogfooding. It does not
add a broad new product surface. It classifies what is stable, what remains
experimental, which schemas are frozen, and how an external user should start a
real local literature-review project safely.

## Capability Groups

- Project profiles and templates: stable for empty/synthetic scaffolds and
  non-destructive project setup.
- Registry and BibTeX validation: stable for local CSV/BibTeX checks and strict
  CI-style validation.
- Structured notes and claims: stable for user-written notes and claim
  extraction from structured Markdown.
- Themes and evidence maps: stable core reports for evidence completeness and
  theme coverage.
- Manuscript and draft QA: experimental heuristic audit reports only.
- Authoring and writing packets: experimental planning aids, not final prose.
- Reading sessions: experimental local logs, queues, and follow-ups.
- Imports and exports: core exports are usable; risky imports remain
  dry-run/review-first.
- Sync and conflict planning: experimental and non-destructive by default.
- Local search and indexing: substring search is stable; SQLite indexed search
  remains rebuildable cache state.
- Local files and sidecars: experimental local-file audit layer; no copying or
  deletion by default.
- Backup, migration, integrity, and audit logs: read-only checks are preferred;
  forced restore/migration remains safety-sensitive.
- Rule engine: experimental declarative JSON checks, no executable plugins.
- Dashboard: stable read-only terminal/Markdown project summary.
- Evidence graph: experimental derived graph summaries and JSON/DOT exports.
- Claim lifecycle: experimental review sidecars for explicit claim status.
- Workflow runner: experimental declarative recipes with no shell/Python
  execution.
- Review packets: experimental local file-based collaboration exports and
  comment imports.
- Performance and incremental rebuilds: experimental cache metadata and scale
  sanity checks.
- Architecture stabilization: v2.6 helper consolidation is preserved; v3.0rc
  freezes behavior rather than refactoring further.

## Safety Boundary

v3.0rc remains local-first. It uses no cloud APIs, no LLM APIs, no publisher
scraping, no automatic PDF downloads, and no copyrighted full-text examples. It
does not fabricate metadata, citations, claims, quotes, summaries, conclusions,
or final literature-review prose.
