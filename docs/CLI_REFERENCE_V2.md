# CLI Reference v2

Use `paperwb --help` and `paperwb COMMAND --help` for exact options. This page
classifies command groups for v2.0rc.

## Stable Core

- `init`
- `project`
- `template`
- `validate-registry`
- `validate-bib`
- `add-paper`
- `list`
- `note-template`
- `claims`
- `search` without `--indexed`
- `report` core reports
- `doctor`
- `dashboard`

## Experimental But Usable

- `index`
- `files`
- `draft`
- `manuscript`
- `reading`
- `followups`
- `import`
- `export` advanced outputs
- `sync`
- `integrity`
- `audit-log`
- `backup`
- `migrate`
- `rules`
- `writing-packet`
- `synthetic`

## Common Flags

- `--project PROJECT`: use a project profile.
- `--out PATH`: write a report/export.
- `--force`: overwrite an output where the command allows it.
- `--dry-run`: plan without writing for risky workflows.

Stable commands should produce user-facing errors and avoid Python tracebacks
for normal bad input.

