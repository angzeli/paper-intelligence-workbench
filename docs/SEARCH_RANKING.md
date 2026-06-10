# Search Ranking

Indexed search ranking is intentionally simple and transparent.

Signals:

- exact phrase in title
- exact phrase in tags
- exact phrase in body text
- per-term frequency in title, tags, and body text
- source-type weight

Source-type weights favor paper, claim, text sidecar, and note records over theme/tag helper records. Scores are not semantic relevance judgments. They are local matching scores to help sort larger result sets.

The tool does not use embeddings, cloud APIs, or LLM APIs.

## Matched Field and Snippet

Markdown search exports include the field that matched first and a short snippet from that field. Snippets come only from local indexed text.

