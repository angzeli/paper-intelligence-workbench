# Manuscript QA

`paperwb manuscript qa` audits a user-written Markdown or LaTeX-ish literature-review draft against local registry, BibTeX, structured notes, claims, and themes.

It checks:

- citation keys found in the draft
- unknown BibTeX or registry keys
- cited papers missing notes or claims
- paragraphs with no citations
- paragraphs whose citations do not match tracked claims
- strong wording backed only by weak, missing, or review-statement evidence
- reviewer-style revision checklist items

Example:

```bash
paperwb manuscript qa drafts/synthetic_overconfident_section.md \
  --project zis_photocatalysis \
  --out reports/manuscript_qa_v1_4.md \
  --force
```

The final readiness verdict is a local completeness verdict, not a scientific truth judgment.

## Boundary

The command does not rewrite prose, invent citations, invent claims, or verify scientific truth. It uses transparent lexical matching only.
