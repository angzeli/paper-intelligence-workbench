# Release Readiness v0.8

## Summary

v0.8 focuses on external release engineering: packaging metadata, CI hardening, docs-site Markdown source, external-user onboarding, release scripts, data-safety auditing, and release matrices. The project remains local-first and dependency-light.

## Packaging

- Package version: `0.8.0`.
- Python requirement: `>=3.10`.
- Runtime dependencies: none.
- Test optional dependency group: `test = ["pytest>=8"]`.
- CLI entry point: `paperwb = "paper_workbench.cli:main"`.
- License: Apache-2.0.
- Editable install path: `python -m pip install -e ".[test]"`.

## CI And Scripts

- Existing GitHub Actions workflow was expanded.
- CI runs pytest, notebook validation, notebook static checks, package import, CLI help, CLI smoke workflow, local-file smoke commands, data-safety audit, and tracked-artifact hygiene.
- `scripts/smoke_cli_workflow.py` runs a non-destructive synthetic workflow.
- `scripts/check_notebooks.py` validates notebook JSON, titles, and path portability.
- `scripts/data_safety_audit.py` scans tracked and unignored files for forbidden artifacts, possible secrets, absolute local paths, large files, and publisher-bypass references.

## Documentation

- Added docs-site source pages:
  - `docs/index.md`
  - `docs/getting-started.md`
  - `docs/workflows.md`
  - `docs/cli-reference.md`
  - `docs/reports.md`
  - `docs/project-profiles.md`
  - `docs/local-search.md`
  - `docs/import-export.md`
  - `docs/authoring-workbench.md`
  - `docs/local-files.md`
  - `docs/safety-and-boundaries.md`
- Added release matrices:
  - `docs/TEST_MATRIX.md`
  - `docs/CLI_BEHAVIOR_MATRIX.md`
  - `docs/REPORT_MATRIX.md`
  - `docs/DATA_SAFETY_MATRIX.md`
- Added `docs/EXTERNAL_USER_QUICKSTART.md`, `docs/INSTALLATION.md`, and `docs/SITE_MAP.md`.

## Validation Performed

- `python -m pytest -q` passed during v0.8 validation.
- `python scripts/check_notebooks.py` passed.
- `python scripts/smoke_cli_workflow.py --out reports/external_user_simulation_v0_8.md --title "External User Simulation v0.8"` passed.
- `python scripts/data_safety_audit.py --out reports/data_safety_audit_v0_8.md --strict` passed with zero errors.
- `python -m paper_workbench.cli --help` passed.
- Editable install check was run before final handoff.

## Data-Safety Assessment

- No tracked or unignored PDFs, SQLite caches, Python caches, `.paperwb` caches, `.idea`, or notebook checkpoints were reported as release-blocking errors.
- Data-safety audit warnings remain for historical reports containing machine-local absolute paths. These are documented as warnings, not silent failures.
- New v0.8 docs use relative `scratch/` output paths.
- No secrets, cloud API keys, LLM API calls, or publisher scraping dependencies were added.

## External-User Usability

The repository now has an external-user quickstart, installation instructions, a docs-site entry point, a report gallery, matrices for release coverage, and a runnable smoke workflow. A new user can validate synthetic examples, generate reports, use a project profile, run indexed search, audit files, import in dry-run mode, and export local artifacts without cloud access.

## Known Limitations

- Documentation remains Markdown-only; no generated HTML site is included.
- Historical reports still include some absolute local paths from earlier stages.
- The data-safety audit is heuristic and requires human review of warnings.
- CI does not execute notebooks by default; it performs static notebook checks.
- The project has not been published to PyPI.

## Verdict

v0.8 is suitable as a local external-user release candidate after final maintainer review. It is installable, testable, documented, and bounded by local-first safety rules.
