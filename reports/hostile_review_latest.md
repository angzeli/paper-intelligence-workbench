# Hostile Maintainer Review: v1.0-rc Current Repository

Date: 2026-06-11

## Release Verdict

**Verdict: do not ship this as an external release candidate until the claims and registry JSON safe-write blockers are fixed.**

The repository is much stronger than the earlier MVP line. It has a coherent local-first architecture, zero runtime dependencies, broad tests, CI, project profiles, import/export workflows, authoring aids, local search, local-file audits, backup/migration safeguards, adversarial fixtures, and v1.0-rc surface documentation.

That said, the current command surface still has unsafe and misleading behavior in ordinary user-facing commands:

- `paperwb claims` silently treats a missing notes path as a successful empty extraction.
- `paperwb claims --output` silently overwrites existing files and has no `--force` flag.
- `paperwb validate-registry --json` silently overwrites existing JSON output and has no `--force` flag.

Those bugs directly contradict `docs/COMMAND_CONTRACTS.md`, which says generated files must not be overwritten without an explicit force flag and that normal bad inputs should return user-facing errors. They are release blockers because they can erase user-generated analysis artifacts or produce empty claim registries after a typo.

Validation performed during this review:

- `python -m pytest -q`: passed, 148 tests collected.
- `python scripts/data_safety_audit.py --out <temporary-review-report> --title "Hostile Review Data Safety" --strict`: passed with 0 errors and 11 warnings.
- `python scripts/clean_room_install_check.py --quick --out <temporary-review-report>`: passed, 7 steps, 0 failures.
- `python scripts/check_notebooks.py`: passed, 8 notebooks checked.
- `python -m paper_workbench.cli --help`: passed.
- Failure-path probes for missing project, missing indexed-search cache, and missing backup returned non-zero without tracebacks.
- Overwrite and missing-path probes for `claims` and `validate-registry --json` reproduced the blockers below.
- `python -m build`: failed because the current environment does not provide an executable `build.__main__`.

## Release Blockers

### 1. `paperwb claims` silently succeeds on a missing notes path

Repro:

```bash
python -m paper_workbench.cli claims /private/tmp/definitely_missing_paperwb_notes_dir
```

Observed behavior:

- exit code: `0`
- stdout/stderr: empty

With an output path:

```bash
python -m paper_workbench.cli claims /private/tmp/definitely_missing_paperwb_notes_dir --output /private/tmp/paperwb_missing_claims_probe.csv
```

Observed behavior:

- exit code: `0`
- stdout: `Wrote 0 claims to ...`

Why this blocks release:

- A mistyped notes directory can produce an empty claims CSV that looks successful.
- Claim extraction is central to citation audits, evidence maps, writing packets, and exports.
- The command contract says bad inputs should return a user-facing error.

Required fix:

- Validate that the notes path exists before collecting notes.
- Return exit code `2` with an actionable error when the path is missing.
- Add tests for missing directory, missing file, and valid empty existing directory behavior.

### 2. `paperwb claims --output` silently overwrites existing files

Repro:

```bash
python -m paper_workbench.cli claims data/notes --output /private/tmp/paperwb_claims_overwrite_probe.csv
python -m paper_workbench.cli claims data/notes --output /private/tmp/paperwb_claims_overwrite_probe.csv
```

Observed behavior:

- Both commands exit `0`.
- The second command overwrites the existing CSV.
- There is no `--force` option for `paperwb claims`.

Code path:

- `paper_workbench/cli.py::cmd_claims`
- `paper_workbench/claims.py::save_claims_csv(..., force=True)`

Why this blocks release:

- Claim CSVs are user work products, not rebuildable caches in every workflow.
- This violates the v1.0-rc command contract for generated files.
- It undermines the project’s “preserve user notes and raw files” safety posture.

Required fix:

- Add `--force` to `paperwb claims`.
- Default to refusing existing output paths.
- Pass `force=args.force` into `save_claims_csv`.
- Add no-overwrite and force-overwrite CLI regression tests.

### 3. `paperwb validate-registry --json` silently overwrites existing files

Repro:

```bash
python -m paper_workbench.cli validate-registry data/registries/example_papers.csv --json /private/tmp/paperwb_registry_overwrite_probe.json
python -m paper_workbench.cli validate-registry data/registries/example_papers.csv --json /private/tmp/paperwb_registry_overwrite_probe.json
```

Observed behavior:

- Both commands exit `0`.
- The second command overwrites the existing JSON output.
- There is no `--force` option for this export path.

Code path:

- `paper_workbench/cli.py::cmd_validate_registry`
- `paper_workbench/registry.py::save_registry_json`
- `paper_workbench/io.py::write_json(..., force=True)`

Why this blocks release:

- `validate-registry --json` is effectively an export command.
- The command contract says generated files should not be overwritten without force.
- The README and docs encourage external users to run validation commands early.

Required fix:

