# Exports

v0.4 expands local export workflows for downstream writing, backup, and interoperability.

## Data Exports

```bash
paperwb export registry-csv --out exports/registry.csv
paperwb export registry-json --out exports/registry.json
paperwb export claims --out exports/claims.csv
paperwb export claims-json --out exports/claims.json
paperwb export theme-claims --theme photocorrosion --out exports/photocorrosion_claims.json
```

## Reading Lists

```bash
paperwb export reading-list --status unread --out reports/unread.md
paperwb export reading-list --tag photocorrosion --out reports/photocorrosion.md
paperwb export reading-list --theme charge-separation --project zis_photocatalysis --out reports/charge_separation.md
paperwb export reading-list --high-priority --out reports/high_priority.md
paperwb export reading-list --missing-notes --out reports/missing_notes_reading_list.md
paperwb export reading-list --included --format csv --out exports/included.csv
paperwb export reading-list --excluded --out reports/excluded.md
```

## Vaults and Bundles

```bash
paperwb export obsidian --project zis_photocatalysis --out exports/obsidian_zis --force
paperwb export bundle --project zis_photocatalysis --out exports/zis_bundle --force
```

Backup bundles do not include PDFs by default. Use `--include-pdfs` only for local files you have the right to copy.

## Report Index and Summary

```bash
paperwb export project-summary --project zis_photocatalysis --out reports/project_summary.md --force
paperwb export report-index --project zis_photocatalysis --out reports/index.md --force
```
