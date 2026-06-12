# Migration Guide v2

v2.0rc supports both the legacy `data/` workflow and project profiles under
`projects/`. Migration is optional.

## Recommended Migration Path

1. Run `paperwb doctor` or `paperwb integrity check`.
2. Create a backup if using project profiles: `paperwb backup create --project PROJECT`.
3. Plan legacy migration:

```bash
paperwb migrate plan --from legacy --to-project migrated_review --out scratch/migration_plan.md --force
```

4. Run a dry-run:

```bash
paperwb migrate run --from legacy --to-project migrated_review --dry-run --out scratch/migration_dry_run.md --force
```

5. Only copy files after reviewing the plan:

```bash
paperwb migrate run --from legacy --to-project migrated_review --force
```

## Safety Contract

- Migration copies; it does not delete legacy `data/` files.
- Existing target projects are refused unless the command explicitly supports
  the requested safe behavior.
- Restore workflows should be dry-run first.
- Backups exclude cache files, audit logs, reading-session logs, and PDFs by
  default.

## When Not To Migrate

Do not migrate during active note editing. Finish or commit local note changes
first, run diagnostics, and review the migration plan before copying.

