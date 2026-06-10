# Release Readiness v0.4

Date: 2026-06-10

## Summary

v0.4 adds local import/export interoperability while preserving the project boundary: no cloud APIs, no LLM APIs, no publisher scraping, and no copyrighted PDFs.

## Implemented Importers

- Zotero-style CSV import.
- Generic CSV import with transparent JSON column mapping.
- BibTeX-to-registry import using the existing conservative BibTeX parser.
- RIS import with a lightweight conservative parser for common RIS tags.

All importers generate Markdown import reports and preserve existing registry rows. Matched records are skipped by default. `--fill-missing` fills only blank fields and does not overwrite non-empty user fields.

## Implemented Exporters

- Obsidian-friendly Markdown vault export.
- Backup bundle export with `manifest.json`.
- Project summary export.
- Report index export.
- Richer reading-list exports by status, tag, theme, high priority, missing notes, included papers, and excluded papers.
- Reading-list CSV output.

Backup bundles do not include PDFs by default.

## CLI Commands Checked

- `paperwb --help`
- `paperwb import zotero-csv ... --dry-run`
- `paperwb import csv ... --mapping ... --dry-run`
- `paperwb import bibtex ... --dry-run`
- `paperwb import ris ... --dry-run`
- `paperwb export obsidian ...`
- `paperwb export bundle ...`
- `paperwb export reading-list ...`
- `paperwb export project-summary ...`
- `paperwb export report-index ...`

## Generated Reports

- `reports/import_zotero_csv_v0_4.md`
- `reports/import_generic_csv_v0_4.md`
- `reports/import_bibtex_v0_4.md`
- `reports/import_ris_v0_4.md`
- `reports/obsidian_export_summary_v0_4.md`
- `reports/bundle_export_summary_v0_4.md`
- `reports/reading_list_photocorrosion_v0_4.md`
- `reports/project_summary_v0_4.md`
- `reports/report_index_v0_4.md`
- `reports/release_readiness_v0_4.md`
- `reports/v0_5_recommended_patch_plan.md`

## Tests Run

- `python -m pytest -q`: 69 passed.
- `python scripts/validate_notebooks.py`: validated 5 notebooks.

## Backward Compatibility

- Existing v0.1-v0.3 commands remain available.
- Existing export command names keep their previous defaults.
- The new `import` command is additive.
- Existing project profile and legacy `data/` workflows remain supported.

## Data Safety Assessment

- Imports do not overwrite non-empty registry fields.
- Duplicate DOI, title, or BibTeX-key matches are skipped by default.
- Dry-run mode is available for every importer.
- Backup bundles omit PDFs unless `--include-pdfs` is explicitly provided.
- Import mappings are explicit JSON files for generic CSV.

## Known Limitations

- RIS parsing is intentionally limited to common tags.
- Import conflict resolution is report-based; there is no interactive resolver.
- BibTeX import relies on the lightweight parser and does not handle every BibTeX dialect.
- Obsidian export writes plain Markdown links and does not require or configure Obsidian plugins.

## v0.5 Recommended Scope

Focus v0.5 on import conflict previews, report diff tooling, richer import summaries, optional HTML report export, safer citation-key suggestions, and note repair diagnostics.

## Usability Assessment

v0.4 is usable for local-first exchange with common academic workflows when users inspect dry-run reports before importing real bibliographic data.
