# Privacy Boundaries

Support bundles must not include:

- PDFs
- copied paper full text
- full structured notes
- full drafts or manuscripts
- private reviewer comments
- raw audit logs
- cache or index databases
- backup archives
- API keys, tokens, or secrets

The support workflow generates new summaries instead of copying project source
files. It is designed to preserve enough structure for debugging while keeping
research content private.

## Before Sharing

1. Run `paperwb support redact-preview --project PROJECT`.
2. Generate the bundle in safe mode.
3. Inspect `data_safety_summary.md`.
4. Inspect `sanitized_registry_sample.csv` and `sanitized_claims_sample.csv`.
5. Confirm no private paper titles, notes, drafts, paths, or PDFs are present.

The tool can reduce risk, but it cannot prove that a manually shared folder is
safe after a user edits it.
