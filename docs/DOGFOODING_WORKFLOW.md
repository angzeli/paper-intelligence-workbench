# Dogfooding Workflow

Use templates to start a real local literature-review project without copying
sample papers into the project.

## Start A Project

```bash
paperwb template list
paperwb template inspect photocatalysis
paperwb template create photocatalysis --project my_review
```

## Add Verified Local Inputs

1. Add user-verified rows to `projects/my_review/registry.csv`.
2. Add BibTeX entries to `projects/my_review/bibtex/library.bib`.
3. Generate or copy structured notes into `projects/my_review/notes/`.
4. Add claims only after reading and recording evidence locations.

## Run The Loop

```bash
paperwb doctor --project my_review
paperwb dashboard --project my_review --no-audit-log
paperwb reading queue --project my_review
paperwb rules report --project my_review --out projects/my_review/reports/rules.md --force
paperwb report evidence-map --project my_review --out projects/my_review/reports/evidence_map.md --force
paperwb manuscript qa drafts/my_section.md --project my_review --out scratch/my_section_qa.md --force
```

The dashboard and next actions are suggestions. They do not execute commands or
modify project data automatically.
