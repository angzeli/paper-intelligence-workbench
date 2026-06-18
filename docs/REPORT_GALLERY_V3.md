# Report Gallery v3

Reports are generated Markdown artifacts for human review. They are not stable
machine APIs and they do not judge scientific truth.

For the full v3.5 gallery, use [docs/reports/index.md](reports/index.md).

## Stable Core Reports

| Report | Command | What it answers |
| --- | --- | --- |
| Inventory | `paperwb report inventory` | Which papers are tracked? |
| Reading status | `paperwb report reading-status` | Which papers are unread, skimmed, or read? |
| BibTeX audit | `paperwb report bibtex-audit` | Are citation keys and BibTeX entries linked locally? |
| Evidence map | `paperwb report evidence-map` | Which claims support each theme? |
| Citation audit | `paperwb report citation-audit` | Which cited papers have registry, BibTeX, note, claim, and evidence coverage? |
| Missing notes | `paperwb report missing-notes` | Which papers need notes? |
| Weak claims | `paperwb report weak-claims` | Which claims look under-supported from local metadata? |
| Missing evidence | `paperwb report missing-evidence` | Which claims lack evidence locations? |
| Dashboard | `paperwb dashboard --out` | What are the next local actions? |

## Experimental Reports

- Draft and manuscript QA reports.
- Evidence graph summaries and JSON/DOT exports.
- Claim lifecycle queues and contradiction reports.
- Workflow run reports.
- Review packet and response-to-review reports.
- Sync plans and conflict reports.
- Incremental rebuild plans.
- Sanitized support bundles.
- Compatibility and migration dry-run reports.

## How To Interpret Reports

- Treat every warning as a prompt for manual review.
- Do not treat heuristic manuscript, graph, rule, or claim-lifecycle findings as
  scientific truth.
- Prefer `scratch/` or project-local `reports/` for generated outputs.
- Use `--force` only when you intend to replace an existing generated report.

## Current Release Reports

Use [reports/index.md](../reports/index.md) for the generated report inventory.
The v3.5 docs set includes:

- `reports/docs_audit_v3_4.md`
- `reports/cookbook_inventory_v3_4.md`
- `reports/command_reference_audit_v3_4.md`
- `reports/release_readiness_v3_4.md`
- `reports/v3_5_recommended_patch_plan.md`
