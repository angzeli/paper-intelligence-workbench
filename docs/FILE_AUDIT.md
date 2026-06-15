# File Audit Reports

File audit reports connect registry rows, local files, and text sidecars.

```bash
paperwb files audit --project zis_photocatalysis --force
```

Generated reports:

- `local_files_audit_v2_3.md`
- `duplicate_files_v2_3.md`
- `missing_files_v2_3.md`
- `text_sidecars_v2_3.md`

Reports include:

- supported files found under scan folders
- unlinked files
- missing files referenced by `local_pdf_path`
- duplicate registry `local_pdf_path` values pointing to the same file
- duplicate SHA256 hashes
- existing `files.csv` rows whose files are missing
- existing `files.csv` rows outside the current scan folders
- existing `files.csv` rows whose stored hash differs from the current file hash
- text sidecars and filename matches
- unsupported files
- suggested cleanup warnings

`files audit` checks all target report paths before writing, so an overwrite conflict will not leave a partially refreshed audit set. Use `--force` to intentionally overwrite existing audit reports.

The reports do not inspect scientific claims, do not parse PDF full text, and do not decide whether a file is the correct paper. They audit local organization and metadata completeness only.
