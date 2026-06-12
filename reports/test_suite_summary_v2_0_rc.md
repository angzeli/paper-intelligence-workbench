# Test Suite Summary v2.0rc

## Coverage Areas

- Unit and parser tests.
- CLI smoke and command-contract tests.
- Registry and BibTeX validation.
- Notes, claims, tags, search, reports, and citation audits.
- Project profiles, templates, and dashboard.
- Import/export, sync, search index, local files, backup, migration, integrity,
  rule engine, reading sessions, draft/manuscript QA, adversarial fixtures, and
  release hygiene.

## Validation Status

- `python -m pytest -q`: passed.
- `python -m pytest --collect-only -q`: collected 244 tests.
- Targeted v2 release-candidate tests passed after narrowing a report-sanitizing
  assertion so documented regex patterns are not treated as actual local paths.

## v2 Additions

- `tests/test_v2_release_candidate.py` verifies version metadata, v2 docs,
  v2 release reports, report index entries, and stable command help.
- Release-hygiene tests were adjusted so ignored local egg-info files do not
  fail the suite unless they are tracked.

## Known Test Boundaries

- Notebooks are structurally validated by default rather than fully executed.
- Generated report regression checks assert stable sections and key findings,
  not every byte of every report.
- Synthetic stress fixtures intentionally contain validation findings.
