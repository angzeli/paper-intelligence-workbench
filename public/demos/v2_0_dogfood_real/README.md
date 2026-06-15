# v2.0 Dogfood Demo

This folder is a public, synthetic-only snapshot of the v2.0 dogfood workflow.
It demonstrates the project shape and report locations without committing real
PDFs, real BibTeX metadata, private paths, or generated claims.

For a private real run, use local inputs:

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review --root <demo_root>
paperwb dogfood plan-from-files photocatalysis \
  --project fyp_zis_lit_review \
  --root <demo_root> \
  --references-dir <references_dir> \
  --bibtex <ref.bib> \
  --limit 15 \
  --out <demo_root>/projects/fyp_zis_lit_review/reports/fyp_15_paper_plan.md
```

The real run must remain local and untracked if it contains private filenames,
BibTeX keys, or user-specific paths.
