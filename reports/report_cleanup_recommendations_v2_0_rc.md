# Report Cleanup Recommendations v2.0rc

## Keep

- Current v2.0rc release reports.
- Historical release-readiness and hostile-review reports as audit trail.
- Synthetic example reports used by tests and docs.

## Consider Archiving Later

- Old unversioned reports once v2 docs no longer reference them.
- Superseded patch plans after a public v2 tag.
- Historical stress reports if they become too noisy for public browsing.

## Do Not Commit In Future

- Reports with local absolute paths.
- Reports generated from private user data.
- Cache/index diagnostics containing private filenames unless intentionally
  sanitized.
- Backup archives, audit logs, SQLite indexes, exports, and scratch outputs.

## Squash Guidance

Before a public release, consider squashing only if maintainers want a cleaner
history. The current granular history is useful for auditability.

