# Release Readiness v2.5

Release label: v2.5  
Package metadata: 2.5

## Features Added

- Added `paperwb rebuild plan/status/run`.
- Added content-fingerprint helpers for files and path sets.
- Added local rebuild metadata at `.paperwb/rebuild_metadata.json`.
- Extended performance sanity checks with search-index record and SQLite rebuild
  timings.
- Added a synthetic stress-project generation script for larger local workload
  checks.
- Expanded cache-ignore coverage for rebuild metadata, SQLite files, backups,
  audit logs, and stress outputs.

## Commands Checked

- `paperwb rebuild --help`
- `paperwb rebuild plan --project zis_photocatalysis`
- `paperwb rebuild status --project zis_photocatalysis`
- `paperwb rebuild run --project <temporary synthetic project>`
- `python scripts/performance_sanity.py --papers 500 --claims 1500 --themes 50`
- `python scripts/stress_project_generation.py --papers 500 --claims 1500 --themes 50`

## Reports Generated

- `reports/performance_sanity_v2_5.md`
- `reports/incremental_rebuild_plan_v2_5.md`
- `reports/cache_hygiene_v2_5.md`
- `reports/stress_project_summary_v2_5.md`
- `reports/data_safety_audit_v2_5.md`
- `reports/release_readiness_v2_5.md`
- `reports/v2_6_recommended_patch_plan.md`

## Test Coverage Added

- Content hashing changes when file content changes.
- Rebuild plan detects stale inputs.
- Rebuild metadata refresh makes metadata-backed targets current.
- Search index remains stale when the index file is missing.
- Force refresh records every target.
- CLI smoke coverage for `rebuild run/status/plan`.
- `.gitignore` cache hygiene patterns.
- Performance sanity script smoke run.
- Stress project generation script smoke run.

## Known Limitations

- `paperwb rebuild run` refreshes metadata only; it does not run the recommended
  report, index, dashboard, or manuscript commands.
- Rebuild fingerprints are coarse project-level hashes, not per-paper dependency
  graphs.
- Report freshness is based on source fingerprints and expected outputs, not
  semantic report diffing.
- Performance sanity output is a local smoke check, not a reproducible benchmark.

## Release Verdict

Ready for local dogfooding as an experimental v2.5 scale and cache-hygiene
workflow. The patch improves repeatability for larger projects without adding
heavy dependencies or modifying user evidence automatically.
