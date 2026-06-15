# Claim Lifecycle

v2.2 adds local review state for extracted claims. The source of truth for a
claim is still the user-written structured note; lifecycle state is stored in a
sidecar file such as `claim_lifecycle.json`.

## Statuses

- `newly_extracted`: parsed from notes but not reviewed.
- `needs_evidence_location`: missing a page or section pointer.
- `needs_rereading`: the paper or note should be checked again.
- `verified`: manually checked against the note.
- `ready_for_draft_use`: manually cleared for use in a draft.
- `used_in_draft`: manually marked as used in a draft.
- `deprecated`: should not be used unless reinstated.
- `contradicted`: part of a manual contradiction/tension review.
- `too_weak_to_use`: too weak, speculative, or low-confidence for confident use.

The tool does not auto-verify claims or decide scientific truth.

## Commands

```bash
paperwb claim-review queue --project zis_photocatalysis
paperwb claim-review mark PAPER_ID:c1 --project zis_photocatalysis --status verified
paperwb claim-review mark PAPER_ID:c2 --project zis_photocatalysis --status deprecated --reason "Superseded by rereading."
paperwb claim-review verified --project zis_photocatalysis
paperwb claim-review deprecated --project zis_photocatalysis
paperwb claim-review used-in-drafts --project zis_photocatalysis
```

`mark` writes only the lifecycle sidecar. It does not edit notes, registry rows,
or existing claim exports.
