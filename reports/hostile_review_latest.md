# Hostile Maintainer Review: Latest v0.8 Scoped Fix Verification

## Release Verdict

**Verdict: the release-blocking and high-priority findings from the previous local-file hostile review are resolved.**

This report is intentionally scoped. The requested fix pass limited work to the release-blocking and high-priority issues already listed in the previous `reports/hostile_review_latest.md`. It is not a new broad hostile review of every v0.8 feature.

The current repository has the required local-file safeguards in code, tests, docs, CI, and regenerated reports:

- local-file audit output preflights all targets before writing
- duplicate registry `local_pdf_path` values are detected
- local-file warning details are printed by `files scan` and `files status`
- `files unlink` does not clear manual PDF metadata when no file-registry row was removed
- `files scan --write-registry` merges with existing `files.csv` records
- local-file audit reports reconcile existing `files.csv` records
- CI includes local-file smoke checks

## Release Blockers

None remain from the scoped review.

### Resolved: `files audit` partial writes

`paper_workbench/cli.py` preflights all four local-file audit report outputs before writing any file. The regression test `test_cli_files_audit_preflights_all_outputs_before_writing` verifies that a later output collision prevents earlier report creation.

### Resolved: duplicate registry local file path detection

`paper_workbench/files.py` tracks `relative_path -> list[paper_id]`, records `duplicate_registry_paths`, and marks scanned files as `linked_multiple_registry_paths` when more than one registry paper points to the same file. The regression test `test_scan_local_files_warns_when_registry_reuses_same_local_path` covers this.

## High-Priority Issues

None remain from the scoped review.

### Resolved: CI local-file smoke coverage

`.github/workflows/ci.yml` runs:

- `python -m paper_workbench.cli files --help`
- `python -m paper_workbench.cli files scan --project zis_photocatalysis`
- `python -m paper_workbench.cli files audit --project zis_photocatalysis --reports-dir /tmp/paperwb_ci_file_reports --force`

`tests/test_release_hygiene.py` asserts those release gates remain present.

### Resolved: warning details hidden from `files scan` and `files status`

Both commands now print warning detail lines after the summary/output. `tests/test_local_files_v0_7.py` verifies sidecar warnings are visible in both paths.

### Resolved: `files unlink` clearing manual PDF metadata

`unlink_file_from_paper` now clears `local_pdf_path` only when at least one matching file-registry row was removed. `test_unlink_without_file_registry_record_does_not_clear_manual_pdf_path` covers the edge case.

### Resolved: forced file-registry writes discarding curated rows

`files scan --write-registry` now calls `merge_file_registry_records`, preserving curated notes for matching records and retaining older unmatched rows for review. The CLI test verifies curated sidecar notes and unmatched rows survive a forced scan write.

### Resolved: file audit missing `files.csv` reconciliation

`scan_local_files` now reports missing files referenced by `files.csv`, records outside the current scan folders, and hash mismatches. `local_files_audit_report` and `missing_files_report` include those sections/counts, and `test_file_audit_reconciles_existing_file_registry_records` covers them.

## Medium-Priority Issues

The following were intentionally deferred because they were not release-blocking or high-priority in the scoped review:

- top-level text-sidecar semantics could be clearer for nested text files
- `files audit --project ... --reports-dir ...` still allows an explicit reports-directory override
- old ignored review drafts may still exist locally but are not tracked
- report-directory information architecture remains crowded
- custom diagnostic reports can include local absolute paths if the user chooses such paths

## Low-Priority Polish

Deferred:

- add a header row to `files scan`
- improve raw error handling for `files hash` missing paths
- add richer `files sidecars` output for nested text files
- continue reducing report-directory clutter

## Missing Tests

No missing tests remain for the scoped blocker/high-priority fixes. Existing tests cover:

- local-file audit output preflight
- duplicate registry file paths
- local-file warning output
- safer unlink metadata behavior
- file-registry merge preservation
- file-registry reconciliation
- local-file CLI help/scan/audit smoke coverage
- tracked-PDF policy
- CI release-gate presence

Deferred medium/low polish could still use tests when implemented.

## Documentation Mismatches

The high-priority local-file documentation mismatches are resolved:

- `README.md` documents merged file-registry writes and audit preflight/reconciliation behavior.
- `docs/LOCAL_FILES.md` documents merged file-registry writes and safer unlink semantics.
- `docs/FILE_AUDIT.md` documents duplicate registry paths and `files.csv` reconciliation.
- `docs/CLI_REFERENCE.md` documents local-file merge and unlink behavior.

## CLI Usability Problems

Resolved for scoped findings:

- warning details are now visible in `files scan`
- warning details are now visible in `files status`
- `files audit` no longer leaves partial output after an overwrite collision
- `files scan --write-registry` preserves existing file-registry data instead of replacing it wholesale

Remaining polish is medium/low priority and intentionally deferred.

## Data-Safety Risks

No scoped release-blocking data-safety risks remain. Local-file commands remain non-destructive to user files, backup bundles still omit PDFs by default, SQLite indexes remain rebuildable ignored caches, and no cloud/LLM/scraping behavior was introduced.

The v0.8 data-safety audit still reports warnings for historical reports containing local absolute paths. Those warnings are tracked in `reports/data_safety_audit_v0_8.md` and are not part of the scoped local-file blocker fix.

## Overengineering Risks

The fixes stayed within the existing CSV/Markdown/local-cache architecture. The local-file registry remains a reconciliation aid, not authoritative managed storage. No copying, moving, deleting, PDF parsing, OCR, cloud calls, or LLM APIs were added.

## Recommended Fix Sequence

The scoped release-blocking/high-priority sequence is complete:

1. Preflight local-file audit outputs before writing.
2. Detect duplicate registry `local_pdf_path` values.
3. Add local-file CLI smoke checks to CI/tests.
4. Print warning detail lines in `files scan` and `files status`.
5. Prevent `files unlink` from clearing manual PDF metadata when no file-registry row was removed.
6. Preserve curated file-registry records during scan writes.
7. Reconcile existing `files.csv` records in local-file audits.
8. Update affected local-file docs and reports.

Recommended next step is a fresh full hostile review of the current v0.8 release candidate, not more work under this scoped fix pass.
