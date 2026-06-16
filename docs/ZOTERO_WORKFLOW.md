# Zotero Workflow

Paper Intelligence Workbench does not connect to Zotero or use a cloud API. v0.4 supports local Zotero-style CSV exports.

## Export From Zotero

Export items from Zotero as CSV, then run:

```bash
paperwb import zotero-csv path/to/zotero_export.csv --project my_review --dry-run --report scratch/import_zotero_dry_run.md --force
```

Inspect the generated import report. If the report looks correct, run without `--dry-run`:

```bash
paperwb import zotero-csv path/to/zotero_export.csv --project my_review --force
```

## Field Mapping

Common fields mapped:

- `Title` -> `title`
- `Author` -> `authors`
- `Publication Year` -> `year`
- `Publication Title` -> `journal`
- `DOI` -> `doi`
- `Url` -> `url`
- `Item Type` -> `source_type`
- `Date Added` -> `added_date`
- `Tags` and `Manual Tags` -> `tags`
- `Abstract Note` -> `user_comment`

Unmapped non-empty columns are reported.

## Duplicate Handling

Rows matching existing registry entries by DOI, normalized title, or BibTeX key are skipped by default. Use `--fill-missing` only when you want blank fields completed from the import.
