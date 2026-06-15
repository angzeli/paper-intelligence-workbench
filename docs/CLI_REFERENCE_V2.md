# CLI Reference v2

Use `paperwb --help` and `paperwb COMMAND --help` for exact options. This page
classifies command groups for v2.0.

## Stable Core

- `init`
- `project`
- `template`
- `dogfood`
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
- `graph`
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

## Dogfood Commands

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
paperwb dogfood plan-from-files photocatalysis --project fyp_zis_lit_review --references-dir <references_dir> --bibtex <ref.bib> --out scratch/fyp_15_paper_plan.md --force
```

`dogfood create` is non-destructive and refuses an existing project path.
`plan-from-files` is a planning command only: it compares local PDF filenames
with BibTeX keys and does not copy files, read PDF text, or write registry rows.

## Common Flags

- `--project PROJECT`: use a project profile.
- `--out PATH`: write a report/export.
- `--force`: overwrite an output where the command allows it.
- `--dry-run`: plan without writing for risky workflows.

Stable commands should produce user-facing errors and avoid Python tracebacks
for normal bad input.

## Evidence Graph Commands

```bash
paperwb graph build --project zis_photocatalysis
paperwb graph summary --project zis_photocatalysis --out scratch/evidence_graph_summary.md --force
paperwb graph export --project zis_photocatalysis --format json --out scratch/evidence_graph.json --force
paperwb graph export --project zis_photocatalysis --format dot --out scratch/evidence_graph.dot --force
```

The graph commands are experimental in v2.1. They are read-only unless `--out`
is supplied, and they derive nodes and edges only from local workbench data.
