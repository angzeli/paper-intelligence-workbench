# Backup Bundles

Backup bundles collect local project data into a portable folder.

```bash
paperwb export bundle --project zis_photocatalysis --out exports/zis_bundle --force
```

The bundle includes:

- registry CSV
- BibTeX file
- notes
- themes
- generated reports
- `manifest.json`
- `bundle_summary.md`

The manifest records export timestamp, tool version, files copied, project name, and whether PDFs were included.

PDFs are not copied by default. Use `--include-pdfs` only when the local files exist and you have the right to copy them.
