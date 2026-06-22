# Artifact Inventory v3.0rc2

Date: 2026-06-22

Scope: public-release cleanup inventory for the repository after v3.5 private dogfooding support. This is an inventory and pruning plan, not a deletion record.

## Current State

- Package metadata: `3.5`.
- Cleanup label: `v3.0rc2`.
- Root reports directory: large historical inventory with more than 200 Markdown reports.
- Tracked unsafe artifacts: none found in the inspected tracked-file patterns.
- Ignored local artifacts present: `.paperwb/`, project `.paperwb/`, backups, caches, build outputs, `.DS_Store`, and Python caches.
- Pre-existing tracked modifications were present before this cleanup task in code, tests, and one notebook. They are not classified here as generated artifacts, but they prevent a perfectly clean release worktree until resolved separately.

## Must Keep

- `README.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `pyproject.toml`
- `paper_workbench/`
- `tests/`
- `docs/index.md`
- `docs/STABLE_SURFACE_V3.md`
- `docs/EXPERIMENTAL_FEATURES_V3.md`
- `docs/CLI_REFERENCE_V3.md`
- `docs/DATA_SAFETY_V3.md`
- `docs/PRIVATE_DOGFOODING.md`
- `docs/EXTERNAL_WORKSPACES.md`
- synthetic `data/`, `projects/`, `drafts/`, `examples/`, and `notebooks/`
- current safety and release-readiness reports

## Useful Historical

- v0.x and v1.x reports that document early validation, parser, import/export, authoring, and release-readiness work.
- v2.x reports that document dogfooding, graph, lifecycle, workflow, review-packet, performance, and architecture stabilization work.
- v3.0rc, v3.1, v3.2, v3.3, v3.4, and v3.5 reports that document the current release-hardening arc.

## Stale But Harmless

- Legacy unversioned reports such as `reports/inventory.md`, `reports/evidence_map.md`, and `reports/workspace_health.md`.
- Old release-readiness reports for versions that are no longer current.
- Historical stress reports and report-regression outputs generated from synthetic data.

## Should Move To Archive

These should not be deleted without review, but they should eventually move out of the root reports directory:

- `reports/release_readiness_v0_*.md`
- `reports/release_readiness_v1_*.md`
- `reports/release_readiness_v2_*.md`
- historical v0/v1/v2 feature reports
- old release-candidate simulation reports
- old stress and hostile-review drafts that are not the canonical latest review

## Should Not Be Committed In Future

- `.paperwb/`
- `.paperwb-local/`
- `*.sqlite`, `*.db`, and SQLite sidecar files
- `backups/`
- audit logs
- support bundles from real projects
- private external workspace reports with path-revealing mode enabled
- PDFs
- copied paper full text
- `.DS_Store`
- build outputs and egg-info directories
- `scratch/`, `tmp/`, and ad hoc export directories

## Unsafe If Public

No tracked unsafe files were found by the inspected patterns. The unsafe categories remain:

- real PDFs or full text
- private external workspace config
- verbose support bundles
- raw audit logs
- cache databases
- backup archives
- reports containing private absolute paths, real paper filenames, or real bibliography metadata

## Recommendation

Do not delete reports in this cleanup pass. Add a generated-report policy, keep current v3.0rc2/v3.5 reports visible, and schedule an archive move after confirming no docs or tests depend on historical root-level paths.
