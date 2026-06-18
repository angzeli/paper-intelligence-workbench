# Safety

Paper Intelligence Workbench is designed for local, user-controlled literature
review work.

## Hard Boundaries

- No cloud APIs.
- No LLM APIs.
- No publisher scraping.
- No PDF downloads or OCR.
- No copied copyrighted paper full text in examples.
- No fabricated paper metadata, citations, claims, quotes, summaries, or
  conclusions.
- No final literature-review prose generation.
- No silent overwrites of user notes, registries, BibTeX files, sync state,
  backups, restores, or migrations.

## Safe Defaults

- Templates and dogfood projects are empty or synthetic.
- Support bundles redact private content by default.
- Import, sync, migration, and restore workflows should be dry-run first.
- Backups do not include PDFs by default.
- Cache and index files are ignored and rebuildable.

## What Not To Commit

- PDFs.
- Copied paper full text or copyrighted sidecars.
- `.paperwb/` caches.
- SQLite index databases.
- Backup archives.
- Audit logs.
- Private dogfood outputs or private absolute paths.
- Real paper metadata that the user did not intentionally add to a project.

## Safety References

- [Data Safety v3](../DATA_SAFETY_V3.md)
- [Privacy Boundaries](../PRIVACY_BOUNDARIES.md)
- [Redaction](../REDACTION.md)
- [Support Bundles](../SUPPORT_BUNDLES.md)
- [Safe Sync Workflow](../SAFE_SYNC_WORKFLOW.md)
- [Safe Write Operations](../SAFE_WRITE_OPERATIONS.md)
- [Migration Guide v3](../MIGRATION_GUIDE_V3.md)
