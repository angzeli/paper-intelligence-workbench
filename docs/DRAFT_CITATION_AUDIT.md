# Draft Citation Audit

`paperwb draft audit` checks a user-written Markdown draft against local Paper
Intelligence Workbench data. It is an audit workflow, not a writing assistant.

The audit answers:

- which citation keys appear in the draft;
- whether those keys exist in the local BibTeX library;
- whether those keys link to registry papers;
- whether cited papers have structured notes and extracted claims;
- whether paragraph wording is stronger than the tracked evidence;
- whether paragraphs have citations but no local evidence match;
- whether technical paragraphs mention project themes without citations.

Example:

```bash
paperwb draft audit drafts/synthetic_photocorrosion_section.md \
  --project zis_photocatalysis \
  --out scratch/draft_audit.md \
  --force
```

The report uses transparent local keyword, tag, theme, and citation-key overlap.
It does not use embeddings, cloud services, LLM APIs, or publisher scraping.

## Interpretation Boundary

Findings such as `paragraph_no_evidence_match` or
`possible_unsupported_claim` mean "check this manually." They do not prove that
the paragraph is scientifically wrong.
