# Project Onboarding: fyp_zis_lit_review

Template: `photocatalysis`

## Intake Loop

- [ ] Add one verified paper row to `registry.csv`.
- [ ] Add or import the matching BibTeX entry into `bibtex/library.bib`.
- [ ] Run `paperwb validate-registry projects/fyp_zis_lit_review/registry.csv`.
- [ ] Run `paperwb validate-bib projects/fyp_zis_lit_review/bibtex/library.bib --registry projects/fyp_zis_lit_review/registry.csv`.
- [ ] Generate a note template with `paperwb note-template PAPER_ID --project fyp_zis_lit_review`.
- [ ] Read the paper yourself and fill the note manually.
- [ ] Add user-written claims with section/page evidence where possible.
- [ ] Run `paperwb claims --project fyp_zis_lit_review`.
- [ ] Run `paperwb report evidence-map --project fyp_zis_lit_review --out projects/fyp_zis_lit_review/reports/evidence_map.md --force`.
- [ ] Run `paperwb report citation-audit --project fyp_zis_lit_review --out projects/fyp_zis_lit_review/reports/citation_audit.md --force`.
- [ ] Back up before larger edits with `paperwb backup create --project fyp_zis_lit_review`.

## Boundaries

- Do not copy PDFs into Git.
- Do not paste copyrighted paper text into examples.
- Do not fabricate metadata, citations, notes, claims, or quotes.
- Treat all reports as planning aids, not scientific-truth judgments.
