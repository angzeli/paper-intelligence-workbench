# Imports

v0.4 adds local import workflows for existing bibliography lists. Imports never call cloud APIs, scrape websites, or fabricate metadata.

## Supported Sources

- Zotero-style CSV: `paperwb import zotero-csv`
- Generic CSV with JSON mapping: `paperwb import csv`
- BibTeX: `paperwb import bibtex`
- RIS: `paperwb import ris`

Each importer writes a Markdown import report with rows read, records imported, records skipped, duplicates, warnings, unmapped fields, dry-run status, and the output registry path.

## Safety Rules

- Existing registry rows are preserved.
- Duplicate matches by DOI, normalized title, or BibTeX key are skipped by default.
- `--fill-missing` fills only blank fields on matched registry rows.
- Non-empty user fields are not overwritten.
- `--dry-run` reports what would happen without writing the registry.
- Import reports are not overwritten unless `--force` is passed.

## Examples

```bash
paperwb import zotero-csv data/examples/zotero_export.csv --project zis_photocatalysis --dry-run --force
paperwb import csv data/examples/generic_papers.csv --mapping data/examples/generic_mapping.json --dry-run --force
paperwb import bibtex data/examples/library_import.bib --dry-run --force
paperwb import ris data/examples/library.ris --dry-run --force
```

Use a temporary project or `--dry-run` before importing real files.
