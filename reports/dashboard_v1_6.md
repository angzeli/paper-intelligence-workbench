# Terminal Dashboard v1.6

This dashboard summarizes local project state only. It does not modify user data, use cloud services, or infer paper content.

Project: zis_photocatalysis
Root: `projects/zis_photocatalysis`
Projects discovered: 6

## Summary

| Metric | Count |
| --- | ---: |
| Papers | 2 |
| Notes | 2 |
| Claims | 2 |
| BibTeX entries | 2 |
| Themes | 2 |
| Missing parsed notes | 0 |
| Weak/low-confidence claims | 1 |
| Claims missing evidence locations | 1 |

## Reading Status

| Status | Papers |
| --- | ---: |
| deeply_read | 1 |
| read | 1 |

## Issue Counts

| Source | Errors | Warnings | Info |
| --- | ---: | ---: | ---: |
| BibTeX | 0 | 1 | 0 |
| Citation audit | 1 | 6 | 0 |
| Workspace health | 1 | 4 | 0 |
| Rules | 8 | 16 | 0 |
| Manuscript QA | 4 | 2 | 0 |

## Next Actions

| Priority | Action ID | Reason | Command | Related |
| --- | --- | --- | --- | --- |
| critical | `health:claim_missing_evidence_location:zis_stability_2024:c1` | Workspace health error: zis_stability_2024:c1 has no section/page evidence location. | `paperwb doctor --project zis_photocatalysis` | zis_stability_2024:c1 |
| high | `missing_evidence:zis_stability_2024:c1` | zis_stability_2024:c1 has no section/page evidence location. | `paperwb report citation-audit --project zis_photocatalysis` | zis_stability_2024:c1 |
| high | `rule:builtin.citation_audit.claim_missing_evidence_location:zis_stability_2024:c1` | Rule violation: zis_stability_2024:c1 has no section or page evidence location. | `paperwb rules report --project zis_photocatalysis` | zis_stability_2024:c1 |
| high | `rule:builtin.manuscript.citation_key_not_in_bibtex:unknownSynthetic2027` | Rule violation: Citation key unknownSynthetic2027 is not present in the BibTeX library. | `paperwb rules report --project zis_photocatalysis` | unknownSynthetic2027 |
| high | `rule:builtin.workspace_health.claim_missing_evidence_location:zis_stability_2024:c1` | Rule violation: zis_stability_2024:c1 has no section/page evidence location. | `paperwb rules report --project zis_photocatalysis` | zis_stability_2024:c1 |
| medium | `citation:theme_only_review_statements:photocorrosion` | Citation audit warning: photocorrosion is supported only by review statements. | `paperwb report evidence-map --project zis_photocatalysis` | photocorrosion |
| medium | `citation:theme_too_few_papers:photocorrosion` | Citation audit warning: photocorrosion has evidence from 1 paper(s); target is 2. | `paperwb report evidence-map --project zis_photocatalysis` | photocorrosion |
| medium | `citation:theme_under_supported:photocorrosion` | Citation audit warning: photocorrosion has 1 supporting claim(s); target is 2. | `paperwb report evidence-map --project zis_photocatalysis` | photocorrosion |
| medium | `followup:note:zis_charge_2025:1` | Add verified notes from user-owned sources. | `paperwb followups list --project zis_photocatalysis` | zis_charge_2025 |
| medium | `followup:note:zis_stability_2024:1` | Add section/page before citing. | `paperwb followups list --project zis_photocatalysis` | zis_stability_2024 |

## Reading Queue

| Rank | Score | Paper ID | Status | Title | Reasons |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 138 | zis_charge_2025 | deeply_read | Synthetic ZIS Charge Transfer Benchmark | reading_priority=critical; priority=high; supports weak theme photocorrosion; has added_date |
| 2 | 93 | zis_stability_2024 | read | Synthetic ZIS Stability Screening Memo | reading_priority=high; priority=medium; supports weak theme photocorrosion; has added_date |

## Open Follow-ups

| Action ID | Paper ID | Theme | Action |
| --- | --- | --- | --- |
| `note:zis_charge_2025:1` | zis_charge_2025 | charge-separation | Add verified notes from user-owned sources. |
| `note:zis_stability_2024:1` | zis_stability_2024 | photocorrosion | Add section/page before citing. |

## Recent Audit Events

| Timestamp | Action | Success | Summary |
| --- | --- | --- | --- |
| 2026-06-11T20:15:53.698703+00:00 | write_index_status_report | True | Wrote index status report |
| 2026-06-11T20:15:53.699428+00:00 | rebuild_index | True | Rebuilt 15 index records |
| 2026-06-11T20:15:53.991058+00:00 | clear_index | True | Cleared index records for zis_photocatalysis |
| 2026-06-11T20:15:55.740061+00:00 | write_manuscript_citation_coverage | True | Audited manuscript citations in drafts/synthetic_overconfident_section.md |
| 2026-06-11T20:15:55.811966+00:00 | write_manuscript_qa | True | Audited manuscript drafts/synthetic_overconfident_section.md; verdict=needs evidence strengthening |
| 2026-06-11T20:15:55.885801+00:00 | write_manuscript_revision_checklist | True | Wrote manuscript checklist for drafts/synthetic_overconfident_section.md |
| 2026-06-11T20:15:55.957814+00:00 | write_manuscript_context_table | True | Wrote citation context table for drafts/synthetic_overconfident_section.md |
| 2026-06-11T20:15:56.046333+00:00 | write_manuscript_paragraph_evidence | True | Wrote manuscript paragraph evidence table for drafts/synthetic_overconfident_section.md |
| 2026-06-11T20:15:56.129325+00:00 | write_claim_traceability | True | Wrote claim traceability for drafts/synthetic_overconfident_section.md |
| 2026-06-11T20:15:58.391961+00:00 | write_rule_report | True | Wrote rule report with 2 findings |

## Generated Reports

- `reports/bibtex_audit.md`
- `reports/citation_audit.md`
- `reports/claims_by_theme.md`
- `reports/evidence_map.md`
- `reports/inventory.md`
- `reports/missing_evidence.md`
- `reports/missing_notes.md`
- `reports/papers_by_tag.md`
- `reports/photocorrosion_section_outline.md`
- `reports/reading_status.md`
- `reports/theme_dashboard.md`
- `reports/weak_claims.md`
- `reports/workspace_health.md`
