# Hostile Maintainer Review: v0.10 Current Repository

Date: 2026-06-11

## Release Verdict

**Verdict: do not cut an external release until the two safe-write blockers below are fixed.**

The repository is much stronger than the original MVP: the package imports, the 136-test suite passes, notebooks validate structurally, CI exists, local-first boundaries are documented, and representative CLI workflows run. The architecture is coherent for an alpha local-first workbench.

The release is still blocked by two command-ordering bugs in safety-sensitive workflows. Both can apply data-changing work before discovering that the requested report output cannot be written. That violates the project's own v0.9/v0.10 guarantees around dry-run-first workflows, auditability, and non-destructive operation.

Validation performed during this review:

- `python -m pytest -q`: passed, 136 collected tests
- `python scripts/check_notebooks.py`: passed, 8 notebooks checked
- `python scripts/validate_notebooks.py`: passed, 8 notebooks validated
- `python scripts/data_safety_audit.py --out <temporary-review-report> --strict`: passed with 0 errors and 12 warnings
- `python -m paper_workbench.cli --help`: passed
- Representative CLI checks for registry validation, BibTeX validation, project validation, evidence-map generation, citation-audit generation, writing-packet generation, indexed search, local-file status, claims export, import failure handling, and migration dry-run

## Release Blockers

### 1. Forced backup restore can mutate files before report-output preflight

`paper_workbench/cli.py` runs `restore_backup(...)` in `cmd_backup_restore` before attempting to write `args.out` with `force=args.force_report`.

Consequence: `paperwb backup restore BACKUP_ID --force --out existing_report.md` can restore project files and only then fail because the report path already exists. The user sees an error after a state change that should have been preflighted.

Why this blocks release:

- Restore is one of the highest-risk commands in the tool.
- The docs say restore is safety-oriented and reportable.
- The v0.10 failure-mode guide says commands should avoid partial outputs when preflight checks fail.
- The audit log event is also written after the restore/report path, so the failure path can leave a state change without the intended report.

Required fix:

- Preflight `args.out` before calling `restore_backup` when an output path is requested.
- Add a regression test proving that an existing restore report path prevents any restore and prevents pre-restore backup creation.
- Keep dry-run behavior unchanged.

### 2. Forced legacy migration can copy files before report-output preflight

`paper_workbench/cli.py` runs `run_legacy_migration(...)` in `cmd_migrate_run` before attempting to write `args.out` with `force=args.force_report`.

Consequence: `paperwb migrate run --force --out existing_report.md` can copy files into a new project and only then fail because the report path already exists.

Why this blocks release:

- Migration is explicitly marketed as non-destructive and reviewable.
- Report generation is part of the migration audit trail.
- A failed report write after copying files is a bad external-user experience and undermines trust in dry-run/force semantics.

Required fix:

- Preflight `args.out` before forced migration work starts.
- Add a regression test proving an existing migration report path prevents project creation/copying.
- Preserve the existing dry-run default and legacy `data/` compatibility.

## High-Priority Issues

### 1. Claims CSV exports leak machine-local absolute paths

`paper_workbench/claims.py` writes `Claim.note_file` directly. Project notes are parsed from absolute project-profile paths, so `paperwb claims --project ... --output ...` emits rows such as:

```text
.../projects/zis_photocatalysis/notes/zis_charge_2025.md
```

The data-safety audit also reports absolute-path warnings in generated stress claims and historical reports.

Required fix:

- Relativize `note_file` values in claims CSV exports where possible.
- Add tests for `paperwb claims --project ... --output ...` and `export claims` to ensure committed/generated outputs do not contain local absolute paths.
- Regenerate affected reports/CSV outputs.

### 2. External installation docs state the wrong package version

`docs/INSTALLATION.md` says the expected package version is `0.8.0`, while `pyproject.toml` and `paper_workbench.__version__` are `0.10.0`.

Required fix:

- Update the version claim or remove the hardcoded version from installation docs.
- Add a lightweight docs/version consistency test if the version remains documented.

### 3. Forced restore validates the target backup after creating a pre-restore backup

`paper_workbench/backups.py::restore_backup` creates the pre-restore backup before calling `plan_restore(...)` for the selected backup. If the selected backup is corrupt or missing internal files, the command can create a new backup before failing to restore.

This is not data-loss behavior, but it is still a surprising side effect in a failure path.

Required fix:

- Validate/plan the requested backup before creating the pre-restore backup.
- Add a regression test for corrupt or incomplete backup input.

### 4. Several CLI failure messages still miss the v0.10 error-quality bar

The error taxonomy asks for what happened, where it happened, why it matters, and what to do next. Some common failure paths still emit terse messages, for example:

```text
error: backup not found: missing_backup
```

Required fix:

- Improve high-traffic errors for missing backup, wrong project, missing registry, and missing index.
- Add assertions that important failure messages include a next-step hint.

### 5. Current data-safety report is stale and under-versioned

The only data-safety report is `reports/data_safety_audit_v0_8.md`, while the package is v0.10. The script also titles new output as v0.8.

Required fix:

