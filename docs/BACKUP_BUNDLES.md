# Backup Bundles

Backup bundles collect local project data into a portable folder.

```bash
paperwb export bundle --project zis_photocatalysis --out exports/zis_bundle
```

Choose a new or empty output directory. Bundle export refuses non-empty directories so stale files cannot be mistaken for current backup contents.

The bundle includes:

- registry CSV
- BibTeX file
- notes
- themes
- user-provided `.txt` text sidecars from the project/default `text/` folder
- generated reports
- `manifest.json`
- `bundle_summary.md`

The manifest records export timestamp, tool version, files copied, text sidecars copied, project name, and whether PDFs were included.

PDFs are not copied by default. Use `--include-pdfs` only when the local files exist and you have the right to copy them.

SQLite cache files under `.paperwb/` are not authoritative project data and should not be included in backup bundles.
