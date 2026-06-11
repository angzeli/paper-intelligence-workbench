# File Audit Reports

The v0.7 file audit reports connect registry rows, local files, and text sidecars.

```bash
paperwb files audit --project zis_photocatalysis --force
```

Generated reports:

- `local_files_audit_v0_7.md`
- `duplicate_files_v0_7.md`
- `missing_files_v0_7.md`
- `text_sidecars_v0_7.md`

Reports include:

- supported files found under scan folders
- unlinked files
- missing files referenced by `local_pdf_path`
- duplicate SHA256 hashes
- text sidecars and filename matches
- unsupported files
- suggested cleanup warnings

The reports do not inspect scientific claims, do not parse PDF full text, and do not decide whether a file is the correct paper. They audit local organization and metadata completeness only.
