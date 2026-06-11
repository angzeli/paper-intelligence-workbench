# v0.9 Recommended Patch Plan

## High Priority

- Add a lightweight generated documentation site build, if maintainers want HTML output, without replacing Markdown source.
- Normalize or archive historical reports that still contain machine-local absolute paths.
- Add wheel-build and install-from-wheel smoke checks.
- Add release artifact checklist automation for `CHANGELOG.md`, version consistency, reports, and docs index updates.
- Add report-regression coverage for v0.7 local-file and v0.8 release-engineering reports.

## Medium Priority

- Add optional notebook execution smoke for one short notebook in CI.
- Add a `paperwb version` or `paperwb --version` CLI path.
- Add a release manifest report that links package metadata, test results, smoke results, and data-safety audit output.
- Add optional HTML conversion for Markdown reports using a local-only dependency or standard-library fallback.
- Add import conflict preview tables for ambiguous DOI/title/BibTeX matches.

## Low Priority

- Add shell completion docs.
- Add examples for migrating a legacy `data/` workspace into a project profile without moving files.
- Add richer local-file registry CSV/JSON exports.
- Add machine-readable JSON output for data-safety audit findings.

## Explicitly Not Worth Doing Yet

- Do not publish to PyPI until maintainers agree on release cadence and support expectations.
- Do not add cloud-hosted docs requirements.
- Do not add OCR or PDF full-text extraction.
- Do not add LLM-based summarization or prose generation.
- Do not replace CSV/Markdown source files with a database source of truth.

## Overengineering Risks

- A full documentation-site stack can distract from CLI reliability.
- Strict data-safety rules can become noisy if historical reports are not archived or normalized.
- Release scripts should remain transparent Python scripts rather than an opaque release framework.
