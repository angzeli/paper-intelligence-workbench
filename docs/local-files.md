# Local Files

Local-file workflows reconcile user-provided files with registry rows. They do not download, scrape, OCR, copy, move, delete, or summarize documents.

## Commands

```bash
paperwb files scan --project zis_photocatalysis
paperwb files status --project zis_photocatalysis
paperwb files audit --project zis_photocatalysis --force
paperwb files link PAPER_ID path/to/file.pdf --project zis_photocatalysis
paperwb files unlink PAPER_ID --project zis_photocatalysis
paperwb files sidecars --project zis_photocatalysis
```

`files scan` is read-only unless `--write-registry` is supplied. File-registry writes merge with existing `files.csv` rows so curated notes are preserved.

Detailed docs:

- [LOCAL_FILES.md](LOCAL_FILES.md)
- [TEXT_SIDECARS.md](TEXT_SIDECARS.md)
- [PDF_METADATA.md](PDF_METADATA.md)
- [FILE_AUDIT.md](FILE_AUDIT.md)
