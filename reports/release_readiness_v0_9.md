# Release Readiness v0.9

## Summary

v0.9 adds local data-integrity safeguards for real workspaces:

- workspace integrity checks
- local audit log JSONL files
- backup snapshots with manifests
- restore dry-run and forced restore workflows
- pre-restore backup support
- non-destructive legacy `data/` to project-profile migration planning
- safe-write documentation and a synthetic safety workflow example

The release remains local-first. No cloud APIs, LLM APIs, publisher scraping, copyrighted PDFs, or real paper full text were added.

## Commands Added

- `paperwb integrity check`
- `paperwb audit-log show`
- `paperwb audit-log clear`
- `paperwb backup create`
- `paperwb backup list`
- `paperwb backup inspect`
- `paperwb backup plan-restore`
- `paperwb backup restore`
- `paperwb migrate plan`
- `paperwb migrate run`

## Data-Safety Changes

- `.paperwb/` remains ignored for audit logs and SQLite cache files.
- `backups/` is ignored so local snapshots are not committed accidentally.
- Restore defaults to dry-run unless `--force` is passed.
- Forced restore creates a pre-restore backup unless explicitly disabled.
- Migration copies files into a new project; it does not move or delete legacy `data/` files.
- Existing target projects are treated as conflicts.

## Reports Generated

- `reports/workspace_integrity_v0_9.md`
- `reports/migration_plan_v0_9.md`
- `reports/backup_manifest_demo_v0_9.md`
- `reports/restore_dry_run_v0_9.md`
- `reports/audit_log_demo_v0_9.md`
- `reports/release_readiness_v0_9.md`
- `reports/v0_10_recommended_patch_plan.md`

## Validation

Validation performed for this release:

- package import check
- `paperwb --help`
- `paperwb integrity check`
- `paperwb backup create/list/inspect`
- `paperwb backup restore --dry-run`
- `paperwb migrate plan`
- `paperwb migrate run --dry-run`
- `paperwb audit-log show`
- `examples/workspace_safety_workflow.py`
- v0.9 pytest coverage
- full pytest suite
- notebook JSON validation

## Backward Compatibility

Existing registry, notes, BibTeX, project profile, import/export, search, file-audit, and authoring commands are preserved. New audit-log writes are local ignored side effects under `.paperwb/`.

The legacy `data/` workflow remains supported. Migration is optional and non-destructive.

## Known Limitations

- Restore copies files from backup manifests but does not delete files that were created after the backup.
- Restore checksum verification after copying is not yet a separate report.
- Migration does not rewrite registry paths or note content for project-relative conventions.
- Backup snapshots are plain directories, not compressed archives.
- Audit-log filtering is basic.

## Release Verdict

v0.9 is usable as a local safety layer for small literature-review projects. It should still be treated as alpha software: users should review migration and restore plans before using `--force`.
