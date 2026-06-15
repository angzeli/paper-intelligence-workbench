# Release Readiness v2.2

Release label: `v2.2`

## Features Added

- Claim lifecycle model with explicit local statuses such as `verified`,
  `needs_evidence_location`, `needs_rereading`, `deprecated`, `contradicted`,
  and `too_weak_to_use`.
- Project-local sidecar workflow for `claim_lifecycle.json` and
  `contradictions.json`.
- `paperwb claim-review` queue, mark, verified, deprecated, and used-in-drafts
  commands.
- `paperwb contradictions` create, add, and report commands for manual
  contradiction/tension review groups.
- Lifecycle warnings in writing packets and draft/manuscript evidence audits
  when lifecycle state is supplied.
- Dashboard next-action integration for claim review queues.
- Evidence graph claim-node metadata for lifecycle state when a sidecar is
  supplied.

## Commands Checked

```bash
python -m paper_workbench.cli claim-review --help
python -m paper_workbench.cli contradictions --help
python -m paper_workbench.cli claim-review queue --project zis_photocatalysis --limit 3
pytest tests/test_claim_lifecycle_v2_2.py -q
```

## Reports Generated

- `reports/claim_review_queue_v2_2.md`
- `reports/verified_claims_v2_2.md`
- `reports/deprecated_claims_v2_2.md`
- `reports/contradictions_v2_2.md`
- `reports/claims_used_in_drafts_v2_2.md`
- `reports/release_readiness_v2_2.md`
- `reports/v2_3_recommended_patch_plan.md`

## Data Safety

- No PDFs are copied, read, or parsed.
- No paper metadata, claims, counterclaims, or scientific conclusions are
  fabricated.
- Claim lifecycle state is explicit local review metadata and does not mutate
  source notes.
- Existing claim CSV exports remain unchanged.
- Contradiction groups are manual review aids, not automatic scientific
  findings.

## Known Limitations

- Sidecar schemas are experimental and should be dogfooded before stabilization.
- Contradiction suggestions are simple tag-based possible tensions only.
- Draft-used claim state is explicit user metadata, not inferred from every
  manuscript audit.
- Lifecycle integration in reports is intentionally warning-oriented and does
  not block output generation.

## Verdict

Ready for local dogfooding as an experimental v2.2 evidence-review workflow.
Do not mark lifecycle sidecar schemas stable until they have been used on real
notes and reviewed for false-positive queue noise.
