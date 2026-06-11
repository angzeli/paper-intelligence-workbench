# Release Readiness v1.8

Date: 2026-06-11

## Verdict

v1.8 is ready as a focused architecture-cleanup release. It does not add major
user-facing features and preserves existing CLI behavior.

## Changes Made

- Centralized path display through `paper_workbench.paths.display_path`.
- Kept `paper_workbench.index.display_path` as a compatibility wrapper.
- Centralized theme ID normalization through `paper_workbench.tags.normalize_theme_id`.
- Hardened indexed-search rebuilds so duplicate local source keys produce
  deterministic internal record IDs rather than SQLite primary-key crashes.
- Updated API/CLI surface docs from v1.7 to v1.8 where the old release label
  would be inaccurate.
- Added architecture cleanup tests.
- Regenerated `reports/index.md`.

## Validation Run

- `python -m pytest -q`: passed, 240 tests.
- `python scripts/smoke_cli_workflow.py --quick --out <tmp>/paperwb_smoke_v1_8.md`: passed, 14 smoke steps.
- `python scripts/data_safety_audit.py --out <tmp>/paperwb_data_safety_v1_8.md --strict`: passed, 0 errors and 7 warnings.
- `python scripts/check_notebooks.py`: passed, 8 notebooks structurally checked.
- `python -m paper_workbench.cli --help`: passed.
- `python -m paper_workbench.cli template --help`: passed.
- `python -m paper_workbench.cli search photocorrosion --project zis_photocatalysis`: passed.
- `python -m paper_workbench.cli checklist --project zis_photocatalysis --theme charge_separation`: passed.
- `python -m paper_workbench.cli export report-index --out <tmp>/paperwb_report_index_v1_8.md --force`: passed.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`: passed and reported `1.8.0`.
- `git diff --check`: passed.
- `git ls-files "*.pdf" "*.sqlite" "*.db" ".paperwb/*" "*/.paperwb/*" "__pycache__/*" "*/__pycache__/*" ".pytest_cache/*" "build/*" "dist/*" "*.egg-info/*"`: passed with no tracked unsafe files.

## Backward Compatibility

- No CLI commands were added, removed, or renamed.
- Existing substring and indexed search report path rendering should remain
  equivalent.
- Theme matching accepts the same spelling variants while using one shared
  normalizer internally.
- Existing generated reports remain historical artifacts.
- Indexed search preserves user-facing paper IDs and citation keys while
  deduplicating only internal cache record IDs.

## Known Limitations

- `paper_workbench/cli.py` remains large and should be split only with stronger
  command-contract tests.
- Historical reports still include some data-safety absolute-path warnings.
- Docs still overlap across CLI reference, CLI surface, and command contracts.

## Recommended Next Maintenance

- Extract CLI command groups gradually.
- Add a focused docs de-duplication pass.
- Consider a common report output helper with overwrite/audit-log contract
  tests.
- Keep architecture cleanup releases small and behavior-preserving.
