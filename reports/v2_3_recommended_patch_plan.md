# v2.3 Recommended Patch Plan

## Recommended Scope

- Dogfood claim lifecycle sidecars on a real photocatalysis project with manual
  notes.
- Add a lifecycle schema audit report if real use shows sidecar drift or stale
  claim IDs.
- Improve draft-used claim tracking after manuscript QA has stable paragraph and
  claim occurrence IDs.
- Add small report filters for deprecated, contradicted, and reread-needed
  claims by theme.
- Review dashboard next-action noise from claim-review queue items.

## Do Not Expand Yet

- Do not auto-verify claims.
- Do not infer semantic contradictions with LLMs or embeddings.
- Do not rewrite notes or claim text from lifecycle commands.
- Do not treat contradiction groups as scientific truth judgments.
- Do not add a database-backed lifecycle store before sidecar workflows have
  been dogfooded.

## Validation Needed Before v2.3

- Run claim review on a real project with 10-15 manually entered papers.
- Confirm deprecated and verified reports help writing decisions.
- Compare contradiction group reports with manual reviewer expectations.
- Check that manuscript QA warnings remain helpful when lifecycle sidecars are
  present.
