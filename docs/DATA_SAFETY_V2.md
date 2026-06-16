# Data Safety v2

Paper Intelligence Workbench is local-first.

## Prohibited In Repository Fixtures

- Copyrighted PDFs.
- Copied full paper text.
- Real secrets or API keys.
- No cloud APIs.
- No LLM APIs.
- No publisher scraping.
- Fabricated real paper metadata, claims, quotes, or conclusions.

## Ignored Local Artifacts

- `.paperwb/`
- SQLite index files.
- Audit logs.
- Backup snapshots.
- Exports and scratch outputs.
- Python caches and build artifacts.
- PDFs.

## Safe Defaults

- Imports support dry-run and preserve non-empty fields.
- Sync apply is dry-run first.
- Restore and migration require explicit force for writes.
- Bundle exports do not include PDFs by default.
- Dashboard is read-only except for explicit `--out`.

## Historical Warning Allowlist

The data-safety audit suppresses a small explicit allowlist of old release
reports and tests that intentionally contain local absolute-path examples from
earlier hostile reviews or path-safety fixtures. New private paths outside that
allowlist should still appear as warnings and must be reviewed before release.
