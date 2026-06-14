# Project Templates

`paperwb template` creates reusable local project scaffolds for real
literature-review work. Templates contain empty registries, domain themes,
rule examples, checklist files, and dashboard expectations. They do not include
real paper metadata, PDFs, claims, quotes, or summaries.

For first-project dogfooding, `paperwb dogfood` wraps these template conventions
with extra onboarding files and empty-project-friendly status checks.

## Commands

```bash
paperwb template list
paperwb template inspect photocatalysis
paperwb template create photocatalysis --project my_project
paperwb template create finance --project my_finance_reading
paperwb template create ml-methods --project my_ml_methods
paperwb template create generic --project my_lit_review
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood plan-from-files photocatalysis --project fyp_zis_lit_review --references-dir <references_dir> --bibtex <ref.bib> --out scratch/fyp_15_paper_plan.md --force
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

## Dogfooding Additions

The photocatalysis dogfood scaffold adds:

- `project_onboarding.md`
- `first_week_plan.md`
- `evidence_tracking_checklist.md`
- `drafts/`
- `reading_sessions/`
- an expanded FYP photocatalysis theme pack

`plan-from-files` is read-only. It compares local PDF filename slugs with local
BibTeX keys to help choose an initial 15-paper reading set. It does not copy
PDFs, parse PDF text, or write registry data.
