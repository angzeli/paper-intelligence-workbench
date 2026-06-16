# Cache Hygiene v2.5

## Summary

v2.5 keeps performance and rebuild state local, reproducible, and disposable.
The new rebuild metadata file is cache state, not user evidence.

## Ignored Cache and Local State

- `.paperwb/`
- `**/.paperwb/`
- `rebuild_metadata.json`
- `**/rebuild_metadata.json`
- `*.sqlite`
- `*.sqlite3`
- `*.db`
- `*.db-wal`
- `*.db-shm`
- `*.sqlite-wal`
- `*.sqlite-shm`
- `backups/`
- `**/backups/`
- `audit.log`
- `**/audit.log`
- `scratch/`
- `tmp/`
- `stress_outputs/`
- `**/stress_outputs/`
- `*.pdf`

## Rebuild Metadata Boundary

`paperwb rebuild run` writes `.paperwb/rebuild_metadata.json` only. It records
content fingerprints for stale detection and can be deleted safely. It does not
rewrite registry rows, notes, BibTeX entries, reports, drafts, or indexes.

## Search Index Boundary

SQLite indexes remain rebuildable caches. They are ignored by default and should
be regenerated with `paperwb index rebuild` when stale.

## Data-safety Result

No v2.5 cache state, stress project directory, backup archive, audit log, PDF, or
SQLite database should be staged for commit.
