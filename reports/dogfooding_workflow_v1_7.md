# Dogfooding Workflow v1.7

v1.7 focuses on making Paper Intelligence Workbench easier to use on a first
real local literature-review project.

## Start

```bash
paperwb template list
paperwb template inspect photocatalysis
paperwb template create photocatalysis --project my_review
```

## Add Local Inputs

- Add only user-verified papers to `projects/my_review/registry.csv`.
- Add local BibTeX entries to `projects/my_review/bibtex/library.bib`.
- Use `projects/my_review/templates/NOTE_TEMPLATE.md` or `paperwb note-template`
  for structured notes. Copy the template into `notes/` only for a real paper.
- Record claims only after reading and recording evidence locations.

## Daily Loop

```bash
paperwb doctor --project my_review
paperwb dashboard --project my_review --no-audit-log
paperwb reading queue --project my_review
paperwb rules report --project my_review --out projects/my_review/reports/rules.md --force
paperwb report evidence-map --project my_review --out projects/my_review/reports/evidence_map.md --force
```

## Before Drafting

```bash
paperwb writing-packet --project my_review --theme THEME
paperwb manuscript qa drafts/my_section.md --project my_review --out scratch/my_section_qa.md --force
```

Use the generated outputs as checklists and planning aids. The tool does not
write final literature-review prose, fabricate citations, or decide scientific
truth.
