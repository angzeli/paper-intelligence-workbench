# Backward Compatibility Policy

The workbench should preserve local user data before preserving internal
implementation convenience.

## Guarantees

- Historical workspace inspection is read-only.
- Legacy migration copies files and does not delete source files.
- Forced migration should be preceded by inspection and dry-run.
- Existing project targets are conflicts, not overwrite targets.
- Extra registry columns must be preserved by migration.
- Project paths that escape a project root must be rejected or reported.

## Non-Guarantees

- Experimental sidecar schemas are not frozen.
- Generated report layouts may evolve.
- Unknown registry columns are not interpreted by core commands.
- Broken notes are not repaired automatically.

