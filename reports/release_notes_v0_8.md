# Release Notes v0.8

## Theme

v0.8 prepares Paper Intelligence Workbench for an external-user-quality local release. It does not publish the package, add cloud services, add LLM APIs, scrape publishers, or include copyrighted PDFs/full text.

## Added

- Hardened package metadata and version alignment for `0.8.0`.
- `CHANGELOG.md` and `CONTRIBUTING.md`.
- Installation documentation in `docs/INSTALLATION.md`.
- Docs-site Markdown source pages under `docs/`.
- External-user quickstart at `docs/EXTERNAL_USER_QUICKSTART.md`.
- Test, CLI behavior, report, and data-safety matrices.
- `scripts/smoke_cli_workflow.py` for a non-destructive synthetic CLI workflow.
- `scripts/check_notebooks.py` for static notebook JSON/path/title checks.
- `scripts/data_safety_audit.py` and `paper_workbench.safety` for tracked/unignored file safety audits.
- v0.8 release reports and v0.9 patch plan.

## Changed

- CI now runs notebook checks, CLI smoke workflow checks, local-file smoke checks, and data-safety audit checks.
- `.gitignore` now excludes common build artifacts and scratch/export output folders.
- README now links to v0.8 onboarding and release-engineering docs.
- Older walkthrough docs now use relative `scratch/` paths instead of machine-local temp paths.

## Safety Boundary

- Runtime dependencies remain empty.
- Smoke and audit scripts are local-only and require no secrets.
- The data-safety audit reports warnings for historical reports that contain machine-local paths; errors remain zero for release-blocking tracked artifacts.

## Not Included

- No package publishing.
- No documentation site generator dependency.
- No PDF metadata extraction.
- No cloud, LLM, scraping, OCR, or full-text ingestion changes.
