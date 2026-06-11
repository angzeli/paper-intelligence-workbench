# Claim Traceability

`paperwb manuscript trace-claims` reverses the manuscript audit: instead of starting from draft paragraphs, it starts from tracked local claims.

It reports whether each claim:

- appears in the draft through heuristic evidence matching
- appears in one or more paragraphs
- is not used
- is used despite weak evidence or missing evidence location
- appears repeatedly across multiple paragraphs

Example:

```bash
paperwb manuscript trace-claims drafts/synthetic_overconfident_section.md \
  --project zis_photocatalysis \
  --theme photocorrosion \
  --out reports/claim_traceability_v1_4.md \
  --force
```

Traceability is useful before writing or revising a subsection because it shows which tracked evidence actually made it into the draft.
