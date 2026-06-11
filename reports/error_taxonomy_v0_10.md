# Error Taxonomy v0.10

The shared taxonomy is implemented in `paper_workbench/errors.py`.

| Code | Severity | Source | Suggested action |
| --- | --- | --- | --- |
| `missing_required_column` | error | registry/import | Check the CSV header row and use the documented registry schema. |
| `malformed_csv` | error | registry/import | Open the CSV locally, fix the row/header structure, and retry. |
| `bad_mapping` | error | import | Fix the JSON mapping so every target is a registry field and every source column exists. |
| `bibtex_parse_warning` | warning | bibtex | Review the surrounding BibTeX manually; the parser is conservative. |
| `note_parse_warning` | warning | notes | Review the note against the structured note format. |
| `corrupt_backup_manifest` | error | backup | Inspect or recreate the backup; restore is blocked until manifest JSON is valid. |
| `audit_log_parse_warning` | warning | audit-log | Review the malformed audit log line; later valid events remain readable. |
| `unsafe_destructive_action` | error | safe-write | Rerun with explicit dry-run or force after reviewing the plan. |
| `path_escapes_workspace` | error | integrity | Use project-relative or workspace-relative paths. |

## Message Standard

Actionable errors should explain:

- what happened
- where it happened
- why it matters
- what the user can do next

The taxonomy is intentionally lightweight and does not replace existing `ValidationFinding` objects.
