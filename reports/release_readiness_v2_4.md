# Release Readiness v2.4

Release label: v2.4
Package metadata: 2.4

## Features Added

- Added `paperwb review-packet create` for local file-based manual review
  packets.
- Added `paperwb review-packet import-comments` for dry-run-first reviewer
  comment validation and sidecar import.
- Added `paperwb review-packet comments`, `response`, and `followups` reports.
- Added packet models for review packets, review items, reviewer comments,
  response reports, and review statuses.
- Added review packet docs, collaboration boundary docs, and a synthetic example
  workflow.

## Safety Behavior

- Review packets do not include PDFs by default.
- Review packets do not use cloud services, email, scraping, LLM APIs, or
  publisher access.
- Reviewer comments are advisory local sidecar metadata.
- Comment import never rewrites claims, notes, registry rows, BibTeX entries,
  or evidence locations.
- Comment import defaults to dry-run unless `--force` is supplied.

## Commands Checked

- `paperwb --help`
- `paperwb review-packet --help`
- `paperwb review-packet create --project zis_photocatalysis --theme photocorrosion`
- `paperwb review-packet import-comments ... --dry-run`
- `paperwb review-packet import-comments ... --force`
- `paperwb review-packet comments`
- `paperwb review-packet response`
- `paperwb review-packet followups`

## Tests Added

- Packet creation and manifest generation.
- CSV comment template generation.
- Comment import dry-run behavior.
- Invalid comment rows and unknown item IDs.
- Response and follow-up report generation.
- No automatic claim overwrite behavior.
- CLI smoke tests for the review-packet command group.

## Validation Run

- `python -m pytest -q` passed.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"` returned `2.4`.
- `paperwb --help` passed.
- `paperwb review-packet --help` passed.
- Review packet creation, dry-run comment import, forced comment import,
  comments report, response report, and follow-up report were checked on the
  synthetic `zis_photocatalysis` project.

## Reports Generated

- `reports/reviewer_comment_import_v2_4.md`
- `reports/reviewer_comments_v2_4.md`
- `reports/response_to_review_v2_4.md`
- `reports/review_followups_v2_4.md`
- `reports/release_readiness_v2_4.md`
- `reports/v2_5_recommended_patch_plan.md`

## Known Limitations

- Packet shape is experimental and may change after real supervisor feedback.
- Comment import validates linked item IDs only when a packet manifest or
  comparable current project items are available.
- Reviewer comments are not merged into existing lifecycle or follow-up systems.
- Draft packet support is intentionally conservative and based on existing
  Markdown draft parsing.

## Verdict

Ready for local dogfooding as an experimental v2.4 collaboration workflow.
The stable evidence database remains unchanged by review-packet operations.
