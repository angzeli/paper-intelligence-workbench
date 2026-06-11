# Workspace Migration

v0.9 supports non-destructive migration planning from the legacy `data/` workflow into a project profile.

```bash
paperwb migrate plan --from legacy --to-project migrated_lit_review
paperwb migrate run --from legacy --to-project migrated_lit_review --dry-run
```

To actually copy files:

```bash
paperwb migrate run --from legacy --to-project migrated_lit_review --force
```

Migration copies files; it does not move or delete legacy data. Existing target projects are treated as conflicts. A pre-migration backup is created before a forced migration.

The migration planner detects:

- legacy registry
- legacy BibTeX files
- legacy notes
- legacy themes
- legacy reports, reported but not copied by default
- target conflicts

The v0.9 migration path is intentionally conservative. It does not rewrite registry paths or update note contents.
