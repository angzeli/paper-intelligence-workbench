# Structured Note Format

Paper notes are Markdown files under `data/notes/`. Generate a template with:

```bash
paperwb note-template PAPER_ID
```

The parser expects these headings:

```text
# Paper Note: [Title]
## Metadata
## One-sentence summary
## Why this paper matters
## Research question or problem
## Method / approach
## Key findings
## Limitations
## Useful for my literature review
## Not useful for
## Claims and evidence
### Claim 1
## Open questions
## Follow-up actions
```

Metadata uses bullet fields:

```text
- Paper ID:
- BibTeX key:
- DOI:
- Year:
- Journal:
- Tags:
- Reading status:
```

Claim blocks use bullet fields:

```text
- Claim:
- Evidence type:
- Section / page:
- Quote or paraphrase:
- Confidence:
- Tags:
- User comment:
- Strength:
- Supports theme:
```

The parser is conservative. Missing metadata, unknown evidence types, unknown strengths, and missing evidence locations are returned as warnings. The tool does not infer or fabricate claims from free-form prose.

Supported reading statuses:

- `unread`
- `skimmed`
- `partially_read`
- `read`
- `deeply_read`
- `archived`

Supported evidence types:

- `experimental_result`
- `review_statement`
- `method_description`
- `theory_or_mechanism`
- `limitation`
- `background_context`
- `opinion_or_interpretation`
- `unclear`

Supported claim strengths:

- `strong`
- `moderate`
- `weak`
- `speculative`
