# Restore Workflow

Restore is deliberately non-destructive by default.

```bash
paperwb backup plan-restore BACKUP_ID --project zis_photocatalysis
paperwb backup restore BACKUP_ID --project zis_photocatalysis --dry-run
```

To actually restore files:

```bash
paperwb backup restore BACKUP_ID --project zis_photocatalysis --force
```

When `--force` is used, the command creates a pre-restore backup first unless `--no-pre-restore-backup` is provided.

Restore never deletes unrelated files. It copies files from the backup back to their original workspace-relative paths and reports files that will be overwritten.

## Reports

Use `--out` to write a restore plan/report:

```bash
paperwb backup restore BACKUP_ID --project zis_photocatalysis --dry-run --out reports/restore_dry_run_v0_9.md --force-report
```

Review overwrite counts before using `--force`.
