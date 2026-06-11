# Sync Conflicts

Plan ID: sync_zotero_csv_sync_conflict_zotero_to_registry_20260611T165940Z
Conflicts: 2

| Conflict ID | Type | Paper ID | Field | Risk | Registry value | Source value | Suggested action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C0001 | same_doi_different_title | zis_charge_2025 | title | high | Synthetic ZIS Charge Transfer Benchmark | Synthetic ZIS Charge Transfer Alternate Title | Verify whether one title is abbreviated, stale, or incorrect before applying. |
| C0002 | tag_mismatch | zis_charge_2025 | tags | medium | charge-separation; catalyst-stability | charge-separation; sync-conflict; imported-zotero | Review tags manually; the sync planner does not merge tag vocabularies automatically. |

## Recommended Review

- Resolve high-risk identifier conflicts before applying registry sync.
- Compare note conflicts manually; v1.3 does not auto-merge note text.
- Regenerate a new sync plan after manual edits.