- Regenerate a current data-safety report for v0.10 after absolute-path cleanup.
- Either remove version-specific wording from `paper_workbench/safety.py` or update it consistently.

## Medium-Priority Issues

- Non-indexed search output prints absolute paths for project note matches, while indexed search displays project-relative paths.
- Many current CLI help strings and generated report headings still say v0.7, v0.8, or v0.9. Historical reports can keep old versions, but active commands should not look stale.
- The canonical `zis_photocatalysis` example project reports an integrity error for a missing evidence location. That is useful for demos, but the docs should label it clearly as intentional synthetic bad data.
- Reports and docs are now numerous and partially duplicated between uppercase release docs and docs-site-style lowercase pages.
- Backup creation is not transactional; a copy failure midway could leave a partial backup directory.
- BibTeX parsing is intentionally lightweight and still not suitable for arbitrary BibTeX edge cases beyond the tested recovery behavior.
- Note parsing remains template-sensitive. It tolerates some variants but still silently ignores claim styles outside the supported heading/field pattern.
- CI runs Python 3.11 only despite package classifiers for 3.10, 3.11, and 3.12.

## Low-Priority Polish

- `paperwb project validate` defaults to exit 0 even when errors are printed unless `--strict` is used; this is consistent with other commands but may surprise new users.
- `paperwb files status` prints absolute root and file-registry paths; readable, but less portable than the newer report path style.
- The report directory is crowded with historical release artifacts, making it hard for external users to identify the latest reports.
- Notebook numbering has gaps because some workflows were implemented as scripts instead of notebooks. This is harmless but looks unfinished.
- Some report headings include "Demo" in files that are now used as real command output.

## Missing Tests

Add focused tests for:

- forced restore with an existing `--out` path does not restore files
- forced restore with an invalid/corrupt backup does not create a pre-restore backup
- forced migration with an existing `--out` path does not create/copy a project
- `paperwb claims --project ... --output ...` writes portable `note_file` paths
- `paperwb export claims ...` writes portable `note_file` paths
- installation docs do not claim a version different from `paper_workbench.__version__`
- non-indexed search path display is project-relative or intentionally documented
- data-safety warnings stay below an agreed budget after report regeneration

## Documentation Mismatches

- `docs/INSTALLATION.md` expects version `0.8.0`; package version is `0.10.0`.
- `docs/CLI_FAILURE_MODES.md` says commands should avoid partial outputs when preflight checks fail, but forced restore/migration violate that with `--out`.
- `docs/CLI_REFERENCE.md` says report commands refuse to overwrite existing output unless forced. That is true for direct report commands, but restore/migration combine state changes with later report writes and need stricter wording or fixed behavior.
- `README.md` presents the safety workflow clearly, but it does not warn that the included synthetic example projects intentionally contain errors and warnings.
- Data-safety docs mention historical absolute-path warnings, but the tracked reports still contain them.

## CLI Usability Problems

- Missing backup errors are terse and do not tell the user how to list backups or check `--backups-dir`.
- Forced restore and forced migration can fail after doing work if report output cannot be written.
- Non-indexed search results show absolute paths, while indexed results show portable paths.
- Some active help text still embeds older release numbers, which makes the current CLI look stale.
- Project-profile commands reject path overrides correctly, but the error messages could point users to `--out` or project config when relevant.

## Data-Safety Risks

No tracked PDFs, cache databases, `.paperwb` directories, backup archives, `.idea`, or Python cache files were found in `git ls-files`.

No cloud API, LLM API, publisher scraping, PDF download, OCR, or copyrighted example PDF behavior was found.

Remaining data-safety risks:

- Claims CSV and historical reports contain local absolute paths.
- The data-safety audit currently reports 12 absolute-path warnings.
- User-provided text sidecars are supported correctly, but the audit cannot prove text copyright status. The docs should keep emphasizing synthetic/user-owned text only.
- Restore/migration report-output ordering can weaken auditability on failure.

## Overengineering Risks

The project now has a very broad CLI surface: registry, BibTeX, notes, claims, themes, reports, project profiles, imports, exports, search index, local files, authoring aids, backups, migration, integrity, audit logs, synthetic corpora, and adversarial fixtures.

That breadth is useful, but it creates release-management risk:

- docs and report labels drift across versions
- safety guarantees need command-contract tests, not just module tests
- historical artifacts can mask current release state
- duplicated docs make it easy to update one page and miss another

The architecture should stay boring: standard library, CSV/Markdown/JSON, SQLite cache, deterministic reports, and explicit force/dry-run behavior.

## Recommended Fix Sequence

1. Fix `backup restore --force --out ...` preflight ordering and add no-mutation regression tests.
2. Fix `migrate run --force --out ...` preflight ordering and add no-copy regression tests.
3. Validate selected backups before creating pre-restore backups.
4. Relativize claims CSV/export note paths and regenerate affected reports.
5. Update `docs/INSTALLATION.md` and current data-safety report/version labels.
6. Improve missing-backup and missing-project CLI error messages.
7. Re-run `pytest`, notebook checks, data-safety audit, and representative CLI smoke tests.
8. Regenerate `reports/hostile_review_latest.md` only after the fixes are verified.
