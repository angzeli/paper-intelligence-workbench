# Next Actions v1.6

| Priority | Action ID | Reason | Command | Related |
| --- | --- | --- | --- | --- |
| critical | `health:claim_missing_evidence_location:zis_stability_2024:c1` | Workspace health error: zis_stability_2024:c1 has no section/page evidence location. | `paperwb doctor --project zis_photocatalysis` | zis_stability_2024:c1 |
| medium | `citation:theme_only_review_statements:photocorrosion` | Citation audit warning: photocorrosion is supported only by review statements. | `paperwb report evidence-map --project zis_photocatalysis` | photocorrosion |
| medium | `citation:theme_too_few_papers:photocorrosion` | Citation audit warning: photocorrosion has evidence from 1 paper(s); target is 2. | `paperwb report evidence-map --project zis_photocatalysis` | photocorrosion |
| medium | `citation:theme_under_supported:photocorrosion` | Citation audit warning: photocorrosion has 1 supporting claim(s); target is 2. | `paperwb report evidence-map --project zis_photocatalysis` | photocorrosion |
| medium | `followup:note:zis_charge_2025:1` | Add verified notes from user-owned sources. | `paperwb followups list --project zis_photocatalysis` | zis_charge_2025 |
| medium | `followup:note:zis_stability_2024:1` | Add section/page before citing. | `paperwb followups list --project zis_photocatalysis` | zis_stability_2024 |
| medium | `weak_claim:zis_stability_2024:c1` | zis_stability_2024:c1 is weak/speculative or low-confidence. | `paperwb report weak-claims --project zis_photocatalysis` | zis_stability_2024:c1 |
| low | `maintenance:backup` | Create a local backup before major imports, sync applies, migrations, or restore tests. | `paperwb backup create --project zis_photocatalysis` | workspace |
| low | `read:zis_charge_2025` | Read next: Synthetic ZIS Charge Transfer Benchmark (reading_priority=critical; priority=high; supports weak theme photocorrosion). | `paperwb reading start zis_charge_2025 --project zis_photocatalysis` | zis_charge_2025 |
| low | `read:zis_stability_2024` | Read next: Synthetic ZIS Stability Screening Memo (reading_priority=high; priority=medium; supports weak theme photocorrosion). | `paperwb reading start zis_stability_2024 --project zis_photocatalysis` | zis_stability_2024 |
