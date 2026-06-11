# Import Report: zotero-csv

- Source file: data/examples/zotero_export.csv
- Project: zis_photocatalysis
- Dry run: true
- Rows read: 5
- Records imported: 3
- Records updated: 0
- Records skipped: 2
- Output registry path: projects/zis_photocatalysis/registry.csv

## Imported Paper IDs

- synthetic_2026_synthetic_imported_charge
- local_2025_synthetic_imported_photocorrosion
- paper_2024_missing_author_synthetic

## Updated Paper IDs

- None.

## Skipped Records

- Synthetic Imported Charge Transport Note
- row 6

## Unmapped Fields

- Extra Local Column

## Warnings

| Severity | Code | Source | Identifier | Message | Suggestion |
| --- | --- | --- | --- | --- | --- |
| warning | duplicate_record | row 4 | Synthetic Imported Charge Transport Note | Synthetic Imported Charge Transport Note matches existing registry row synthetic_2026_synthetic_imported_charge; skipped. | Use --fill-missing only when you want blank registry fields completed. |
| warning | unsupported_item_type | row 5 | Web Page | Unsupported item type 'Web Page'; mapped to other. | Review source_type after import. |
| warning | missing_author | row 5 | paper_2024_missing_author_synthetic | paper_2024_missing_author_synthetic is missing author. |  |
| error | missing_title | row 6 | person_2023_untitled_import | Imported record is missing title. | Add a title before importing. |
