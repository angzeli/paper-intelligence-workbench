# Local Search

The default search path is substring-based and requires no index:

```bash
paperwb search photocorrosion --project zis_photocatalysis
```

For larger workspaces, build a local SQLite index:

```bash
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb index status --project zis_photocatalysis --include-text --check-files
paperwb search photocorrosion --project zis_photocatalysis --indexed --text
```

The index is a rebuildable cache under `.paperwb/`. It is ignored by git and is not authoritative source data.

Detailed docs:

- [LOCAL_SEARCH.md](LOCAL_SEARCH.md)
- [SQLITE_INDEX.md](SQLITE_INDEX.md)
- [FULL_TEXT_SIDECARS.md](FULL_TEXT_SIDECARS.md)
- [SEARCH_RANKING.md](SEARCH_RANKING.md)
- [INDEX_MAINTENANCE.md](INDEX_MAINTENANCE.md)
