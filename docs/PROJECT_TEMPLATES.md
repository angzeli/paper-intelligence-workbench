# Project Templates

`paperwb template` creates reusable local project scaffolds for real
literature-review work. Templates contain empty registries, domain themes,
rule examples, checklist files, and dashboard expectations. They do not include
real paper metadata, PDFs, claims, quotes, or summaries.

## Commands

```bash
paperwb template list
paperwb template inspect photocatalysis
paperwb template create photocatalysis --project my_project
paperwb template create finance --project my_finance_reading
paperwb template create ml-methods --project my_ml_methods
paperwb template create generic --project my_lit_review
```

Creation is non-destructive. If the target project path already exists, the
command fails instead of reusing or overwriting it.

## Generated Files

- `registry.csv`: standard registry headers with no fabricated papers.
- `themes.json`: domain theme definitions.
- `rules.json`: safe declarative rule examples.
- `templates/NOTE_TEMPLATE.md`: structured note scaffold kept outside the
  parsed `notes/` directory until copied for a specific paper.
- `registry_schema.md`: local schema reminder.
- `report_checklist.md`: first reports to run.
- `manuscript_qa_checklist.md`: audit checklist before drafting.
- `dashboard_expectations.md`: how to interpret dashboard next actions.
- `reading_queue_config.json`: transparent local ranking notes.

## First Commands After Creation

```bash
paperwb doctor --project my_project
paperwb dashboard --project my_project --no-audit-log
paperwb rules validate-config --project my_project
paperwb report evidence-map --project my_project --out scratch/my_project_evidence_map.md --force
```

The templates are starting points. Replace placeholder structure with
user-verified metadata and user-written notes only.
