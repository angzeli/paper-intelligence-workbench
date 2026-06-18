# Private Dogfooding Adapter v3.5

## Purpose

v3.5 adds a local-only external workspace adapter for real private
literature-review projects. It lets a user keep real project data outside this
repository while still using the Paper Intelligence Workbench CLI.

## Commands Added

```bash
paperwb external add NAME <external_workspace> --project PROJECT
paperwb external list
paperwb external validate NAME --strict
paperwb external validate NAME --out scratch/external_validation.md
paperwb external remove NAME
paperwb external run NAME doctor
```

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

## Local-only Config

Registrations are stored in:

```text
.paperwb-local/workspaces.json
```

The file is ignored by Git and treated as a forbidden tracked artifact by the
data-safety audit. It may contain private absolute paths.

## Non-copying Behavior

The adapter stores pointers only. It does not copy PDFs, notes, drafts,
BibTeX, registry rows, or private project reports into this repository.
Workflow outputs are printed to stdout, written to user-specified paths, or
written into the external workspace.

External validation reports and run summaries redact private local paths by
default. `--show-paths` is available only as an explicit local-debugging opt-in
for outputs that will not be committed or shared.

## Validation

External validation checks that the registered path and project profile can be
resolved. It also includes workspace-health findings so incomplete real
projects remain visible. Structural errors block `external run`; ordinary
project-readiness findings do not prevent dashboard, report, or support-bundle
generation.
