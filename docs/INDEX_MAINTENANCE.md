# Index Maintenance

The SQLite index is a rebuildable cache. If it is missing or stale, rebuild it from local inputs.

```bash
paperwb index status --project zis_photocatalysis --include-text --check-files
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb index clear --project zis_photocatalysis
```

`index status --check-files` compares current local file-derived records with indexed content hashes and reports changed or missing records.

The command does not watch files in the background. There is no daemon or cloud service.

## Safe Practices

- Rebuild after editing registry rows, BibTeX files, notes, themes, or sidecar text.
- Keep `.paperwb/` out of git.
- Do not store copyrighted full text in sidecars.
- Use `--include-text` only when sidecar files are intended to be indexed.

