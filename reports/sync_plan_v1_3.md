# Sync Plan

- Plan ID: sync_zotero_csv_sync_conflict_zotero_to_registry_20260611T165940Z
- Project: zis_photocatalysis
- Source: zotero-csv (data/examples/sync_conflict_zotero.csv)
- Target: registry (projects/zis_photocatalysis/registry.csv)
- Dry run: true
- Actions: 1
- Conflicts: 2

## Action Summary

- create_paper: 1

## Conflict Summary

- same_doi_different_title: 1
- tag_mismatch: 1

## Actions

| Action ID | Type | Paper ID | Field | Risk | Requires force | Reason |
| --- | --- | --- | --- | --- | --- | --- |
| A0001 | create_paper | synthetic_2026_synthetic_sync_planning |  | low | true | Imported record does not match an existing registry row by paper_id, DOI, title, or BibTeX key. |

## Conflicts

| Conflict ID | Type | Paper ID | Field | Risk | Registry value | Source value | Suggested action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C0001 | same_doi_different_title | zis_charge_2025 | title | high | Synthetic ZIS Charge Transfer Benchmark | Synthetic ZIS Charge Transfer Alternate Title | Verify whether one title is abbreviated, stale, or incorrect before applying. |
| C0002 | tag_mismatch | zis_charge_2025 | tags | medium | charge-separation; catalyst-stability | charge-separation; sync-conflict; imported-zotero | Review tags manually; the sync planner does not merge tag vocabularies automatically. |

## Safety Boundary

This plan is local and non-destructive until applied. v1.3 does not auto-merge note conflicts or overwrite non-empty registry fields.
