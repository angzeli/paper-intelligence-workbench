# Support Bundle Redaction Preview

Safe mode is active: titles, authors, DOI/URL values, local PDF paths, note bodies, claims, quotes, and user comments are redacted.

Project: clean_demo
Root: <redacted-path>/clean_demo

## Counts Preserved

| Item | Count |
| --- | ---: |
| bibtex_entries | 1 |
| claims | 1 |
| notes | 1 |
| papers | 1 |
| reports | 0 |
| themes | 1 |

## Registry Sample Shape

| paper_id | title | authors | year | doi | local_pdf_path | bibtex_key | reading_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| paper_001 | <redacted-title-001> | <redacted-authors> | 2026 | <redacted-doi> |  | <redacted-bibtex-key-001> | read |

## Claims Sample Shape

| claim_id | paper_id | claim_text | evidence_type | section | page | quote_or_paraphrase | strength |
| --- | --- | --- | --- | --- | --- | --- | --- |
| claim_001 | paper_001 | <redacted-claim-text> | experimental_result | Fixture section p. 1 | 1 | <redacted-quote-or-paraphrase> | strong |

## Redaction Rules

- `absolute local paths` -> `<redacted-path>`: Home-directory and temporary filesystem paths are replaced.
- `local_pdf_path` -> `<redacted-local-pdf-path>`: PDF references are never exported as usable paths.
- `note bodies` -> `<redacted-note-body>`: Structured note prose is summarized by counts only.
- `claim_text` -> `<redacted-claim-text>`: Claim text is redacted in safe mode.
- `quote_or_paraphrase` -> `<redacted-quote-or-paraphrase>`: Quotes/paraphrases are redacted by default.
- `secret/token patterns` -> `<redacted-secret>`: Known secret-like strings are replaced.