- Add `--force` for the JSON export path.
- Refuse existing `--json` output by default.
- Add tests for no-overwrite and force behavior.

## High-Priority Issues

### 1. README quickstart writes into tracked `reports/` files with `--force`

The dedicated external quickstart correctly writes to `scratch/`, but the top-level README quickstart still tells new users to run commands such as:

```bash
paperwb claims data/notes --output reports/example_claims.csv
paperwb report inventory --registry data/registries/example_papers.csv --force
paperwb report evidence-map ... --force
```

This dirties a fresh clone and can overwrite checked-in report artifacts. That is the opposite of a safe first-run experience.

Required fix:

- Change README quickstart outputs to `scratch/` or a temp workspace.
- Add a doc smoke test or script check that README quickstart examples do not write to tracked report files.

### 2. Package metadata still says `0.10.0` while release docs advertise `v1.0-rc`

`pyproject.toml` and `paper_workbench.__version__` are still `0.10.0`. The v1.0-rc reports acknowledge this, but an external user running install verification sees `0.10.0`, not an RC identity.

This is acceptable for an internal hardening pass, but not for a public release candidate.

Required fix before public RC:

- Decide whether the RC is versioned `1.0.0rc1`, `1.0.0-rc`, or stays `0.10.0`.
- Align `pyproject.toml`, `paper_workbench.__version__`, changelog, and release reports.

### 3. The "clean-room install check" is not a real clean-room install

`scripts/clean_room_install_check.py` explicitly uses the current environment, injects `PYTHONPATH`, and invokes `python -m paper_workbench.cli`. That is useful, but it does not prove that a fresh external checkout can install and run the console entry point.

CI does run editable install, but the clean-room report title overstates what the script proves.

Required fix:

- Either rename the script/report to "current-environment release check" or add an optional true venv mode.
- Make CI prove `paperwb --help` after editable install, not only `python -m paper_workbench.cli --help`.

### 4. Wheel/sdist build is not verified

`python -m build` failed in the review environment:

```text
/opt/anaconda3/bin/python: No module named build.__main__; 'build' is a package and cannot be directly executed
```

The project is not being published yet, but external release engineering should at least verify that source and wheel distributions can be built in CI or document that the release is editable-install only.

Required fix:

- Add a CI build check after installing `.[dev]`, or document that v1.0-rc is not a distribution artifact.
- Keep build artifacts ignored.

### 5. The API surface doc over-promises stability

`docs/API_SURFACE.md` marks many module helpers as "stable enough" without detailed function contracts. Several of those helpers are implementation-facing and may need refactoring, especially `reporting`, `exports`, `index`, `files`, `backups`, and `migration`.

Required fix:

- Narrow the stable Python API to dataclasses plus a small set of loader/validator functions, or mark module helpers as semi-stable/experimental.
- State that CLI and file formats are the stable API for v1.0.

### 6. CLI errors expose absolute local paths

Examples from review probes:

- missing project: `/Users/liangze/Desktop/paper-intelligence-workbench/projects/...`
- missing backup: `/Users/liangze/Desktop/paper-intelligence-workbench/projects/...`
- missing index: `/private/tmp/nonexistent_paperwb_review.sqlite`

Absolute paths are useful locally, but users often paste CLI errors into issues. This is not a functional blocker, but it conflicts with the data-safety posture and keeps absolute-path warnings alive in reports.

Required fix:

- Prefer workspace-relative paths in user-facing errors when possible.
- Keep absolute paths available only when the path is outside the workspace or when explicitly requested.

### 7. Historical absolute-path warnings remain in tracked reports

The v1.0-rc data-safety audit reports 0 errors and 11 warnings. All warnings are absolute local path patterns in historical reports/tests.

This is documented, but for a public release candidate the report archive still looks untidy and machine-specific.

Required fix:

- Decide whether historical reports are immutable audit artifacts or should be sanitized/regenerated.
- If kept, document the warning budget explicitly in `DATA_SAFETY_MATRIX.md`.

### 8. CI tests only Python 3.11 despite classifiers for 3.10, 3.11, and 3.12

`pyproject.toml` claims Python 3.10, 3.11, and 3.12 support. CI only runs 3.11.

Required fix:

- Add a matrix for 3.10, 3.11, and 3.12, or narrow classifiers.

## Medium-Priority Issues

- `paper_workbench/cli.py` is over 1,700 lines and now owns too much orchestration, argument parsing, error handling, and command behavior.
- Active help text still embeds older release numbers such as v0.7, v0.9, and v0.9/v0.10 in command descriptions. Historical reports can keep versions; active CLI help should be release-neutral.
- The canonical `zis_photocatalysis` project intentionally contains evidence gaps and integrity errors, but this is not obvious enough in every quickstart path.
- There are many duplicated docs: uppercase release docs and lowercase docs-site pages can drift.
- `write_text`, `write_json`, and `write_csv_rows` default to `force=True`. Callers often override it, but this default contributed to the blockers above.
- Backup creation is not transactional; a copy failure can leave a partial backup directory.
- BibTeX parsing remains intentionally lightweight and should not be presented as robust for arbitrary user libraries.
- Note parsing remains template-sensitive and ignores unsupported claim-heading styles.
- The release report says `paperwb --help` passed, but the clean-room script itself does not call the installed `paperwb` console script.

