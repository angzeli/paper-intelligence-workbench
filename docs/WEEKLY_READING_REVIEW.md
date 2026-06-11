# Weekly Reading Review

The weekly reading review summarizes local reading-session activity and points
to remaining evidence gaps.

## Command

```bash
paperwb reading review --project zis_photocatalysis --out scratch/weekly_reading_review.md --force
paperwb reading review --project zis_photocatalysis --days 14 --out scratch/two_week_review.md --force
paperwb reading review --project zis_photocatalysis --as-of 2026-06-11 --out scratch/reproducible_review.md --force
```

Use `--as-of YYYY-MM-DD` or an ISO datetime when you need reproducible review
windows for tests, examples, or generated reports. Without `--as-of`, the
review window is relative to the current local run time.

## Report Contents

The report includes:

- sessions in the selected period
- papers marked read or deeply read
- notes created during sessions
- user-supplied claims-added count
- weak or incomplete themes
- open follow-up actions
- next recommended reading queue

Malformed session-log lines and corrupt follow-up completion state are reported
as warnings and skipped. The source notes and session files are not rewritten.

## Boundary

This is a workflow report. It does not certify that a theme is scientifically
settled and does not infer missing claims from papers. Use it to decide what to
read or check next.
