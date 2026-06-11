# Sync Plan

- Plan ID: sync_zotero_csv_sync_conflict_zotero_to_registry_20260611T171848Z
- Project: zis_photocatalysis
- Source: zotero-csv (data/examples/sync_conflict_zotero.csv)
- Target: registry (projects/zis_photocatalysis/registry.csv)
- Dry run: true
- Actions: 1
- Conflicts: 1

## Action Summary

- create_paper: 1

## Conflict Summary

- same_doi_different_title: 1

## Actions

| Action ID | Type | Paper ID | Field | Risk | Requires force | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| A0001 | create_paper | synthetic_2026_synthetic_sync_planning |  | low | true | Imported record does not match an existing registry row by paper_id, DOI, title, or BibTeX key. |

## Conflicts

| Conflict ID | Type | Paper ID | Field | Risk | Registry value | Source value | Suggested action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C0001 | same_doi_different_title | zis_charge_2025 | title | high | Synthetic ZIS Charge Transfer Benchmark | Synthetic ZIS Charge Transfer Alternate Title | Verify whether one title is abbreviated, stale, or incorrect before applying. |

## Warnings

- Suppressed registry updates for zis_charge_2025 because the imported record has a high-risk identity conflict.

## Safety Boundary

This plan is local and non-destructive until applied. Real registry applies are refused for high-risk conflicts or stale source/registry files. v1.3 does not auto-merge note conflicts or overwrite non-empty registry fields.
