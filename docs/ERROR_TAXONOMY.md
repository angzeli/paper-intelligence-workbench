# Error Taxonomy

The v0.10 taxonomy lives in `paper_workbench/errors.py`. It does not replace existing `ValidationFinding` objects; it provides shared language for common user-facing diagnostics.

Each diagnostic should include:

- severity: `error`, `warning`, or `info`
- code: stable machine-readable identifier
- source: parser, importer, registry, backup, migration, index, or CLI area
- message: what happened
- suggested action: what the user should do next

## Representative Codes

| Code | Severity | Source | Meaning |
| --- | --- | --- | --- |
| `missing_required_column` | error | registry/import | A CSV header lacks a required field. |
| `malformed_csv` | error | registry/import | CSV structure cannot be safely interpreted. |
| `bad_mapping` | error | import | Generic CSV mapping is invalid or unsafe. |
| `bibtex_parse_warning` | warning | BibTeX | Parser recovered but the entry needs manual review. |
| `note_parse_warning` | warning | notes | Structured note is incomplete or malformed. |
| `corrupt_backup_manifest` | error | backup | Restore cannot trust `manifest.json`. |
| `audit_log_parse_warning` | warning | audit log | One audit-log line is malformed; later lines remain readable. |
| `unsafe_destructive_action` | error | safe write | A force/dry-run requirement was not satisfied. |
| `path_escapes_workspace` | error | integrity | A relative path escapes the selected workspace root. |

## Compatibility

Existing reports may still use domain-specific codes such as `duplicate_doi`, `missing_author`, or `claim_missing_evidence_location`. New parser and workflow rules should prefer stable codes and update this document when a code becomes public.
