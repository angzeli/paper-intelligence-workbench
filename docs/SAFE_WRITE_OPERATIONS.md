# Safe Write Operations

v0.9 hardens write-heavy workflows around explicit force flags, dry-run plans, backup snapshots, and audit events.

## Defaults

- Note templates do not overwrite without `--force`.
- Reports and exports refuse existing output paths unless `--force` is passed.
- Imports support `--dry-run`.
- Backup restore defaults to dry-run unless `--force` is passed.
- Migration defaults to dry-run unless `--force` is passed.
- Audit-log clear requires `--force`.

## Recommended Release Check

```bash
paperwb integrity check --project zis_photocatalysis
paperwb backup create --project zis_photocatalysis
paperwb backup plan-restore BACKUP_ID --project zis_photocatalysis
paperwb migrate plan --from legacy --to-project migrated_lit_review
```

## Boundaries

The tool preserves user notes and raw files. It does not delete user files, rewrite metadata silently, download PDFs, scrape publishers, or use cloud/LLM APIs.
