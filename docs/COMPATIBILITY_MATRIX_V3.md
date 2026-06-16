# Compatibility Matrix v3

Use this matrix before touching historical or user-created workspaces.

```bash
paperwb compatibility matrix
paperwb compatibility inspect tests/fixtures/workspaces/v0_1_legacy_data
paperwb compatibility report tests/fixtures/workspaces/v0_1_legacy_data --out scratch/compatibility.md
```

| Source workspace | Supported | Inspectable | Migratable | Requires backup | Manual review |
| --- | --- | --- | --- | --- | --- |
| legacy `data/` workflow | yes | yes | yes, to project profile | yes | if malformed |
| early project profile without `project.json` | yes | yes | not needed | no | if files are missing |
| pre-v2 registry schema | yes | yes | copy-preserved | yes for migration | if extra/missing columns exist |
| v2.0 dogfood workspace | yes | yes | not needed | no | only if user data is incomplete |
| v3.0rc project workspace | yes | yes | not needed | no | only if diagnostics find errors |
| malformed missing registry | partial | yes | no | n/a | yes |
| malformed broken notes | partial | yes | not until repaired | yes if migrating | yes |
| partial migration conflict | partial | yes | blocked until target chosen | yes | yes |
| extra-column registry | yes | yes | copy-preserved | yes for migration | yes |

The source of truth for the generated matrix is `paperwb compatibility matrix`.

## Policy

- Inspect before migration.
- Dry-run before forced migration.
- Preserve extra registry columns by copying raw CSV files where possible.
- Do not rewrite or normalize a user registry just to migrate it.
- Never overwrite an existing project target silently.

