# Behavior Preservation v2.6

Date: 2026-06-16

## Contracts Checked

- `paperwb --help` still loads the full CLI.
- Clean first-run project validation remains green:
  - `paperwb validate-registry projects/clean_demo/registry.csv --strict`
  - `paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict`
  - `paperwb dashboard --project clean_demo --no-audit-log`
- Incremental rebuild commands remain available:
  - `paperwb rebuild status --project zis_photocatalysis`
  - `paperwb rebuild plan --project zis_photocatalysis`
- Shared Markdown escaping preserves pipe and newline escaping in finding
  tables.
- Integrity report finding output keeps the existing severity/code/identifier/
  message/suggestion table shape.

## Test Coverage Added

- `tests/test_architecture_stabilization_v2_6.py`
  - Markdown cell escaping and table rendering.
  - Shared finding table rendering through an existing report.
  - Integrity report rendering through shared helpers.
  - Path containment and relative display behavior.

## Not Changed

- No registry, BibTeX, note, claim, theme, sync-plan, backup-manifest, or
  rebuild-metadata schema changes.
- No stable command contract changes.
- No new destructive behavior.
- No new dependency.

## Remaining Risk

The CLI remains large and should be split only after v3.0rc command contracts
are frozen. Many report modules still use local `_escape` helpers; migrating
them is safe only when paired with golden report checks for the affected output.

