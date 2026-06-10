# Import Report: bibtex

- Source file: data/examples/library_import.bib
- Project: ml_methods
- Dry run: true
- Rows read: 3
- Records imported: 2
- Records updated: 0
- Records skipped: 1
- Output registry path: /Users/liangze/Desktop/paper-intelligence-workbench/projects/ml_methods/registry.csv

## Imported Paper IDs

- synthetic_2026_synthetic_bibtex_imported
- local_2025_synthetic_bibtex_imported

## Updated Paper IDs

- None.

## Skipped Records

- SyntheticImportDuplicate

## Unmapped Fields

- None.

## Warnings

| Severity | Code | Source | Identifier | Message | Suggestion |
| --- | --- | --- | --- | --- | --- |
| warning | unsupported_item_type | row 2 | inproceedings | Unsupported item type 'inproceedings'; mapped to other. | Review source_type after import. |
| warning | duplicate_record | row 3 | SyntheticImportDuplicate | SyntheticImportDuplicate matches existing registry row synthetic_2026_synthetic_bibtex_imported; skipped. | Use --fill-missing only when you want blank registry fields completed. |
