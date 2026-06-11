# v0.10 Recommended Patch Plan

## High Priority

- Add checksum verification after forced restores and include results in restore reports.
- Add a restore conflict mode that can skip overwrites or restore only selected paths.
- Add audit-log filters for action, project, path substring, success, dry-run, and date range.
- Add migration path rewriting diagnostics for `notes_path`, `local_pdf_path`, and report links.
- Add tests for backup behavior with missing backup files and hash mismatches.

## Medium Priority

- Add optional compressed backup archives while keeping `manifest.json` inspectable.
- Add project-to-project migration plans for splitting or renaming review projects.
- Add a `backup verify` command.
- Add a `migrate inspect` command that compares source and target after a forced migration.
- Add a report that summarizes recent audit-log events by command type.

## Low Priority

- Add colored terminal output when supported.
- Add a compact machine-readable JSON output option for integrity and migration reports.
- Add a configurable backup retention report.
- Add richer report-index grouping for safety reports.

## Not Worth Doing Yet

- Cloud backup integrations.
- Automatic destructive cleanup of old files.
- Background file watching.
- Full database replacement for CSV/Markdown sources.
- PDF text extraction or OCR as a default workflow.

## Overengineering Risks

The safety layer should remain understandable and inspectable. Backup, restore, migration, and audit-log commands should keep using transparent local files rather than becoming a hidden state-management system.
