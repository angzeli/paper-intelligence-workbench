# Release Readiness Report v0.2

Date: 2026-06-09

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

## Tests Run

- `pytest`
- Result: `31 passed`

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

The legacy `data/` workflow still works. Existing commands remain available, and old registry CSVs remain readable because new v0.2 fields default to blank values when missing. Project profiles are opt-in through `--project`.

## Known Limitations

- BibTeX parsing remains lightweight and does not interpret every macro or LaTeX construct.
- Note parsing is still template-oriented and conservative.
- Search is still local substring matching, not semantic search.
- Project profiles are folder-based only; there is no migration command yet.
- Evidence maps and outlines organize user-tracked evidence but do not judge scientific truth.

## Risks

- Users with highly customized BibTeX libraries may need parser-specific fixes.
- Large projects may need indexing or optional SQLite in a future release.
- Generated diagnostics can be noisy when synthetic fixtures intentionally include validation problems.
- Profile paths are intentionally local and should not be treated as cloud-sync state.

## Suggested v0.3 Roadmap

- Add non-destructive migration reports from legacy `data/` workspaces to profile workspaces.
- Add citation-key suggestions without automatic mutation.
- Add local HTML export for generated Markdown reports.
- Add richer note-format diagnostics with precise malformed field locations.
- Add optional fielded search and SQLite FTS for larger projects.

## Usability Assessment

The repository is usable for a real small literature-review project if the user supplies verified metadata, notes, BibTeX entries, claims, and evidence locations. It remains local-first and does not fabricate research content.
