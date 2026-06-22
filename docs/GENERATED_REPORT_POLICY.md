# Generated Report Policy

Generated reports are useful release evidence, but they should not become a dumping ground for private data or stale artifacts.

## Commit Reports When

- They are release-readiness, data-safety, compatibility, architecture, or public-demo evidence.
- They are generated from synthetic or empty local data.
- They help a future maintainer understand the current supported surface.
- They contain no private paths, PDFs, full text, raw notes, drafts, secrets, cache databases, backup archives, or audit logs.

## Do Not Commit

- Private dogfooding output from real projects.
- Reports generated from external workspaces unless all private paths and metadata are redacted.
- `.paperwb/` cache output, SQLite indexes, rebuild metadata, backup archives, audit logs, or support bundles with verbose local-only data.
- Reports under `scratch/`, `tmp/`, `exports/`, or project-local private workspaces.

## Current Reports Directory

The root `reports/` directory intentionally contains historical release-burn artifacts. New users should start from:

- `reports/index.md`
- `reports/hostile_review_latest.md`
- the newest release-readiness report
- current data-safety and dogfooding reports

Older v0.x, v1.x, and v2.x reports should be treated as historical evidence, not current user guidance.

## Archive Policy

Do not delete historical reports casually. Prefer a reviewed archive move such as:

```text
reports/archive/v0/
reports/archive/v1/
reports/archive/v2/
reports/archive/v3-pre-rc2/
```

Before moving reports, update `reports/index.md`, docs links, and any tests that intentionally reference historical files.

## Regeneration Policy

Regenerate current release reports when changing:

- public CLI behavior
- stable versus experimental surface docs
- safety or privacy behavior
- report generation behavior
- docs or cookbook commands
- release-readiness verdicts

Generated reports should say what commands were run and whether they used synthetic data.
