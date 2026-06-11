# Import / Export

Import and export workflows are local-only. They do not call Zotero cloud services, publisher sites, or LLM APIs.

## Imports

```bash
paperwb import zotero-csv data/examples/zotero_export.csv --project zis_photocatalysis --dry-run
paperwb import csv data/examples/generic_papers.csv --mapping data/examples/generic_mapping.json --dry-run
paperwb import bibtex data/examples/library_import.bib --dry-run
paperwb import ris data/examples/library.ris --dry-run
```

Imports preserve existing rows. `--fill-missing` fills blank fields only.

## Exports

```bash
paperwb export claims-json --project zis_photocatalysis --out scratch/claims.json --force
paperwb export obsidian --project zis_photocatalysis --out exports/obsidian_zis
paperwb export bundle --project zis_photocatalysis --out exports/zis_bundle
```

Backup bundles do not include PDFs unless explicitly requested.

Detailed docs:

- [IMPORTS.md](IMPORTS.md)
- [EXPORTS.md](EXPORTS.md)
- [ZOTERO_WORKFLOW.md](ZOTERO_WORKFLOW.md)
- [OBSIDIAN_EXPORT.md](OBSIDIAN_EXPORT.md)
- [BACKUP_BUNDLES.md](BACKUP_BUNDLES.md)
