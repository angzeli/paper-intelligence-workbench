# External Workspaces

External workspaces are local workspace roots registered through an ignored
local config file. They let the CLI run against real private projects outside
the repository.

## Commands

```bash
paperwb external add NAME <external_workspace> --project PROJECT
paperwb external list
paperwb external validate NAME
paperwb external validate NAME --out scratch/external_validation.md
paperwb external remove NAME
paperwb external run NAME doctor
```

`<external_workspace>` should be a workspace root containing
`projects/PROJECT/`. The adapter reuses the normal project-profile layout.

## Bounded Run Workflows

`paperwb external run` accepts only known workflow names:

- `doctor`
- `dashboard`
- `validate-registry`
- `validate-bib`
- `claims`
- `evidence-map`
- `citation-audit`
- `support-bundle`
- `backup`

It does not execute arbitrary shell commands or workflow-recipe code.

## Validation Behavior

`external validate` checks whether the registered path and project profile can
be resolved. It also includes workspace-health findings so incomplete real
projects are visible. With `--strict`, only missing external path/project
structure blocks the command; weak evidence or under-supported themes remain
findings for the user to address.

Validation reports and run summaries redact private local paths by default.
Use `--show-paths` only for local debugging when the output will not be
committed or shared.
