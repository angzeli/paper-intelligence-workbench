# Sync Plan

- Plan ID: sync_obsidian_vault_obsidian_zis_vault_to_notes_20260611T165940Z
- Project: zis_photocatalysis
- Source: obsidian-vault (scratch/v1_3/obsidian_zis_vault)
- Target: notes (projects/zis_photocatalysis/notes)
- Dry run: true
- Actions: 0
- Conflicts: 8

## Action Summary

- None.

## Conflict Summary

- local_note_differs_from_exported_note: 8

## Actions

| Action ID | Type | Paper ID | Field | Risk | Requires force | Reason |
| --- | --- | --- | --- | --- | --- | --- |
|  | none |  |  |  | false | No actions planned. |

## Conflicts

| Conflict ID | Type | Paper ID | Field | Risk | Registry value | Source value | Suggested action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C0001 | local_note_differs_from_exported_note | zis_charge_2025 | claim_count | medium | 1 | 0 | Review both Markdown files manually; v1.3 does not auto-merge note content. |
| C0002 | local_note_differs_from_exported_note | zis_charge_2025 | claim_texts | medium | The synthetic ZIS benchmark records stronger charge transfer for the treated variant. |  | Review both Markdown files manually; v1.3 does not auto-merge note content. |
| C0003 | local_note_differs_from_exported_note | zis_charge_2025 | follow_up_actions | medium | Add verified notes from user-owned sources. |  | Review both Markdown files manually; v1.3 does not auto-merge note content. |
| C0004 | local_note_differs_from_exported_note | zis_charge_2025 | personal_reading_notes | medium | Synthetic local-only note. |  | Review both Markdown files manually; v1.3 does not auto-merge note content. |
| C0005 | local_note_differs_from_exported_note | zis_stability_2024 | claim_count | medium | 1 | 0 | Review both Markdown files manually; v1.3 does not auto-merge note content. |
| C0006 | local_note_differs_from_exported_note | zis_stability_2024 | claim_texts | medium | The memo suggests photocorrosion risk may increase under unstable synthetic screening conditions. |  | Review both Markdown files manually; v1.3 does not auto-merge note content. |
| C0007 | local_note_differs_from_exported_note | zis_stability_2024 | follow_up_actions | medium | Add section/page before citing. |  | Review both Markdown files manually; v1.3 does not auto-merge note content. |
| C0008 | local_note_differs_from_exported_note | zis_stability_2024 | personal_reading_notes | medium | Keep as an audit fixture. |  | Review both Markdown files manually; v1.3 does not auto-merge note content. |

## Safety Boundary

This plan is local and non-destructive until applied. v1.3 does not auto-merge note conflicts or overwrite non-empty registry fields.
