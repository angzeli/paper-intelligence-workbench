# Backward Compatibility v2

## Supported

- Legacy `data/` workflow compatibility remains supported.
- Legacy `data/registries`, `data/notes`, `data/bibtex`, and `data/examples`
  workflows remain supported.
- Project profiles under `projects/` remain supported.
- Existing v1 structured notes should continue to parse conservatively.
- Existing registry fields from v1 are preserved.
- Existing report commands still write Markdown and refuse overwrites without
  force flags.

## Not Guaranteed Stable

- SQLite index cache schema.
- Audit-log JSONL schema.
- Backup internal directory shape.
- Sync-plan JSON schema.
- Generated report table ordering beyond tested stable sections.
- Synthetic stress corpus exact records.

## Compatibility Priority

The highest priority is preserving user notes, registries, BibTeX files, themes,
and project profiles. Cache files and generated reports can be regenerated.
