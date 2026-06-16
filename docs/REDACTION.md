# Redaction

Support bundles are safe by default.

Safe mode redacts:

- absolute local paths such as home-directory or temporary filesystem paths
- `local_pdf_path` values
- paper titles, authors, DOI/URL values, and BibTeX keys in registry samples
- claim text
- quotes and paraphrases
- user comments
- note bodies and personal reading notes
- full draft/manuscript text
- secret-like token patterns

Safe mode preserves:

- schema field names
- row counts
- reading-status counts
- tags and themes
- evidence type, strength, confidence, and location fields
- validation finding codes and severities

Preview redaction before writing a bundle:

```bash
paperwb support redact-preview --project clean_demo
```

Verbose local-only mode intentionally preserves more metadata for private
debugging:

```bash
paperwb support redact-preview --project clean_demo --verbose-local-only
```

Do not share verbose bundles until you inspect them manually.
