# Adding Real Papers Safely

Paper Intelligence Workbench can track real local literature-review data, but it
must not invent or import uncertain evidence as truth.

## Safe Intake Checklist

- [ ] Confirm the paper belongs in the project.
- [ ] Add only verified title, authors, year, venue, DOI, URL, and BibTeX key.
- [ ] Store local file paths relatively where possible.
- [ ] Validate registry and BibTeX.
- [ ] Generate a note template.
- [ ] Read the paper yourself.
- [ ] Write summaries, claims, and evidence locations manually.
- [ ] Extract claims and regenerate reports.
- [ ] Back up before large edits.

## Commands

```bash
paperwb validate-registry projects/PROJECT/registry.csv
paperwb validate-bib projects/PROJECT/bibtex/library.bib --registry projects/PROJECT/registry.csv
paperwb note-template PAPER_ID --project PROJECT
paperwb claims --project PROJECT --output scratch/PROJECT_claims.csv --force
paperwb report evidence-map --project PROJECT --out projects/PROJECT/reports/evidence_map.md --force
paperwb report citation-audit --project PROJECT --out projects/PROJECT/reports/citation_audit.md --force
paperwb backup create --project PROJECT --notes "Before major registry or note edits"
```

## What To Avoid

- Do not commit PDFs.
- Do not commit full-text article sidecars unless they are synthetic.
- Do not paste copyrighted article sections into notes for examples.
- Do not mark a claim strong without a page or section evidence location.
- Do not treat manuscript QA or dashboards as scientific truth evaluation.
