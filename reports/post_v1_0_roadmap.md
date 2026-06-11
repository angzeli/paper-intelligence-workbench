# Post v1.0 Roadmap

## High Priority

- Decide whether to bump package metadata from `0.10.0` to a v1.0 release
  version before tagging.
- Run a true fresh virtual-environment install on at least one machine outside
  the development checkout.
- Review historical reports with absolute-path warnings and either keep them as
  archived release artifacts or replace them with portable regenerated reports.
- Add report diff tooling for golden report changes.
- Add checksum verification output after forced restores.

## Medium Priority

- Improve BibTeX macro and string handling while keeping parse warnings
  transparent.
- Add import preview tables for ambiguous matches.
- Add project-to-project migration planning.
- Add richer filters to authoring reports, such as minimum strength and evidence
  type.
- Add optional compressed backup bundles while keeping manifests inspectable.

## Low Priority

- Add optional local HTML export for Markdown reports.
- Add advisory citation-key suggestions.
- Add larger synthetic corpus profiles for performance checks.
- Add local-only report search and report diff browsing.

## Not Worth Doing Yet

- Cloud sync.
- Publisher scraping.
- LLM-generated summaries or prose.
- OCR or full PDF parsing as a default workflow.
- Heavy database migrations that replace CSV/Markdown as authoritative files.

## v1.0.0 Tagging Checklist

- Run the full test suite.
- Run the clean-room check.
- Run the CLI smoke workflow.
- Run the data-safety audit.
- Inspect `git status` for ignored caches and unsafe artifacts.
- Confirm no push, tag, or publication happened accidentally.
