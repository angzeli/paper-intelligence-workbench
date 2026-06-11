# v1.2 Recommended Patch Plan

## High Priority

- Fix any remaining write-path inconsistencies from the latest hostile review,
  especially multi-report preflight behavior.
- Add more real-world synthetic draft fixtures for citation punctuation,
  footnote-like text, and mixed Markdown/link syntax.
- Tune draft-audit false positives around short introductory paragraphs that do
  not need citations.
- Add report-diff tooling for draft audits so users can compare revisions.

## Medium Priority

- Add optional CSV/JSON export for paragraph evidence matrices.
- Add citation-pattern examples for common Pandoc variants if users request
  them.
- Add project-specific draft folders in generated project profiles.
- Improve report wording for cases where a citation is known in BibTeX but not
  linked to a registry paper.

## Low Priority

- Add optional local HTML rendering for draft audit reports.
- Add configurable strong-wording dictionaries per discipline.
- Add local-only draft section summaries based only on extracted paragraph
  headings and citation coverage.

## Explicitly Out Of Scope

- LLM-based draft rewriting.
- Automatic citation insertion.
- Semantic truth judgments.
- Publisher scraping or remote metadata lookup.
- PDF full-text extraction as a default path.
