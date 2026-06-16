# Release Readiness v3.2

## Verdict

Ready for local dogfooding as a compatibility-focused patch.

v3.2 adds read-only compatibility inspection, a documented compatibility matrix,
historical synthetic workspace fixtures, and migration torture coverage. It does
not change the existing copy-based legacy migration behavior.

## Features Added

- `paperwb compatibility inspect WORKSPACE`
- `paperwb compatibility report WORKSPACE`
- `paperwb compatibility matrix`
- Synthetic historical workspace fixture library under
  `tests/fixtures/workspaces/`
- Compatibility reports for legacy migration, partial migration conflicts, and
  extra-column registry preservation
- Documentation for backward compatibility, schema evolution, legacy
  workspaces, and v3 migration workflow

## Safety Assessment

- Compatibility inspection is read-only except explicit `--out` report writes.
- Migration tests operate on synthetic fixtures or temporary copies only.
- Legacy migration remains copy-based and does not delete source files.
- Extra user registry columns are reported and preserved by copy-based
  migration.
- Project-profile paths that escape a project root are reported as errors.
- No PDFs, copied paper text, real paper metadata, cloud APIs, LLM APIs, or
  publisher scraping were added.

## Commands Checked

- `paperwb compatibility --help`
- `paperwb compatibility inspect tests/fixtures/workspaces/v0_1_legacy_data`
- `paperwb compatibility inspect tests/fixtures/workspaces/path_traversal_workspace --strict`
- `paperwb compatibility matrix --out reports/compatibility_matrix_v3_2.md --force`
- `paperwb migrate run --root tests/fixtures/workspaces/v0_1_legacy_data --to-project migrated_review --dry-run --out reports/legacy_migration_dry_run_v3_2.md --force-report`

## Tests Added

- Historical fixture inspection tests
- Malformed workspace diagnostics
- Path traversal detection
- Partial migration conflict detection
- Dry-run and forced migration on copied synthetic fixtures
- Extra registry column preservation
- CLI smoke tests for `compatibility inspect`, `compatibility report`, and
  `compatibility matrix`

## Known Limitations

- The compatibility inspector estimates workspace generation from layout
  signals; it does not prove exact historical version provenance.
- Existing migration support is still legacy `data/` to project profile only.
- Broken notes are reported but not repaired.
- Experimental sidecars remain outside the stable compatibility guarantee.

## Recommended Follow-up

- Run the compatibility workflow on one real private dogfood workspace without
  committing outputs.
- Keep adding historical fixtures when schemas or migration behavior change.
- Defer broader migration automation until real compatibility reports show a
  repeated need.

