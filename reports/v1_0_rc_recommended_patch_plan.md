# v1.0-rc Recommended Patch Plan

## High Priority

- Add a `paperwb validate all` command that runs registry, BibTeX, notes, files, integrity, and index checks in one pass.
- Add checksum verification after forced backup restore.
- Add report-diff tooling for golden report changes.
- Add fixture minimization notes so new adversarial cases stay small and readable.
- Add structured JSON output for integrity and failure-mode reports.

## Medium Priority

- Add optional `backup verify` and `backup prune --dry-run`.
- Add `audit-log show --action`, `--since`, and `--failed-only` filters.
- Improve BibTeX recovery around missing commas and string macros.
- Add note lint suggestions for malformed claim headings without rewriting notes.
- Add project-to-project migration planning.

## Low Priority

- Add terminal color only when stdout is a TTY.
- Add a fixture index page that links each adversarial case to its test.
- Add optional compressed backup archives after verification tooling exists.

## Explicitly Out of Scope

- Cloud backup or sync.
- LLM/embedding-based repair of user notes.
- Publisher scraping.
- Automatic metadata correction.
- Destructive cleanup commands.

## Overengineering Risks

Do not turn the taxonomy into a heavy exception hierarchy. The current `ValidationFinding` plus stable codes is sufficient for v1.0-rc.
