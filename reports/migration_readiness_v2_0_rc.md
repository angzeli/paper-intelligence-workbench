# Migration Readiness v2.0rc

## Scope

This report evaluates whether the legacy `data/` workflow and project-profile
workflow can coexist safely for v2.0rc.

## Expected Behavior

- Legacy `data/` commands remain supported.
- Project-profile commands remain supported.
- Migration planning is non-destructive.
- Migration dry-run is non-destructive.
- Forced migration should copy files rather than delete legacy data.
- Restore defaults to dry-run unless `--force` is used.

## Validation Status

- `paperwb migrate plan --from legacy --to-project <project> --root . --out <tmp> --force`: passed.
- `paperwb migrate run --from legacy --to-project <project> --root . --dry-run --out <tmp> --force-report`: passed.
- `paperwb integrity check --project <synthetic_template_project> --out <tmp> --force`: passed with 0 errors and expected warnings for an empty project scaffold.
- `paperwb backup create --project <synthetic_template_project>`: passed and included registry, BibTeX, themes, and project profile files.
- `paperwb backup list --project <synthetic_template_project>`: passed.
- `paperwb backup inspect <backup_id> --project <synthetic_template_project>`: passed.
- `paperwb backup plan-restore <backup_id> --project <synthetic_template_project> --out <tmp> --force`: passed.
- `paperwb backup restore <backup_id> --project <synthetic_template_project> --dry-run --out <tmp> --force-report`: passed.
- `paperwb audit-log show --project <synthetic_template_project>`: passed when using the installed `paperwb` console entry point.

## Finding

Migration and restore workflows are ready for local dogfooding as non-destructive
planning tools. `restore` still defaults to dry-run unless `--force` is used,
and migration dry-run copies nothing.

## Documentation Note

The v2 getting-started and installation docs now clarify that `python -m
paper_workbench.cli ...` is a repository-root fallback. Users should run
`paperwb` inside initialized workspaces so local data folders do not shadow the
installed package.

## Safety Boundary

Do not run destructive workspace migrations during release validation. Generate
plans and dry-run reports unless a synthetic temporary workspace is used.
