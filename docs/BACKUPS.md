# Backup Snapshots

v0.9 backup snapshots copy key local project files into `backups/` by default.

```bash
paperwb backup create --project zis_photocatalysis
paperwb backup list --project zis_photocatalysis
paperwb backup inspect BACKUP_ID --project zis_photocatalysis
```

Backups include registry, BibTeX, notes, themes, and project profile metadata. Generated reports are excluded unless `--include-reports` is used. PDFs, SQLite indexes, cache files, and `.paperwb/` state are excluded.

Each backup has a `manifest.json` with:

- backup ID
- created timestamp
- project name
- tool version
- included files
- excluded files
- optional notes

Backups are local files. They are not pushed, uploaded, encrypted, or synchronized by this tool.

## Git Policy

`backups/` is ignored. Do not commit backup snapshots unless a future fixture is intentionally small, synthetic, and reviewed.
