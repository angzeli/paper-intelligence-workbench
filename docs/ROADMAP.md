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

## v1.1 Completed

- Markdown draft citation parsing and citation coverage audits.
- Paragraph-level heuristic evidence matching against local notes and claims.
- Draft revision checklists and paragraph evidence matrices.
- Synthetic draft corpus and draft-audit workflow documentation.

## v1.2 Completed

- Local reading queue generation using transparent registry/note/theme gaps.
- Reading session start/finish/status commands with ignored JSONL session logs.
- Safe note-template integration that preserves existing notes unless `--force-note` is explicit.
- Follow-up action listing, Markdown export, and completion state outside source notes.
- Weekly reading review reports summarizing sessions, claims added, weak themes, follow-ups, and next reading candidates.

## v1.3 Completed

- Local sync plans for Zotero-style CSV, generic CSV mappings, BibTeX, and RIS.
- JSON sync plans and Markdown sync/conflict/apply reports.
- Safe registry apply for creates and blank-field fills only.
- Backup-before-force behavior for sync apply.
- Conservative note and Obsidian round-trip conflict detection.

## v1.4 Completed

- Manuscript citation QA for Markdown and LaTeX-ish drafts.
- Citation context tables for every citation occurrence.
- Claim-to-draft traceability reports by theme.
- Manuscript revision checklists and paragraph evidence tables.
- Synthetic manuscript drafts covering unknown citations, overconfident wording, review-only support, and citation mismatch cases.

## Near-Term Patches for v1.5

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
- Add richer interactive conflict-resolution commands for ambiguous sync matches.
- Add writer-facing filters for authoring reports, such as minimum claim strength and evidence type.
- Add optional advisory PDF metadata extraction if a lightweight dependency is justified.
- Add reading-session conflict handling for interrupted/duplicate active sessions.
- Add optional calendar-style session summaries while keeping all state local.

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

## v1.4 Candidate Scope

- Harden manuscript QA against more real-world footnotes, captions, and appendices.
- Add report diffs for manuscript QA, draft audits, and weekly reading reviews.
- Improve citation-pattern fixtures without becoming a full citation processor.
- Add opt-in sync field patch files for manually approved non-empty metadata changes.
- Add richer follow-up filters by status, age, and linked theme.