## Low-Priority Polish

- `paperwb project validate` exits 0 by default even when errors are printed unless `--strict` is used. This is consistent with validators but surprising.
- `reports/` is crowded with historical artifacts; a new user has to know which report index is current.
- Notebook numbering has gaps.
- Some generated report titles still say "Demo".
- `CONTRIBUTING.md` release checks do not mention `scripts/clean_room_install_check.py` or notebook JSON validation.
- Some command-contract tests check for option/help fragments rather than end-to-end behavior for every command they list.

## Missing Tests

Add focused tests for:

- `paperwb claims MISSING_PATH` returns non-zero and does not write output.
- `paperwb claims --output existing.csv` refuses overwrite by default.
- `paperwb claims --output existing.csv --force` overwrites intentionally after the new flag is added.
- `paperwb validate-registry --json existing.json` refuses overwrite by default.
- `paperwb validate-registry --json existing.json --force` overwrites intentionally after the new flag is added.
- README quickstart commands write only to ignored `scratch/` or temporary paths.
- Installed console script `paperwb --help` works in CI after editable install.
- Source and wheel distribution build succeeds.
- Python 3.10 and 3.12 test matrix, or classifier consistency if matrix is not added.
- User-facing errors avoid workspace absolute paths where possible.

## Documentation Mismatches

- `docs/COMMAND_CONTRACTS.md` says generated files are not overwritten without force; `claims --output` and `validate-registry --json` violate that.
- `docs/CLI_SURFACE.md` says report/export write safety is stable; claims extraction and registry JSON validation have export-like writes without safe defaults.
- README quickstart uses tracked `reports/` outputs and `--force`, while `docs/EXTERNAL_USER_QUICKSTART.md` correctly uses `scratch/`.
- `docs/API_SURFACE.md` implies broader Python API stability than the implementation is ready to support.
- `reports/release_readiness_v1_0_rc.md` says no blockers were found, but the overwrite and missing-path probes above show release blockers.
- `reports/clean_room_install_check_v1_0_rc.md` is named as clean-room even though the script says it uses the current Python environment.

## CLI Usability Problems

- `paperwb claims` has no `--force` despite writing files.
- `paperwb validate-registry --json` has no `--force` despite writing files.
- `paperwb claims` gives no error for a nonexistent notes path.
- Some errors include absolute local paths that are noisy and privacy-sensitive in shared logs.
- Active command help still includes old release numbers, making the CLI look like a stack of historical prototypes.

## Data-Safety Risks

No tracked PDFs, SQLite cache databases, `.paperwb` directories, backup archives, `.idea`, Python cache files, or obvious secret files were found in `git ls-files`.

No cloud API, LLM API, publisher scraping, PDF download, OCR, or copyrighted example PDF behavior was found.

Remaining data-safety risks:

- Silent overwrites in `claims --output` and `validate-registry --json`.
- Silent empty claim extraction on missing notes paths.
- README quickstart overwrites tracked reports.
- Historical absolute-path warnings remain in tracked reports/tests.
- User-facing CLI errors expose local absolute paths.
- Text sidecar copyright safety cannot be proven automatically; docs correctly keep emphasizing synthetic or user-owned text.

## Overengineering Risks

The project has become a large local workbench with registry validation, BibTeX parsing, structured notes, claims, themes, reports, project profiles, import/export, search indexing, local-file ingestion, authoring aids, backups, restore, migration, audit logs, synthetic data, adversarial fixtures, docs-site pages, CI, and release reports.

That breadth is defensible, but the risks are now release-management risks:

- safety guarantees must be enforced uniformly across all write commands;
- docs drift is already visible;
- versioned historical reports can contradict current release claims;
- a broad "stable" API surface will slow necessary refactors;
- monolithic CLI orchestration makes command-level safety audits harder.

Keep the v1.0 scope boring: local files, explicit force/dry-run semantics, reproducible reports, and CLI/file-format stability. Do not expand features until the safe-write contract is uniformly enforced.

## Recommended Fix Sequence

1. Fix `paperwb claims` missing-path handling and add regression tests.
2. Add `--force` to `paperwb claims`; refuse existing output by default; add tests.
3. Add `--force` to `validate-registry --json`; refuse existing output by default; add tests.
4. Update README quickstart to use `scratch/` outputs only.
5. Update command-contract docs and release-readiness report after blockers are fixed.
6. Add CI proof for installed `paperwb --help`, package build, and Python version matrix or adjust classifiers.
7. Narrow `docs/API_SURFACE.md` to avoid overpromising Python helper stability.
8. Reduce absolute local paths in user-facing errors and regenerate the data-safety report.
