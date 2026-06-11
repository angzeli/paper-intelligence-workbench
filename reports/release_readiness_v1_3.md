# Release Readiness v1.3

Date: 2026-06-11

## Verdict

v1.3 is usable as a local sync-planning layer for small literature-review
projects. It is intentionally conservative: it plans creates, blank-field
fills, and conflicts before writing, and it does not auto-merge notes or
overwrite non-empty registry metadata.

## Features Added

- `paper_workbench.sync` data model for sync sources, targets, plans, actions,
  conflicts, and apply reports.
- `paperwb sync plan` for local source-to-registry sync planning.
- `paperwb sync apply` for dry-run by default and safe forced registry applies.
- `paperwb sync conflicts` for standalone conflict reports.
- `paperwb sync plan-obsidian` for conservative Obsidian vault round-trip
  checks against local structured notes.
- Synthetic sync-conflict fixture at `data/examples/sync_conflict_zotero.csv`.
- Example script at `examples/sync_conflict_workflow.py`.

## Commands Checked

- `paperwb sync --help`
- `paperwb sync plan --project zis_photocatalysis --source data/examples/sync_conflict_zotero.csv --source-type zotero-csv`
- `paperwb sync conflicts scratch/v1_3/sync_plan_v1_3.json`
- `paperwb sync apply scratch/v1_3/sync_plan_v1_3.json --dry-run`
- `paperwb sync plan-obsidian --project zis_photocatalysis --vault scratch/v1_3/obsidian_zis_vault`

## Reports Generated

- `reports/sync_plan_v1_3.md`
- `reports/sync_conflicts_v1_3.md`
- `reports/sync_apply_dry_run_v1_3.md`
- `reports/obsidian_roundtrip_v1_3.md`
- `reports/release_readiness_v1_3.md`
- `reports/v1_4_recommended_patch_plan.md`

## Data Safety Assessment

- Sync sources are local files only.
- No cloud, Zotero cloud, LLM, publisher scraping, download, or remote metadata
  lookup is used.
- `sync apply` defaults to dry-run.
- Forced applies create a backup by default.
- Forced applies only create missing registry rows and fill blank fields.
- Non-empty registry conflicts and note conflicts remain manual-review items.

## Tests

Validation performed:

- Focused v1.3 sync tests passed.
- Command-contract and release-engineering metadata tests passed after adding
  the sync command and bumping package metadata.
- Full `pytest` suite passed.
- Package import check returned version `1.3.0`.
- `paperwb --help` and `paperwb sync --help` passed.
- Representative sync plan, conflict report, dry-run apply, and Obsidian
  round-trip CLI smoke checks passed.
- Notebook JSON structure check passed.
- Data-safety audit strict mode completed with 0 errors.

## Known Limitations

- v1.3 does not auto-resolve non-empty registry conflicts.
- Obsidian round-trip comparison is parse-based and conservative; exported
  files that are not in the structured note format may produce expected
  conflicts.
- There is no interactive conflict-resolution UI.
- Sync plans are not a stable external JSON schema yet.
- Forced apply writes the registry only; it does not update BibTeX or notes.

## Recommended v1.4 Scope

- Add optional user-authored field patch files for explicitly approved
  non-empty metadata changes.
- Add conflict grouping by DOI/title/BibTeX key.
- Add report diffs for sync plans.
- Add project-to-project sync planning.
- Keep all sync behavior local-first and non-destructive by default.
