# Report Gallery

Reports are Markdown artifacts generated from local data. They answer planning
questions for the user; they are not stable machine APIs and they do not judge
scientific truth.

## Core Reports

| Report | What it answers | Command | Inputs | Output | Limitations |
| --- | --- | --- | --- | --- | --- |
| Inventory | Which papers are in the project? | `paperwb report inventory --project clean_demo --out scratch/inventory.md --force` | Registry | Markdown | Metadata quality depends on registry rows. |
| Reading status | What has been read, skimmed, or left unread? | `paperwb report reading-status --project clean_demo --out scratch/reading_status.md --force` | Registry | Markdown | Does not verify that a paper was actually read. |
| BibTeX audit | Are citation keys linked and valid locally? | `paperwb report bibtex-audit --project clean_demo --out scratch/bibtex_audit.md --force` | Registry, BibTeX | Markdown | BibTeX metadata is advisory. |
| Evidence map | Which themes have claims and evidence locations? | `paperwb report evidence-map --project clean_demo --out scratch/evidence_map.md --force` | Registry, notes, claims, themes | Markdown | Based only on user-entered claims. |
| Citation audit | Which papers are citation-ready? | `paperwb report citation-audit --project clean_demo --out scratch/citation_audit.md --force` | Registry, BibTeX, notes, claims | Markdown | Does not validate scientific truth. |
| Missing notes | Which included papers lack notes? | `paperwb report missing-notes --project clean_demo --out scratch/missing_notes.md --force` | Registry, notes | Markdown | Empty notes may still need manual review. |
| Weak claims | Which claims are low confidence or weakly supported? | `paperwb report weak-claims --project clean_demo --out scratch/weak_claims.md --force` | Claims | Markdown | Strength labels are user/local metadata. |
| Missing evidence | Which claims lack locations or evidence details? | `paperwb report missing-evidence --project clean_demo --out scratch/missing_evidence.md --force` | Claims | Markdown | Does not fetch missing evidence. |
| Dashboard | What should I do next? | `paperwb dashboard --project clean_demo --out scratch/dashboard.md --force --no-audit-log` | Project profile | Markdown or terminal | Read-only suggestions only. |

## Writing And QA Reports

| Report | What it answers | Command | Limitations |
| --- | --- | --- | --- |
| Writing packet | What local evidence supports this theme? | `paperwb writing-packet --project clean_demo --theme clean-theme --out scratch/writing_packet.md --force` | Planning aid only; not final prose. |
| Draft audit | Which draft paragraphs need citation/evidence review? | `paperwb draft audit drafts/synthetic_good_section.md --project clean_demo --out scratch/draft_audit.md --force` | Heuristic matching. |
| Manuscript QA | What would a reviewer flag in this draft? | `paperwb manuscript qa drafts/synthetic_good_section.md --project clean_demo --out scratch/manuscript_qa.md --force` | Does not judge truth or rewrite prose. |
| Claim traceability | Which tracked claims are used in a draft? | `paperwb manuscript trace-claims drafts/synthetic_good_section.md --project clean_demo --out scratch/trace.md --force` | Depends on local matching and citation keys. |

## Safety And Operations Reports

| Report | What it answers | Command | Limitations |
| --- | --- | --- | --- |
| Integrity | Is the workspace internally consistent? | `paperwb integrity check --project clean_demo --out scratch/integrity.md --force` | Does not repair data by itself. |
| Compatibility | What kind of workspace is this? | `paperwb compatibility report tests/fixtures/workspaces/v0_1_legacy_data --out scratch/compatibility.md --force` | Version detection is heuristic. |
| Support bundle | What sanitized diagnostics can be shared? | `paperwb support bundle --project clean_demo --out scratch/support_bundle` | Safe mode redacts content by default. |
| Rebuild plan | What generated state is stale? | `paperwb rebuild plan --project clean_demo --out scratch/rebuild_plan.md --force-report` | Cache metadata is rebuildable and experimental. |
| Rule report | Which declarative local rules fire? | `paperwb rules report --project clean_demo --out scratch/rules.md --force` | Rule coverage depends on local config. |

## Import, Sync, And Collaboration Reports

| Report | What it answers | Command | Limitations |
| --- | --- | --- | --- |
| Import dry-run | What would an import change? | `paperwb import zotero-csv data/examples/zotero_export.csv --project clean_demo --dry-run --report scratch/import.md --force` | Review before applying. |
| Sync plan | What creates, updates, skips, or conflicts are proposed? | `paperwb sync plan --source data/examples/zotero_export.csv --source-type zotero-csv --project clean_demo --out scratch/sync.md --json-out scratch/sync.json --force` | Apply remains safety-sensitive. |
| Review packet | What should a collaborator review? | `paperwb review-packet create --project clean_demo --theme clean-theme --out scratch/review_packet --force` | Experimental; verify packet has items. |
| Response to review | Which reviewer comments need action? | `paperwb review-packet import-comments scratch/review_packet/comments.csv --project clean_demo --dry-run` | Comments are advisory, not evidence changes. |

## Current Generated Reports

Use [reports/index.md](../../reports/index.md) for the generated report
inventory. The v3.4 docs patch creates:

- `reports/docs_audit_v3_4.md`
- `reports/cookbook_inventory_v3_4.md`
- `reports/command_reference_audit_v3_4.md`
- `reports/release_readiness_v3_4.md`
- `reports/v3_5_recommended_patch_plan.md`
