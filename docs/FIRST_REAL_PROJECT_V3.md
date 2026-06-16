# First Real Project v3

The recommended first real project is a small FYP-style literature review with
10-15 papers added manually from user-verified metadata.

## Recommended Path

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
```

If you already have a local references folder and a BibTeX file, generate a
planning report before editing project data:

```bash
paperwb dogfood plan-from-files photocatalysis \
  --project fyp_zis_lit_review \
  --references-dir <references_dir> \
  --bibtex <ref.bib> \
  --limit 15 \
  --out scratch/fyp_15_paper_plan.md \
  --force
```

This compares filenames and BibTeX keys only. It does not copy PDFs, read PDF
text, write registry rows, or fabricate metadata.

## Manual Intake Checklist

For each paper:

1. Verify title, authors, year, venue, DOI, and BibTeX key yourself.
2. Add the registry row with `paperwb add-paper` or a reviewed import.
3. Validate the registry and BibTeX.
4. Generate a note template.
5. Read the paper.
6. Write claims and evidence locations manually.
7. Extract claims and review evidence gaps.

## What Not To Do

- Do not commit PDFs or full text.
- Do not paste copyrighted paper text into fixtures.
- Do not treat filename or PDF metadata as authoritative.
- Do not let an import overwrite non-empty registry fields silently.
- Do not use generated reports as final prose.
