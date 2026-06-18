# Real Project Safety

Real project mode is intentionally conservative.

## Do

- Keep real workspaces outside the repository.
- Register them with `paperwb external add`.
- Run `paperwb external validate NAME` before reports.
- Generate reports into the external workspace.
- Use `paperwb external run NAME support-bundle` for redacted diagnostics.
- Run the data-safety audit before commits.

## Do Not

- Do not copy PDFs into the repository.
- Do not commit `.paperwb-local/`.
- Do not commit real BibTeX exports, real registry rows, private notes, full
  drafts, or private support bundles.
- Do not use cloud APIs, LLM APIs, publisher scraping, or PDF downloading.
- Do not treat reviewer comments, graph connections, or heuristic QA findings
  as scientific truth.

## Before Sharing Diagnostics

Open the generated support bundle and confirm it contains only sanitized
diagnostic files. Safe bundles should not contain PDFs, cache databases, backup
archives, raw audit logs, full notes, full drafts, or private comments.

