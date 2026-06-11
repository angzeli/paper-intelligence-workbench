# Release Readiness v0.10

## Summary

v0.10 is a quality-engineering release focused on adversarial fixtures, error quality, parser resilience, and regression lockdown.

## Added

- `paper_workbench/errors.py` shared taxonomy helpers.
- `tests/fixtures/adversarial/` synthetic torture fixtures.
- `tests/test_adversarial_v0_10.py` failure-path and parser robustness tests.
- Documentation for adversarial testing, error taxonomy, recovery, and CLI failure modes.
- v0.10 reports for adversarial coverage, taxonomy, and failure modes.

## Parser Robustness

- Registry validation now reports missing required CSV headers.
- Registry validation now catches relative `local_pdf_path` and `notes_path` values that escape the workspace.
- BibTeX torture fixtures verify conservative recovery from broken entries.
- Note torture fixtures verify warnings instead of crashes for malformed claim blocks.
- Generic CSV imports validate mapping targets and source columns before writes.
- Zotero CSV imports validate that the title column exists.
- Corrupted backup manifests now block restore with an actionable error.
- Corrupted audit-log lines are represented as parse-warning events while later valid events remain readable.

## CLI Failure Behavior

Representative failure-path commands return non-zero without Python tracebacks:

- bad generic CSV mapping
- missing project profile
- missing backup snapshot
- missing registry headers in strict mode

## Tests Run

- `python -m pytest tests/test_adversarial_v0_10.py -q`
- `python -m pytest -q`
- package import check
- `python -m paper_workbench.cli --help`
- representative failure-path CLI commands

## Remaining Risks

- BibTeX parsing remains intentionally lightweight and not a complete BibTeX implementation.
- CSV parsing cannot detect every malformed row shape when Python's CSV reader accepts it.
- Warning snapshots use structured assertions rather than exact full-output snapshots to avoid brittle path/timestamp churn.
- Existing historical reports still contain some legacy machine-local path warnings tracked by the data-safety audit.

## Release Verdict

v0.10 materially improves confidence for imperfect local user data. The project is still alpha, but common bad-input paths now have stronger tests and clearer recovery guidance.
