# Real Project Onboarding

Use this workflow when moving from synthetic examples to a real local
literature-review project. The workbench helps track verified metadata, notes,
claims, citations, and reports. It does not invent paper records or evidence.

## Create The Scaffold

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
```

The scaffold is intentionally empty. Add papers only after you have verified
the metadata and citation key yourself.

## Intake One Paper

1. Add a row to `projects/fyp_zis_lit_review/registry.csv`.
2. Add the matching BibTeX entry to `projects/fyp_zis_lit_review/bibtex/library.bib`.
3. Run registry and BibTeX validation.
4. Generate a note template.
5. Read the paper and fill the note manually.
6. Extract claims from your note.
7. Regenerate evidence and citation reports.

```bash
paperwb validate-registry projects/fyp_zis_lit_review/registry.csv
paperwb validate-bib projects/fyp_zis_lit_review/bibtex/library.bib --registry projects/fyp_zis_lit_review/registry.csv
paperwb note-template PAPER_ID --project fyp_zis_lit_review
paperwb claims --project fyp_zis_lit_review --output scratch/fyp_claims.csv --force
paperwb report evidence-map --project fyp_zis_lit_review --out projects/fyp_zis_lit_review/reports/evidence_map.md --force
paperwb report citation-audit --project fyp_zis_lit_review --out projects/fyp_zis_lit_review/reports/citation_audit.md --force
```

## Metadata-backed 15-paper Plan

If you already have a private PDF folder and a private BibTeX file, generate a
read-only plan first:

```bash
paperwb dogfood plan-from-files photocatalysis --project fyp_zis_lit_review --references-dir <references_dir> --bibtex <ref.bib> --out scratch/fyp_15_paper_plan.md --force
```

This compares PDF filename slugs with BibTeX keys. It does not copy PDFs, read
PDF text, write registry rows, or verify scientific content.

## Safety Rules

- Do not commit PDFs or copied full-text papers.
- Do not paste copyrighted article text into example fixtures.
- Do not fabricate metadata, claims, quotes, summaries, or citations.
- Use reports as planning aids, not truth evaluation.
- Back up before large manual edits.
