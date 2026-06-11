# Safe Sync Workflow

Use sync in this order:

1. Export or prepare a local source file.
2. Generate a sync plan.
3. Read the Markdown plan.
4. Inspect conflicts.
5. Apply only if the plan contains safe changes.
6. Regenerate registry, BibTeX, evidence, and citation reports.

Example:

```bash
paperwb sync plan --project zis_photocatalysis \
  --source data/examples/zotero_export.csv \
  --source-type zotero-csv \
  --out scratch/sync_plan.md \
  --json-out scratch/sync_plan.json \
  --force

paperwb sync conflicts scratch/sync_plan.json --out scratch/sync_conflicts.md --force
paperwb sync apply scratch/sync_plan.json --dry-run --out scratch/sync_apply_dry_run.md --force-report
```

Use `--force` only after reviewing the plan. Forced sync applies create a local
backup by default. Use `--no-backup` only for disposable test workspaces.

Never use sync to overwrite notes or registry fields that contain user-entered
data. Resolve those conflicts manually.

Real applies are refused when a plan contains high-risk identity conflicts or
when the source/registry files changed after plan generation. Regenerate the
plan after manual edits so the dry-run report reflects the current workspace.
