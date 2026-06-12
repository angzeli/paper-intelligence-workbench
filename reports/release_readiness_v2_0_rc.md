# Release Readiness v2.0rc

Version: `2.0.0rc1`

## Release Verdict

Ready for local dogfooding as a v2.0 release candidate.

## What Changed For v2.0rc

- Package metadata moved to `2.0.0rc1`.
- v2 stable, experimental, deprecated, schema, migration, compatibility,
  command-contract, workflow, report, safety, limitation, roadmap, and test
  documentation was added.
- v2 release reports were generated to summarize migration readiness, report
  inventory, data safety, notebook/example validation, test coverage, and
  external-user simulation.

## Blockers

- None currently known.

## High-Priority Issues

- None found during v2.0rc validation.

## Medium-Priority Issues

- The repository has many historical reports from the long v1.x burn cycle.
  They are useful context but should be trimmed or archived before a public
  release branch is presented to external users.
- Some experimental command groups are intentionally broad. They should remain
  marked experimental until real-user workflows prove the interfaces.

## Validation Status

- Editable install in a temporary virtual environment: passed.
- Package import/version check: `2.0.0rc1`.
- `paperwb --help`: passed.
- CLI smoke workflow: 14 steps passed.
- Current-environment clean-room check: 7 steps passed.
- Notebook validation: 8 notebooks checked.
- Data-safety audit: 597 tracked files checked, 0 errors, 8 warnings.
- External-user temp workspace simulation: passed with expected empty-template
  warnings.
- Legacy migration plan and dry-run: passed.
- Backup create/list/inspect/restore dry-run on a synthetic project: passed.
- Full test suite: 244 tests passed.

## Commands Checked

- `paperwb --help`
- `paperwb init`
- `paperwb template list`
- `paperwb template inspect photocatalysis`
- `paperwb template create photocatalysis --project <project> --root <tmp>`
- `paperwb project list`
- `paperwb project validate <project>`
- `paperwb validate-registry data/registries/example_papers.csv`
- `paperwb validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv`
- `paperwb note-template synth_charge_2024 ...`
- `paperwb claims data/notes ...`
- `paperwb report evidence-map ...`
- `paperwb report citation-audit ...`
- `paperwb dashboard --project zis_photocatalysis ...`
- `paperwb rules run --project zis_photocatalysis`
- `paperwb import zotero-csv ... --dry-run`
- `paperwb export registry-json ...`
- `paperwb export reading-list ...`
- `paperwb index rebuild ...`
- `paperwb search ... --indexed`
- `paperwb draft audit ...`
- `paperwb manuscript qa ...`
- `paperwb writing-packet ...`
- `paperwb reading queue ...`
- `paperwb followups list ...`
- `paperwb sync plan ...`
- `paperwb sync apply ... --dry-run`
- `paperwb files audit ...`
- `paperwb integrity check ...`
- `paperwb backup create/list/inspect/plan-restore/restore --dry-run`
- `paperwb migrate plan`
- `paperwb migrate run --dry-run`

## Data Safety

The release candidate remains local-first. Cache/index files, audit logs,
backups, exports, scratch outputs, PDFs, and Python caches are ignored and must
not be staged.

## Tagging Status

No tag has been created. This repository is not published.

## Recommendation

Do not expand the feature set before tagging. The next step should be a final
maintainer review of the v2 docs, reports, and git diff, then tag locally only
when explicitly approved.
