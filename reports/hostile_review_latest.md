# Hostile Maintainer Review: Current Release Candidate

Date: 2026-06-11

## Release Verdict

**Verdict: do not ship as an external release candidate until the uncaught audit-log traceback is fixed.**

The repository is materially stronger than earlier stages. It now has a coherent local-first architecture, broad CLI coverage, project profiles, registry and BibTeX validation, structured notes, claim extraction, theme reports, authoring reports, local file scanning, indexed search, import/export workflows, backup and migration safeguards, adversarial fixtures, CI, packaging metadata, and release-candidate documentation.

The current release candidate still has one release-blocking CLI failure: `paperwb audit-log clear` without `--force` raises an uncaught traceback instead of a clean user-facing error. That violates the documented command contract and makes the CLI look unsafe in a normal safeguard path.

Validation performed during this review:

- `python -m pytest -q`: passed.
- `python scripts/data_safety_audit.py --out <tmp-report> --title "Hostile Review Data Safety" --strict`: passed with 0 errors; only historical warning-class findings were reported.
- `python scripts/clean_room_install_check.py --quick --out <tmp-report>`: passed, 7 current-environment steps, 0 failures.
- `python scripts/check_notebooks.py`: passed, 8 notebooks checked.
- `python scripts/validate_notebooks.py`: passed, 8 notebooks validated.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`: reported `1.0.0rc1`.
- `paperwb --help`: passed.
- Representative project, registry, BibTeX, claims, evidence-map, writing-packet, import, export, search, integrity, backup, and migration probes were run.
- `python -m build` could not be verified in the current environment because the active Python environment does not expose an executable `build.__main__`.

## Release Blockers

### 1. `paperwb audit-log clear` exposes an uncaught traceback

Repro:

```bash
python -m paper_workbench.cli audit-log clear
```

Observed behavior:

- exit code: `1`
- stderr includes a Python traceback
- final exception: `PermissionError: audit-log clear requires --force`

Why this blocks release:

- This is a normal safety path, not an exceptional internal failure.
- A command that refuses to clear audit logs without `--force` is correct, but it must fail cleanly.
- The command contract says common failure paths should return clear user-facing errors.
- Tracebacks in safety commands reduce trust in backup, migration, and audit-log behavior.

Likely cause:

- `paper_workbench/cli.py::main` catches `FileNotFoundError`, `FileExistsError`, `IsADirectoryError`, `NotADirectoryError`, and `ValueError`, but not `PermissionError`.
- `paper_workbench/cli.py::cmd_audit_log` raises `PermissionError` for the expected no-force path.

Required fix:

- Either raise `ValueError` for the no-force path or include `PermissionError` in the CLI's user-facing exception handling.
- Return exit code `2`.
- Include an actionable message such as "Use --force to clear the audit log."
- Add a CLI regression test asserting no traceback is printed.

## High-Priority Issues

### 1. `paperwb report all` can leave partial report output after a later collision

Probe:

- A temporary reports directory was created with `citation_audit.md` already present.
- `paperwb report all ... --reports-dir <tmp>/reports` refused to overwrite `citation_audit.md`.
- Before failing, it had already written earlier reports such as inventory, reading status, papers by tag, BibTeX audit, claims by theme, and evidence map.

Why this matters:

- The protected file was not overwritten, which is good.
- The command still leaves a half-generated report set after failure.
- Users can mistake the partial report directory for a complete run.
- This violates the release theme of predictable, non-destructive write operations.

Required fix:

- Preflight all default output paths for `report all` before writing any report.
- If any path would collide, fail before writing the first file unless `--force` is supplied.
- Add a test that seeds a later output path and asserts no earlier outputs are created.

### 2. `paperwb report all --out ...` silently ignores `--out`

Probe:

```bash
paperwb report all --registry data/registries/example_papers.csv --bib data/bibtex/example_library.bib --notes data/notes --reports-dir <tmp>/reports --out <tmp>/single.md
```

Observed behavior:

- exit code: `0`
- multiple files were written under `--reports-dir`
- `<tmp>/single.md` was not created
- no warning or error was printed

Why this matters:

- `--out` is meaningful for individual report types, so users reasonably expect it to matter.
- Silently ignoring a write-path option is exactly the kind of CLI behavior that produces misplaced files.
- This is not data loss, but it is high-priority release polish because it affects a common meta-command.

Required fix:

- Reject `--out` with `report all` and explain that `--reports-dir` controls multi-report output, or implement a single index output if that is intended.
- Add a CLI regression test for the rejected or implemented behavior.

### 3. Active docs still contain examples that write to tracked `reports/` paths

The dedicated external-user quickstart is safer, but broader README and workflow documentation still include commands that write directly to checked-in `reports/` files, often with `--force`.

Why this matters:

- A new external user following a later workflow section can dirty a fresh checkout.
- It encourages `--force` before the user understands what is being overwritten.
- It conflicts with the safe-write posture that v0.9 and v1.0-rc documentation emphasize.

Required fix:

- Move tutorial outputs to `scratch/`, an ignored temporary workspace, or explicitly project-local generated paths.
- Reserve `--force` in docs for commands that first explain why overwrite is safe.
- Add a lightweight docs smoke check for command examples that should not write to tracked report artifacts.

### 4. Package build is not verified in the local release review environment

`python -m build` failed in the current environment because the active Python environment does not expose `build.__main__`.

Why this matters:

- The package is not being published yet, but a release candidate should prove source and wheel distributions can be built somewhere reliable.
- CI may cover this if it installs development extras first, but the local release artifact was not proven by this review.

Required fix:

- Ensure CI runs `python -m build` after installing development extras.
- Document that local maintainers should run the build check in a clean environment with build tooling installed.
- Keep distribution artifacts ignored.

### 5. `files link` and `files unlink` appear non-transactional across multiple metadata files

The local-file commands update file-registry and paper-registry state. The code path appears to perform multiple writes without an explicit rollback strategy if a later write fails.

Why this matters:

- Local file linking is data-integrity sensitive.
- A failure between writes can leave a file registry and paper registry disagreeing.
- This is not observed data loss, but it is a high-priority hardening risk before broad external use.

Required fix:

- Add tests that simulate a later write failure and assert the workspace is left consistent.
- Prefer write-to-temp-and-rename behavior for multi-file updates, or preflight all writable targets before mutating the first file.
- At minimum, emit a clear warning and audit-log event if a partial write is detected.

## Medium-Priority Issues

- `paper_workbench/cli.py` remains very large and owns argument parsing, command behavior, report dispatch, import/export orchestration, and error handling. This makes future safety audits harder.
- Some active CLI help and docs still carry historical version labels such as v0.7, v0.9, or v0.10. Historical reports can keep versions; active help should be release-neutral.
- The canonical synthetic project intentionally contains validation findings, so `project validate --strict` fails. That is valid synthetic coverage, but it can surprise users unless every quickstart distinguishes "demo warnings" from "release failure."
- The data-safety audit still reports historical warning-class findings. They are not blockers, but the warning budget should be documented and kept from growing.
- `files hash` on a missing path fails without a traceback, but the message is still a raw filesystem-style error rather than a full "what happened, why it matters, what to do next" diagnostic.
- Lightweight BibTeX and Markdown note parsing remain intentionally conservative. Docs mostly say this, but report wording should keep saying "tracked evidence completeness," not truth or exhaustive bibliographic correctness.
- Backup creation and restore planning are safer than earlier stages, but partial-copy behavior should be explicitly tested under simulated I/O failures.
- The documentation tree has both docs-site-style lowercase pages and older uppercase reference pages. That duplication increases drift risk.

## Low-Priority Polish

- `reports/` is crowded with historical artifacts. `reports/index_v1_0_rc.md` helps, but new users may still open stale reports first.
- Some generated reports still use demo-oriented titles even when they are part of the release artifact set.
- Notebook numbering has gaps because notebooks were added over several releases.
- Several command-contract tests check help fragments rather than full command lifecycle behavior.
- The clean-room check script name still sounds stronger than its default quick mode, which uses the current environment.
- Some docs still use long command examples that are hard to copy safely without line wrapping mistakes.

## Missing Tests

Add focused tests for:

- `paperwb audit-log clear` without `--force` returns exit code `2`, prints no traceback, and tells the user to use `--force`.
- `paperwb report all` preflights every output path and creates no partial output when a later report path already exists.
- `paperwb report all --out <path>` either fails with a clear message or creates the documented output.
- `files link` and `files unlink` remain consistent if one of their writes fails.
- Backup creation under simulated copy/write failure does not produce a misleading valid manifest.
- README and docs command examples do not write to tracked report files unless the section explicitly explains the overwrite.
- Local package build succeeds in CI or a dedicated release-check script.
- Python version support matches either CI matrix coverage or package classifiers.

## Documentation Mismatches

- `docs/COMMAND_CONTRACTS.md` says common failure paths should be user-facing. `audit-log clear` violates this with a traceback.
- Some README/workflow examples still encourage direct writes to tracked `reports/` outputs, while external-user quickstart material uses safer scratch-style paths.
- `reports/release_readiness_v1_0_rc.md` should be regenerated after the audit-log traceback and report-all partial-write behavior are addressed.
- Clean-room wording should distinguish current-environment smoke checks from a true fresh virtual environment install.
- API surface docs should continue to emphasize that CLI commands and file formats are more stable than Python helper internals.

## CLI Usability Problems

- `paperwb audit-log clear` without `--force` prints a traceback.
- `paperwb report all --out` is accepted but ignored.
- `paperwb report all` can fail after writing a partial report set.
- `files hash` missing-file errors are safe but terse.
- Some command help includes historical version labels that make active commands look provisional.

## Data-Safety Risks

No tracked PDFs, SQLite cache databases, `.paperwb` directories, backup archives, IDE folders, Python cache files, or obvious secret files were found in tracked files during this review.

No cloud API, LLM API, publisher scraping, PDF download, OCR, or copyrighted example PDF behavior was found.

Remaining data-safety risks:

- `audit-log clear` safeguard path crashes with a traceback.
- `report all` can leave partial generated outputs after a collision.
- Tutorial commands can still dirty tracked `reports/` outputs.
- Local file linking may become inconsistent under partial write failures.
- Text sidecar copyright safety cannot be proven automatically; the docs correctly keep emphasizing synthetic or user-owned text.
- Historical absolute-path warnings remain in report artifacts and should not grow.

## Overengineering Risks

The project now spans registry validation, BibTeX parsing, notes, claims, evidence maps, citation audits, project profiles, import/export, indexed search, local files, authoring aids, backups, migration, audit logs, adversarial fixtures, docs-site pages, CI, release checks, and generated reports.

The breadth is useful, but release risk now comes from consistency:

- every write path needs the same force/dry-run/preflight semantics;
- every safety refusal needs a clean error, not a traceback;
- every report generator needs predictable overwrite behavior;
- docs examples need to be treated like tested user workflows;
- the public API surface should stay narrow until internals stabilize.

Do not add new features before fixing the release blocker and high-priority safety issues above.

## Recommended Fix Sequence

1. Fix `paperwb audit-log clear` no-force behavior so it returns a clean user-facing error; add a regression test.
2. Make `paperwb report all` preflight all output paths before writing; add a no-partial-output test.
3. Reject or implement `paperwb report all --out`; add a CLI regression test.
4. Audit README and workflow docs for commands that write to tracked `reports/` paths; move examples to scratch paths where appropriate.
5. Add simulated partial-write tests for `files link`, `files unlink`, and backup creation.
6. Verify package build in CI or a documented release-check environment.
7. Regenerate affected release-readiness, data-safety, and report-index artifacts after the fixes.
