# Dogfooding Guide v3

The dogfooding workflow is the recommended bridge from synthetic examples to a
real local literature-review project.

## Create An Empty Project

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
```

The scaffold contains empty registry, BibTeX, notes, reports, drafts, and
reading-session folders plus onboarding checklists. It contains no real papers.

## Plan From Local Files Without Importing

```bash
paperwb dogfood plan-from-files photocatalysis \
  --project fyp_zis_lit_review \
  --references-dir <references_dir> \
  --bibtex <ref.bib> \
  --limit 15 \
  --out scratch/fyp_15_paper_plan.md \
  --force
```

The plan reports counts, supplement-like files, BibTeX keys, filename/key
matches, unmatched files, unmatched keys, and a starter shortlist if enough
exact matches exist. It does not copy PDFs, read PDF text, or write registry
rows.

## First Week Target

- Add 10-15 verified papers manually.
- Generate note templates.
- Read and write structured notes.
- Extract claims.
- Generate an evidence map and citation audit.
- Use dashboard and checklist reports to decide what to read next.
