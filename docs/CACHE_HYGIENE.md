# Cache Hygiene

Caches and local safety artifacts are rebuildable or machine-local state. They
should not be committed.

## Ignored Local State

The repository ignores:

- `.paperwb/`
- `rebuild_metadata.json`
- SQLite databases such as `*.sqlite`, `*.sqlite3`, and `*.db`
- SQLite sidecar files such as `*.db-wal`, `*.db-shm`, `*.sqlite-wal`, and `*.sqlite-shm`
- `backups/`
- `audit.log`
- `scratch/`
- `tmp/`
- `stress_outputs/`
- `*.pdf`

## Rebuild Metadata

`paperwb rebuild run` writes `.paperwb/rebuild_metadata.json`. This file records
content fingerprints for stale detection only. It can be deleted and regenerated
without losing user notes, registry rows, BibTeX entries, or claims.

## Search Indexes

The optional SQLite search index is a rebuildable cache. Rebuild it with:

```bash
paperwb index rebuild --project PROJECT
```

Check stale index state with:

```bash
paperwb index status --project PROJECT --check-files
```
