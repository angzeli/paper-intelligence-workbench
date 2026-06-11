# Follow-up Actions

Follow-up actions come from two local sources:

- structured note `## Follow-up actions` sections
- user-supplied `paperwb reading finish --follow-up ...` flags

The tool does not invent follow-up actions.

## Commands

```bash
paperwb followups list --project zis_photocatalysis
paperwb followups list --project zis_photocatalysis --theme photocorrosion
paperwb followups export --project zis_photocatalysis --out scratch/followups.md --force
paperwb followups done note:zis_charge_2025:1 --project zis_photocatalysis
```

Marking an action done writes completion state to ignored local JSON. It does
not edit the source note or session record.

Default completion state path:

```text
.paperwb/followups_state.json
```

## Action IDs

Action IDs are deterministic enough for local use:

- `note:PAPER_ID:N`
- `session:SESSION_ID:N`

If the source note changes, note action numbering can change. For important
tasks, keep a stable wording in the note.

