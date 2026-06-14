# Real Project Onboarding v2.0

## Recommended Path

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
```

## Metadata-backed Planning

```bash
paperwb dogfood plan-from-files photocatalysis --project fyp_zis_lit_review --references-dir <references_dir> --bibtex <ref.bib> --out scratch/fyp_15_paper_plan.md --force
```

This command compares local PDF filename slugs with local BibTeX keys. It is a
planning step only. It does not copy files, read PDF text, generate registry
rows, or verify scientific content.

## First Paper Intake Loop

1. Add verified metadata to `registry.csv`.
2. Add the matching BibTeX entry.
3. Validate registry and BibTeX.
4. Generate a note template.
5. Read the paper manually.
6. Add user-written claims and evidence locations.
7. Extract claims.
8. Generate evidence-map and citation-audit reports.
9. Back up before larger edits.

## Release Boundary

v2.0 improves onboarding and dogfooding readiness. It does not add automatic
paper discovery, metadata fabrication, PDF parsing, LLM summarization, or
scientific-truth evaluation.
