# Citation Audit

Citation audit checks whether the user's own registry, notes, claims, evidence links, BibTeX entries, and themes are complete enough to support literature-review writing.

Run:

```bash
paperwb report citation-audit --registry data/registries/papers.csv --bibtex data/bibtex/library.bib --notes-dir data/notes --themes data/examples/themes.json
```

## Findings

The audit identifies:

- papers without notes
- notes without claims
- claims without evidence locations
- weak or low-confidence claims
- BibTeX entries not linked to registry papers
- registry papers missing BibTeX keys
- duplicate DOI or normalized title values
- themes with too few supporting claims
- themes supported only by review statements
- papers tagged for a theme but lacking a clear supporting claim
- registry papers with broken local PDF paths
- claims without confidence values
- claims mapped to undefined themes
- themes with too few supporting papers
- included literature-review papers with weak or speculative evidence

The audit does not decide whether a scientific claim is true. It only checks whether user-supplied evidence tracking is complete and internally consistent.

## Evidence Map

The evidence map groups claims by theme and lists:

- number of supporting papers
- number of claims
- strongest supporting papers
- weakly supported claims
- missing evidence
- suggested follow-up actions

Use it before drafting or revising a literature-review subsection.
