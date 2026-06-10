# SQLite Index

The local search backend uses Python's standard-library `sqlite3` module.

Default cache paths:

- legacy `data/` workflow: `.paperwb/index.sqlite`
- project workflow: `projects/<project>/.paperwb/index.sqlite`

Cache files are ignored by git and should not be committed.

## Records

Each indexed record contains:

- record ID
- project ID
- source type
- source path
- paper ID
- title
- body text
- tags
- year
- reading status
- content hash

The index is rebuildable from local files:

```bash
paperwb index rebuild --project zis_photocatalysis --include-text
```

## FTS5 and Fallback

When SQLite FTS5 is available, the backend creates a `records_fts` virtual table and attempts FTS search first. If FTS5 is unavailable or a query cannot run through FTS, the tool falls back to a normal SQLite table scan with transparent substring matching.

The ranking step is the same after either retrieval path.

