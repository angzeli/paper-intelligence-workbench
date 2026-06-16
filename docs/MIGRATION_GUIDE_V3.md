# Migration Guide v3

v3 migration remains conservative. The supported migration path copies legacy
`data/` files into a new project profile and leaves the old workspace intact.

## Recommended Sequence

```bash
paperwb compatibility inspect path/to/workspace
paperwb compatibility report path/to/workspace --out scratch/compatibility.md
paperwb migrate run --root path/to/workspace --to-project migrated_review --dry-run --out scratch/migration.md
```

Only after reviewing the compatibility report and dry-run plan should a forced
migration be considered:

```bash
paperwb migrate run --root path/to/workspace --to-project migrated_review --force --out scratch/migration_applied.md
```

Forced legacy migration creates a pre-migration backup when practical. It copies
files; it does not move or delete legacy files.

## What Is Preserved

- Raw registry CSV files, including extra user columns.
- BibTeX files.
- Markdown notes.
- Theme definitions.
- Legacy source files.

## What Requires Manual Review

- Missing registry files.
- Project paths escaping a project root.
- Existing migration target projects.
- Broken structured notes.
- Absolute or `..` local PDF path references.
- Extra registry columns that should not be interpreted by core commands until
  reviewed.

