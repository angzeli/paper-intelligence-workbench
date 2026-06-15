# v2.0 Dogfood Demo Results

This demo shows a realistic first pass over an FYP-style photocatalysis
literature-review workspace. It uses user-provided BibTeX metadata and PDF
filenames, but it does not include PDFs, paper full text, quotes, claims, or
fabricated scientific summaries.

## What Is Ready

- `projects/fyp_zis_lit_review/registry.csv` contains 15 starter papers.
- `projects/fyp_zis_lit_review/bibtex/library.bib` contains the matching 15
  BibTeX entries.
- `projects/fyp_zis_lit_review/notes/` contains one blank structured note
  template per starter paper.
- `projects/fyp_zis_lit_review/themes.json` contains the FYP photocatalysis
  theme pack.
- `projects/fyp_zis_lit_review/reports/` contains generated onboarding,
  inventory, validation, dashboard, search, authoring-readiness, file-audit,
  and evidence-gap reports.
- `projects/fyp_zis_lit_review/obsidian_vault/` contains an
  Obsidian-friendly Markdown export of the starter workspace.

## Best Reports To Open First

1. `reports/dashboard.md`
2. `reports/reading_queue.md`
3. `reports/fyp_15_paper_plan.md`
4. `reports/inventory.md`
5. `reports/bibtex_audit.md`
6. `reports/citation_audit.md`
7. `reports/evidence_map.md`
8. `reports/search_metal_sulfide_indexed.md`
9. `reports/writing_packet_metal_sulfide.md`
10. `reports/subsection_readiness_metal_sulfide.md`
11. `reports/report_index.md`

## What The Results Mean

The demo is intentionally a starter workspace, not a finished review. The
registry and BibTeX are populated, but claims and evidence maps remain empty
until a human reads papers and fills the structured notes.

The queue, dashboard, search reports, and authoring-readiness reports are useful
because the registry now includes metadata-derived demo triage tags and
priorities. These tags are workflow labels based on title/key patterns only;
they should be verified before real writing.

## Commands Used For The Final Demo Pass

```bash
paperwb validate-registry projects/fyp_zis_lit_review/registry.csv --strict
paperwb validate-bib projects/fyp_zis_lit_review/bibtex/library.bib --registry projects/fyp_zis_lit_review/registry.csv --strict
paperwb report all --project fyp_zis_lit_review --force
paperwb reading queue --project fyp_zis_lit_review --limit 15 --out projects/fyp_zis_lit_review/reports/reading_queue.md --force
paperwb dashboard --project fyp_zis_lit_review --no-audit-log --out projects/fyp_zis_lit_review/reports/dashboard.md --force
paperwb index rebuild --project fyp_zis_lit_review
paperwb index status --project fyp_zis_lit_review --out projects/fyp_zis_lit_review/reports/index_status.md --force
paperwb search "metal sulfide" --project fyp_zis_lit_review --indexed --out projects/fyp_zis_lit_review/reports/search_metal_sulfide_indexed.md --force
paperwb report subsection-readiness --project fyp_zis_lit_review --theme metal-sulfide-photocatalysts --out projects/fyp_zis_lit_review/reports/subsection_readiness_metal_sulfide.md --force
paperwb writing-packet --project fyp_zis_lit_review --theme metal-sulfide-photocatalysts --out projects/fyp_zis_lit_review/reports/writing_packet_metal_sulfide.md --force
paperwb files audit --project fyp_zis_lit_review --reports-dir projects/fyp_zis_lit_review/reports/file_audit --force
paperwb export obsidian --project fyp_zis_lit_review --out projects/fyp_zis_lit_review/obsidian_vault
paperwb export project-summary --project fyp_zis_lit_review --out projects/fyp_zis_lit_review/reports/project_summary.md --force
paperwb export report-index --project fyp_zis_lit_review --out projects/fyp_zis_lit_review/reports/report_index.md --force
```

## Next Real Use Step

Start with the top paper in `reports/reading_queue.md`, read it manually, fill
the matching note template, and rerun claims, evidence map, citation audit, and
dashboard reports. The tool should make evidence gaps obvious; it should not
fill them automatically.
