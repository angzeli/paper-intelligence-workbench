# Release Readiness v2.6

Release label: v2.6  
Package metadata: 2.6

## Verdict

Ready for local dogfooding as a maintainability stabilization patch, assuming
the full test suite and representative CLI smoke checks pass.

## Stabilization Work Completed

- Clarified internal architecture and module boundaries.
- Added shared internal Markdown report helpers.
- Added shared path containment and relative-display helpers.
- Added a shared `ValidationFinding` factory.
- Migrated low-risk reporting and integrity call sites.
- Added behavior-preservation tests for helper behavior and report output shape.

## Stable Behavior Preserved

- No public CLI command names or flags changed.
- No parser behavior changed.
- No data schema changed.
- No import/export/sync/backup/migration write behavior changed.
- No heavy dependencies were added.

## Commands To Check

- `python -m pytest -q`
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`
- `paperwb --help`
- `paperwb validate-registry projects/clean_demo/registry.csv --strict`
- `paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict`
- `paperwb dashboard --project clean_demo --no-audit-log`
- `paperwb rebuild plan --project zis_photocatalysis`
- `paperwb workflow list`

## Known Limitations

- `paper_workbench/cli.py` is still oversized.
- Many report modules still have local Markdown escaping helpers.
- Domain-specific finding objects remain intentionally separate.
- Historical reports and overlapping docs remain noisy.

## Recommended v3.0rc Scope

- Freeze stable versus experimental command groups.
- Freeze v3 schema references.
- Decide whether to split `cli.py` after command-contract tests are current.
- Keep workflow runner, review packets, evidence graph, claim lifecycle, sync
  apply, indexed search, and rebuild metadata experimental unless dogfooding
  proves the contracts.

