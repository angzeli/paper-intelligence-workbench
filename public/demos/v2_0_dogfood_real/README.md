# Paper Intelligence Workbench v2.0 Dogfood Demo

This folder is a public, metadata-backed dogfood demo for an FYP-style
photocatalysis literature-review workspace.

It demonstrates how Paper Intelligence Workbench moves from a real local
reference folder and BibTeX file into a safe starter workspace:

- 15 registry rows selected from filename/BibTeX-key matches
- 15 BibTeX entries copied from user-provided metadata
- FYP photocatalysis themes and local rule examples
- metadata-derived demo triage tags and reading priorities
- blank structured note templates for every starter paper
- inventory, BibTeX audit, citation audit, evidence map, dashboard, reading
  queue, search, authoring-readiness, Obsidian export, and onboarding reports

## Safety Boundaries

- No PDFs are included.
- No PDF text or copied paper full text is included.
- No claims, quotes, summaries, or conclusions are fabricated.
- The included metadata comes from a user-provided local BibTeX file.
- Blank notes are templates only; they must be filled manually while reading.

## Start Here

Open the project:

```bash
cd public/demos/v2_0_dogfood_real
paperwb dogfood status --project fyp_zis_lit_review
paperwb dashboard --project fyp_zis_lit_review --no-audit-log
```

Useful files:

- `projects/fyp_zis_lit_review/registry.csv`
- `projects/fyp_zis_lit_review/bibtex/library.bib`
- `projects/fyp_zis_lit_review/notes/`
- `projects/fyp_zis_lit_review/reports/fyp_15_paper_plan.md`
- `projects/fyp_zis_lit_review/reports/dashboard.md`
- `projects/fyp_zis_lit_review/reports/reading_queue.md`
- `projects/fyp_zis_lit_review/reports/citation_audit.md`
- `projects/fyp_zis_lit_review/reports/evidence_map.md`
- `projects/fyp_zis_lit_review/reports/writing_packet_metal_sulfide.md`
- `projects/fyp_zis_lit_review/reports/search_metal_sulfide_indexed.md`
- `projects/fyp_zis_lit_review/obsidian_vault/`

## Next Real Dogfood Step

Pick the first paper from the reading queue, read it manually, fill its note
template with user-verified observations and claims, then rerun:

```bash
paperwb claims --project fyp_zis_lit_review --output projects/fyp_zis_lit_review/reports/claims.csv --force
paperwb report evidence-map --project fyp_zis_lit_review --out projects/fyp_zis_lit_review/reports/evidence_map.md --force
paperwb report citation-audit --project fyp_zis_lit_review --out projects/fyp_zis_lit_review/reports/citation_audit.md --force
```
