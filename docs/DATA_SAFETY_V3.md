# Data Safety v3

Paper Intelligence Workbench is local-first. v3 keeps user data safety ahead
of automation.

## Hard Boundaries

- No cloud APIs.
- No LLM APIs.
- No publisher scraping.
- No automatic PDF downloads.
- No OCR or full-text extraction by default.
- No copyrighted PDFs or copied full-text examples.
- No fabricated paper metadata, citations, claims, quotes, summaries, or
  conclusions.

## Files That Should Not Be Committed

- `*.pdf`
- `.paperwb/`
- SQLite/cache databases
- backup archives
- audit logs
- private dogfood demo output
- local stress outputs
- build artifacts

The repository `.gitignore` and `MANIFEST.in` exclude these categories where
practical, but maintainers should still inspect `git status --ignored` before
commits.

## Safe Real-Project Use

- Keep real PDFs outside committed fixtures.
- Store paths relatively where possible.
- Validate metadata before extracting claims.
- Write claims manually from your reading notes.
- Back up before forced migration, restore, or sync apply.
- Treat all heuristic reports as prompts for manual review.

## Sanitized Diagnostics

Use support bundles instead of copying project folders when debugging or asking
for help:

```bash
paperwb support redact-preview --project PROJECT
paperwb support bundle --project PROJECT --out scratch/project_support_bundle
```

Safe support bundles preserve schema shape, counts, and validation findings
while redacting private paths, local PDF paths, paper metadata, note bodies,
claim text, quotes, and comments. They do not copy PDFs, cache databases,
backup archives, raw audit logs, full notes, or full drafts.
