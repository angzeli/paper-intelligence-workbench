# Repository Cleanup Recommendations

Date: 2026-06-11
Stage: v1.0-rc handoff

## Summary

The repository is usable as a release-candidate development tree, but it is crowded. The main cleanup need is not code deletion; it is separating current release artifacts from historical generated reports and reducing documentation duplication before a public-facing release.

Do not delete user data, project fixtures, notes, synthetic stress data, or historical reports without maintainer approval. Treat this as a recommendation list, not an automatic cleanup plan.

## Files That May Be Redundant

Potentially redundant or consolidation candidates:

- Duplicate CLI docs:
  - `docs/CLI_REFERENCE.md`
  - `docs/cli-reference.md`
  - `docs/CLI_SURFACE.md`
  - `docs/COMMAND_CONTRACTS.md`
- Duplicate project/workflow docs:
  - `docs/PROJECT_PROFILES.md`
  - `docs/project-profiles.md`
  - `docs/WORKFLOW_EXAMPLES.md`
  - `docs/workflows.md`
  - `docs/QUICKSTART_EXTERNAL_USER.md`
  - `docs/EXTERNAL_USER_QUICKSTART.md`
  - `docs/getting-started.md`
- Duplicate search docs:
  - `docs/LOCAL_SEARCH.md`
  - `docs/local-search.md`
  - `docs/SQLITE_INDEX.md`
  - `docs/SEARCH_RANKING.md`
  - `docs/INDEX_MAINTENANCE.md`
- Duplicate local-file docs:
  - `docs/LOCAL_FILES.md`
  - `docs/local-files.md`
  - `docs/TEXT_SIDECARS.md`
  - `docs/FULL_TEXT_SIDECARS.md`
  - `docs/FILE_AUDIT.md`
  - `docs/PDF_METADATA.md`
- Import/export docs that may be merged into fewer pages:
  - `docs/IMPORTS.md`
  - `docs/EXPORTS.md`
  - `docs/import-export.md`
  - `docs/ZOTERO_WORKFLOW.md`
  - `docs/OBSIDIAN_EXPORT.md`
  - `docs/BACKUP_BUNDLES.md`
  - `docs/ROUND_TRIP_TESTING.md`
- Release-era documentation that should remain as historical artifacts but not necessarily appear in a first-page docs path:
  - `docs/ADVERSARIAL_TESTING.md`
  - `docs/ERROR_TAXONOMY.md`
  - `docs/ERROR_MESSAGE_GUIDE.md`
  - `docs/CLI_FAILURE_MODES.md`
  - `docs/RECOVERING_FROM_BAD_DATA.md`
  - `docs/GOLDEN_REPORTS.md`
  - `docs/REPORT_REGRESSION_TESTING.md`

Recommended approach:

- Keep `docs/index.md` as the public docs entry.
- Keep lowercase docs-site pages for user-facing docs.
- Keep uppercase docs as reference pages only where they contain unique detail.
- Add cross-links and "canonical page" notes rather than deleting pages immediately.

## Reports That May Be Stale

Reports to treat as historical rather than current:

- `reports/release_readiness.md`
- `reports/release_readiness_v0_2.md`
- `reports/release_readiness_v0_3.md`
- `reports/release_readiness_v0_4.md`
- `reports/release_readiness_v0_5.md`
- `reports/release_readiness_v0_6.md`
- `reports/release_readiness_v0_7.md`
- `reports/release_readiness_v0_8.md`
- `reports/release_readiness_v0_9.md`
- `reports/release_readiness_v0_10.md`
- `reports/release_readiness_v1_0_rc.md`

The current handoff should be read with `reports/hostile_review_latest.md`. That latest hostile review supersedes the older release-readiness verdict by identifying a release blocker.

Other stale or historical report groups:

- v0.2/v0.3 stress reports and performance reports.
- v0.4 import reports that contain historical path warnings.
- v0.5 search/index reports.
- v0.6 authoring reports.
- v0.7 local-file reports.
- v0.8 external-user and data-safety reports.
- v0.9 backup/migration/audit reports.
- v0.10 adversarial reports.

Recommended approach:

- Keep historical reports until after v1.0.0.
- Add a short note in `reports/index_v1_0_rc.md` or future release index saying `hostile_review_latest.md` is the current risk register.
- After v1.0.0, consider moving old reports into `reports/archive/` if the project wants a cleaner public tree.

## Docs That Overlap

Highest-overlap pairs:

