# Reviewer Comment Import

Reviewer comments are collected in the packet `comments.csv` file and imported
separately from project evidence.

The generated `comments.csv` is a template. Rows with no `comment` and no
`recommendation` are treated as untouched template rows and skipped with a
warning. Add at least one of those fields before expecting a comment to be
imported.

```bash
paperwb review-packet import-comments scratch/review_packet_photocorrosion/comments.csv \
  --project zis_photocatalysis \
  --theme photocorrosion \
  --dry-run
```

The default is non-destructive. Use `--force` only after reviewing the dry-run
report:

```bash
paperwb review-packet import-comments scratch/review_packet_photocorrosion/comments.csv \
  --project zis_photocatalysis \
  --theme photocorrosion \
  --force \
  --out scratch/reviewer_comment_import.md \
  --force-report
```

Imported comments are stored in `.paperwb/reviewer_comments.json` under the
selected project or workspace root unless `--comments-store` is provided.

The importer validates:

- required CSV fields
- supported item types
- supported review statuses
- duplicate comment IDs
- unknown item IDs when a manifest or current project items are available

It never rewrites claim text, note files, registry rows, BibTeX, or evidence
locations.
