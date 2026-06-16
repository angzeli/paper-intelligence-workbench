# Sync Plans

A sync plan is a local JSON file plus a Markdown report. It is a dry-run record
of proposed changes and conflicts.

If `paperwb sync plan` receives `--out scratch/sync_plan.md` without
`--json-out`, it writes `scratch/sync_plan.json` beside the Markdown report. If
neither output path is supplied, both files default to the selected reports
directory.

## Plan Contents

Each action includes:

- action ID
- action type
- source and target
- paper ID
- field, when applicable
- old value and new value
- risk level
- whether force is required
- reason

Each conflict includes:

- conflict ID
- conflict type
- paper ID
- field
- registry value
- source value
- risk level
- suggested action

## Safe Apply Boundary

v1.3 applies only safe registry actions:

- create missing paper rows
- fill blank registry fields

It does not overwrite non-empty registry fields, delete rows, delete notes,
rewrite Markdown notes, or merge Obsidian edits.
