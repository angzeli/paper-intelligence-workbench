# Sync

`paperwb sync` compares local sources and writes a reviewable plan before any
registry changes are made. It is designed for local interchange workflows such
as Zotero CSV exports, BibTeX files, generic CSV files, RIS files, and
Obsidian-style Markdown exports.

It does not contact Zotero cloud, scrape publishers, download files, or infer
paper truth.

## Registry Sync Plan

```bash
paperwb sync plan \
  --project zis_photocatalysis \
  --source data/examples/zotero_export.csv \
  --source-type zotero-csv \
  --out scratch/sync_plan.md \
  --json-out scratch/sync_plan.json \
  --force
```

When `--json-out` is omitted, the JSON plan is written beside `--out` if an
explicit Markdown output path is provided. Without `--out`, both files default
to the selected reports directory.

Supported source types:

- `zotero-csv`
- `generic-csv` with `--mapping`
- `bibtex`
- `ris`

The plan can include:

- `create_paper`: imported paper is not in the registry
- `fill_blank_field`: registry field is blank and source has a value
- `skip_unchanged`: source and registry already agree for supported fields
- conflicts for non-empty differences that need manual review

If an imported row has a high-risk identity conflict, such as same DOI with a
different title, the planner suppresses all applyable updates for that row. The
row must be reviewed manually and the plan regenerated.

## Apply

```bash
paperwb sync apply scratch/sync_plan.json --dry-run
paperwb sync apply scratch/sync_plan.json --force
```

`sync apply` defaults to dry-run unless `--force` is supplied. Forced applies
only create missing registry rows and fill blank fields when the plan has no
high-risk conflicts and the source/registry files still match the plan hashes.
They preserve untouched registry fields, do not overwrite non-empty registry
fields, and do not merge note conflicts.

When `--force` is used, the CLI creates a local backup first unless
`--no-backup` is supplied.

## Conflict Reports

```bash
paperwb sync conflicts scratch/sync_plan.json --out scratch/sync_conflicts.md --force
```

Use the conflict report to decide what should be edited manually before
regenerating a plan.