- `docs/CLI_REFERENCE.md` and `docs/cli-reference.md`.
- `docs/REPORT_GALLERY.md`, `docs/reports.md`, and `docs/REPORT_MATRIX.md`.
- `docs/API_SURFACE.md`, `docs/CLI_SURFACE.md`, and `docs/COMMAND_CONTRACTS.md`.
- `docs/LOCAL_SEARCH.md`, `docs/local-search.md`, and `docs/SQLITE_INDEX.md`.
- `docs/LOCAL_FILES.md`, `docs/local-files.md`, `docs/TEXT_SIDECARS.md`, and `docs/FULL_TEXT_SIDECARS.md`.
- `docs/AUTHORING_WORKBENCH.md`, `docs/authoring-workbench.md`, and individual authoring pages such as `docs/EVIDENCE_MATRIX.md`, `docs/CLAIM_BANK.md`, `docs/CITATION_BANK.md`, `docs/PARAGRAPH_PLANNER.md`, `docs/WRITING_PACKET.md`, and `docs/SUBSECTION_READINESS.md`.

Suggested cleanup:

- Choose one canonical user-facing page per topic.
- Keep deeper reference pages only when they have details not present elsewhere.
- Add "See also" links instead of repeating command examples across many pages.
- Prefer examples that write to `scratch/` or temporary paths, not tracked `reports/`.

## Tests That Are Brittle

Potential brittle areas:

- Golden report tests under `tests/golden/` can fail on intended wording or ordering changes.
- Command-contract tests that assert help fragments can become noisy when help text is clarified.
- Data-safety tests include historical absolute-path warning expectations, which may change as reports are cleaned.
- CLI stress tests depend on checked-in synthetic projects staying intentionally imperfect.
- Report regression tests may be sensitive to unordered dict/list output if report generation changes.
- Notebook validation checks portability but does not execute notebooks, so notebook runtime breakage can slip through.
- Failure-path tests should be expanded around write preflight and partial-write behavior.

Recommendations:

- Normalize timestamps, absolute paths, and unordered sections in golden comparisons.
- Prefer structured assertions for counts and required sections over full-file snapshots when output prose is not the contract.
- Add targeted tests for the latest hostile-review findings before any public release.
- Keep synthetic stress fixtures deterministic.

## Generated Artifacts That Should Not Be Committed

Already ignored or should remain ignored:

- `.paperwb/`
- `**/.paperwb/`
- `.pytest_cache/`
- `__pycache__/`
- `*.pyc`
- `.idea/`
- `build/`
- `dist/`
- `*.egg-info/`
- `exports/`
- `backups/`
- `scratch/`
- `tmp/`
- `*.pdf`

Ignored local artifacts observed during this handoff:

- IDE directory.
- local `.paperwb/` audit/index/cache directories.
- Python and pytest caches.
- package egg-info directory.
- ignored historical hostile-review file.

Do not stage those artifacts.

## Suggested `.gitignore` Improvements

Current `.gitignore` already covers the most important local artifacts. Consider adding:

- `.venv/`
- `venv/`
- `.env`
- `.coverage`
- `coverage.xml`
- `htmlcov/`
- `*.sqlite3`
- `*.db-shm`
- `*.db-wal`
- `*.log`
- `*.bak`
- `*.backup`
- `*.zip`
- `*.tar`
- `*.tar.gz`
- `pip-wheel-metadata/`
- `.ruff_cache/` is already covered; keep it.

Do not loosen the `*.pdf` ignore rule unless the project creates a dedicated synthetic dummy-PDF fixture policy.

## Whether Commits Should Be Squashed Before Public Release

Do not squash history casually on the current branch if collaborators may already depend on it.

For public release presentation, a squash or fresh public mirror can be reasonable if:

- maintainers want a clean, understandable v1.0 history;
- all generated reports and release artifacts are final;
- old experimental commits expose no sensitive local paths or mistaken artifacts;
- the current branch has not been shared as the canonical public branch.

If keeping history:

- Tag only after release blockers are fixed.
- Add a current `CHANGELOG.md` entry and release notes that explain v1.0.0 clearly.
- Keep `reports/hostile_review_latest.md` as the current risk register until all release blockers are closed.

Recommended practical path:

1. Fix latest hostile-review blocker and high-priority issues.
2. Regenerate affected reports.
3. Run full CI and true clean install.
4. Decide whether to archive old reports or keep them in place.
5. If public history cleanliness matters, create a reviewed release branch rather than rewriting `main` in place.
