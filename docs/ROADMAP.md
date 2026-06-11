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

## v0.6 Completed

- Literature-review authoring workbench for local planning aids.
- Evidence matrix reports with optional CSV and JSON exports.
- Claim banks that separate strong, weak, missing-evidence, review-statement, and not-ready claims.
- Citation banks that group papers by background, method, primary evidence, mechanism, limitation, review context, comparison, and not-yet-usable roles.
- Paragraph plans that propose evidence-aware paragraph purposes without drafting prose.
- Subsection readiness reports with a transparent local completeness score.
- Writing packets that combine authoring artifacts for one theme.

## v0.7 Completed

- Local file scanner for user-provided PDFs, text sidecars, notes, BibTeX, RIS, and CSV files.
- Local file registry CSV with paper IDs, relative paths, file types, sizes, SHA256 hashes, and advisory metadata status.
- Non-destructive file linking and unlinking commands.
- Duplicate-file, missing-file, unsupported-file, and sidecar diagnostics.
- Local-file audit reports.
- Clear PDF metadata boundary: no scraping, no OCR, no full-text parsing, and no authoritative metadata replacement.

## v0.8 Completed

- Package metadata hardening for an external-user-quality local release.
- Installation, contribution, changelog, and docs-site source pages.
- Release scripts for CLI smoke workflows, notebook checking, and tracked-file data-safety auditing.
- Test, CLI behavior, report, and data-safety matrices.
- v0.8 release notes, release-readiness, external-user simulation, and v0.9 patch-plan reports.
- CI release gates for tests, package import, CLI smoke paths, notebook checks, and data-safety checks.

## v0.9 Completed

- Workspace integrity checks for project profiles and the legacy `data/` workflow.
- Local audit logs under `.paperwb/`.
- Local backup snapshots with manifests and PDF/cache exclusions.
- Non-destructive restore planning with pre-restore backup support.
- Non-destructive legacy `data/` to project-profile migration plans.
- Safe-write documentation and workflow examples.

## v0.10 Completed

- Adversarial synthetic fixture library for malformed local data.
- Central error taxonomy and error-message guidance.
- CLI failure-path regression tests.
- Parser/import/backup hardening for recoverable bad inputs.
- Warning snapshot-style assertions for representative diagnostics.

## v1.0-rc Completed

- API and CLI surface inventories.
- Command-contract documentation and tests.
- Current-environment release check and documented fresh-venv install workflow.
- External-user simulation and data-safety reports.
- Final release-readiness and known-limitations reports.

## Near-Term Patches for v1.0.0

- Add report diff tooling that explains golden snapshot changes.
- Add optional fixture-size profiles such as small, medium, and large.
- Add more robust BibTeX string and macro handling.
- Add optional HTML export for Markdown reports.
- Add safer citation-key suggestions such as `FirstAuthorYearShortTitle`.
- Add richer report filters for specific tags, statuses, and themes.
- Add note repair diagnostics for malformed claim blocks.
- Add checksum verification after forced restores.
- Add optional compressed backup archives while keeping manifests inspectable.
- Add project-to-project migration plans for profile restructuring.
- Add import preview tables and conflict-resolution commands for ambiguous matches.
- Add writer-facing filters for authoring reports, such as minimum claim strength and evidence type.
- Add optional advisory PDF metadata extraction if a lightweight dependency is justified.

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
