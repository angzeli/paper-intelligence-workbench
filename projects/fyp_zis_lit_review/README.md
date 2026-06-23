# fyp_zis_lit_review

This is a local dogfooding scaffold for a `photocatalysis` literature-review project.
It contains no real paper metadata, claims, PDFs, or copied paper text.

## First Commands

```bash
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
paperwb validate-registry projects/fyp_zis_lit_review/registry.csv
paperwb validate-bib projects/fyp_zis_lit_review/bibtex/library.bib --registry projects/fyp_zis_lit_review/registry.csv
```

## Real-use Rule

Add only metadata, BibTeX entries, notes, and claims that you have verified
yourself. The workbench tracks evidence; it does not invent it.
