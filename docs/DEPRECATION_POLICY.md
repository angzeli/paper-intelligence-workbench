# Deprecation Policy

Paper Intelligence Workbench v2.0rc has no deprecated CLI command groups.

## Policy

- Stable commands should receive at least one documented release cycle before
  removal or incompatible behavior changes.
- Experimental commands may change with release notes and tests.
- Generated report formats are not API contracts unless explicitly listed in
  `docs/STABLE_SURFACE_V2.md`.
- Cache, index, audit-log, backup, and migration-plan internals may change as
  long as dry-run and non-destructive behavior is preserved.
- Legacy `data/` workflows are supported in v2.0rc. If they are ever deprecated,
  migration planning must remain copy-only and non-destructive.

## What Counts As Breaking

- Removing a stable CLI command.
- Changing a stable command to overwrite files by default.
- Dropping stable registry or note fields without migration guidance.
- Changing dry-run behavior into write behavior.
- Treating heuristic evidence matching as truth evaluation.

