# Release Readiness v3.0rc

Release label: v3.0rc  
Package metadata: 3.0.0rc1

## Verdict

Ready for local dogfooding as v3.0rc after the focused workflow-runner blocker
fix and full validation.

## Stable Features

- Workspace initialization.
- Project profiles.
- Project templates.
- Dogfooding scaffold creation, status, checklist, and read-only file planning.
- Registry validation.
- BibTeX validation.
- Explicit paper-row append.
- Registry listing.
- Note-template generation.
- Claim extraction from structured notes.
- Core reports: inventory, reading status, BibTeX audit, evidence map, citation
  audit, weak claims, missing evidence, and report index.
- Read-only doctor and dashboard checks.

## Experimental Features

- Sync apply and conflict reconciliation.
- Forced backup restore and migration runs.
- Local file registry and sidecar audits.
- Draft/manuscript heuristic QA.
- Rule engine expansion.
- Workflow recipes.
- Evidence graph exports.
- Indexed search.
- Review packet import.
- Claim lifecycle and contradiction sidecars.
- Reading sessions.
- Incremental rebuild metadata.

## Deprecated Features

No public CLI command groups are deprecated in v3.0rc. Legacy top-level `data/`
examples remain supported, but new real projects should use project profiles.

## Blockers Fixed

- Fixed workflow runner release-candidate recipe failure caused by a stale
  `build_index_records(root=...)` call.

## Test Status

Completed validation in this release-candidate turn:

- `python -m pytest -q`: passed.
- Package import: reported `3.0.0rc1`.
- `paperwb --help`: passed and points to v3 docs.
- Stable CLI smoke commands: passed for clean-demo registry/BibTeX validation,
  dashboard, doctor/integrity, claims, evidence-map, citation-audit, and
  writing-packet checks.
- Documented quickstart checks: dogfood scaffold, empty-project status, and
  empty registry/BibTeX validation passed in a temporary workspace.
- Workflow dry-run: `release_candidate_check` completed with zero errors after
  the index-step compatibility fix.
- Data-safety audit: passed with 746 files checked, zero errors, zero warnings.
- Notebook structural validation: passed for 8 notebooks.

## Docs Status

v3 docs now define stable, experimental, deprecated, schema, getting-started,
core workflow, first-real-project, data-safety, dogfooding, limitations, and
roadmap surfaces.

## Data Safety Status

The v3 data-safety audit is generated in `reports/data_safety_v3_0_rc.md` and
reported zero errors and zero warnings. Git status showed only ignored caches,
IDE files, local `.paperwb` state, backups, build artifacts, scratch files, and
historical ignored hostile-review drafts outside the staged candidate set.

## What To Freeze

- Stable CLI command names and primary flags.
- Registry CSV fields.
- Structured note sections and claim fields.
- Project-profile layout.
- Theme JSON base fields.
- Local-first safety guarantees.

## What Not To Expand Further Before v3.0.0

- Cloud sync.
- LLM workflows.
- Publisher scraping.
- Web UI.
- Automatic claim generation or verification.
- Arbitrary executable workflow/rule plugins.

## Recommended Steps Before Tagging v3.0.0

1. Dogfood on one real 10-15 paper project.
2. Refresh generated reports after any blocker fixes.
3. Confirm docs match actual first-use commands.
4. Confirm no PDFs, full text, cache databases, backups, or audit logs are
   staged.
5. Re-run the full release validation checklist.
