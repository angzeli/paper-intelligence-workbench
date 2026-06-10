# Release Readiness Report v0.2

Date: 2026-06-10

## Implemented Features

- Added multi-project profiles under `projects/` with `paperwb project init`, `paperwb project list`, and `paperwb project validate`.
- Added project-aware path resolution for `list`, `add-paper`, `note-template`, `claims`, `search`, `report`, `checklist`, `doctor`, and `export`.
- Expanded registry schema with project, source type, relevance score, reading priority, inclusion status, and exclusion reason.
- Expanded registry validation for malformed DOI-like strings, invalid priorities, invalid source types, missing notes paths, included papers without claims, excluded papers without reasons, and missing local PDF paths.
- Improved BibTeX validation with entry-type-specific required fields and parse-warning reporting.
- Improved note parsing with personal reading notes, varied claim headings, safer claim-block boundaries, and warning-based behavior.
- Added workspace health diagnostics through `paperwb doctor` and `paperwb report workspace-health`.
- Upgraded evidence-map reporting with strength counts, missing-evidence counts, review-statement counts, primary/contextual evidence counts, missing notes, and follow-up actions.
- Added `paperwb report section-outline` for evidence-based literature-review subsection outlines.
- Added exports for registry CSV/JSON, claims CSV/JSON, reading lists, unread lists, and theme claims.
- Added synthetic project profiles for `zis_photocatalysis`, `finance_reading`, and `ml_methods`.
- Added an end-to-end synthetic workflow script at `examples/end_to_end_workflow.py`.
- Hardened release-blocking CLI trust boundaries after hostile review:
  - common input failures now return concise `error:` messages instead of tracebacks
  - read/report commands no longer create missing registries
  - reports and exports refuse existing output files unless `--force` is provided
  - project path override flags are rejected when `--project` is used
  - unknown section-outline themes return a non-zero CLI error without writing a report
  - `theme-claims` exports use portable relative note paths
  - evidence maps show undefined theme buckets instead of dropping typoed theme claims
  - the lightweight BibTeX parser ignores `@comment`/`@preamble`, resolves simple `@string` macros, and keeps simple concatenated values

## Files Changed

- Core package modules under `paper_workbench/`
- Synthetic data under `data/`
- New project fixtures under `projects/`
- Expanded test suite under `tests/`
- Updated documentation under `README.md`, `AGENTS.md`, and `docs/`
- Generated v0.2 reports under `reports/`

## CLI Commands Checked

- `paperwb --help`
- `paperwb project list`
- `paperwb project validate zis_photocatalysis`
- `paperwb validate-registry data/registries/example_papers.csv`
- `paperwb validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv`
- `paperwb claims data/notes --output data/processed/example_claims_v0_2.csv`
- `paperwb search photocorrosion --project zis_photocatalysis`
- `paperwb report evidence-map`
- `paperwb report citation-audit`
- `paperwb report section-outline --theme photocorrosion`
- `paperwb doctor`
- `paperwb export registry-json`
- `paperwb export claims`
- Negative smoke paths for missing files, duplicate projects, invalid enum values, overwrite refusal, project path conflicts, and unknown section-outline themes

## Tests Run

- `pytest`
- Result: `41 passed`

## Reports Generated

- `reports/inventory_v0_2.md`
- `reports/reading_status_v0_2.md`
- `reports/bibtex_audit_v0_2.md`
- `reports/citation_audit_v0_2.md`
- `reports/evidence_map_v0_2.md`
- `reports/theme_dashboard.md`
- `reports/weak_claims_v0_2.md`
- `reports/missing_evidence.md`
- `reports/photocorrosion_section_outline.md`
- `reports/workspace_health.md`
- canonical root reports without `_v0_2` suffix refreshed to match current v0.2 output
- project-specific reports under each synthetic project profile

## Documentation Updated

- `README.md`
- `AGENTS.md`
- `docs/REGISTRY_SCHEMA.md`
- `docs/NOTE_FORMAT.md`
- `docs/BIBTEX_AUDIT.md`
- `docs/CITATION_AUDIT.md`
- `docs/EVIDENCE_MAPS.md`
- `docs/PROJECT_PROFILES.md`
- `docs/CLI_REFERENCE.md`
- `docs/WORKFLOW_EXAMPLES.md`
- `docs/ROADMAP.md`

## Backward Compatibility

The legacy `data/` workflow still works. Existing commands remain available, and old registry CSVs remain readable because new v0.2 fields default to blank values when missing. Project profiles are opt-in through `--project`. Generated report and export commands now require `--force` before overwriting existing files; this is an intentional safety hardening.

## Known Limitations

- BibTeX parsing remains lightweight and does not interpret every LaTeX construct.
- Note parsing is still template-oriented and conservative; additional field-label aliases remain future work.
- Search is still local substring matching, not semantic search.
- Project profiles are folder-based only; there is no migration command yet.
- Evidence maps and outlines organize user-tracked evidence but do not judge scientific truth.

## Risks

- Users with highly customized BibTeX libraries may still need parser-specific fixes.
- Large projects may need indexing or optional SQLite in a future release.
- Generated diagnostics can be noisy when synthetic fixtures intentionally include validation problems.
- Profile paths are intentionally local and should not be treated as cloud-sync state.

## Suggested v0.3 Roadmap

- Add non-destructive migration reports from legacy `data/` workspaces to profile workspaces.
- Add citation-key suggestions without automatic mutation.
- Add local HTML export for generated Markdown reports.
- Add richer note-format diagnostics with precise malformed field locations.
- Add optional fielded search and SQLite FTS for larger projects.

## Deferred Hostile-Review Items

- More flexible note field aliases such as `Evidence location`.
- A clean green-path starter dataset separate from intentionally broken audit fixtures.
- Less noisy workspace-health summaries for onboarding.
- Explicit public Python API boundaries.

## Usability Assessment

The repository is usable for a real small literature-review project if the user supplies verified metadata, notes, BibTeX entries, claims, and evidence locations. The release-blocking hostile-review issues have been addressed, and the tool remains local-first and does not fabricate research content.
