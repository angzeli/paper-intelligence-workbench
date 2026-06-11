# Rule Report v1.5

This report combines built-in validation adapters with optional project-specific declarative rules.
It audits local metadata and evidence tracking only; it does not modify files or judge scientific truth.

Project: zis_photocatalysis
Rule file: `projects/zis_photocatalysis/rules.json`
Configured rules: 4
Built-in adapter findings: 14
Configured rule findings: 2
Total findings: 16

## Findings

| Severity | Rule ID | Target | Identifier | Message | Suggested action |
| --- | --- | --- | --- | --- | --- |
| error | builtin.citation_audit.claim_missing_evidence_location | claim | zis_stability_2024:c1 | zis_stability_2024:c1 has no section or page evidence location. | Add section, page, figure, table, or appendix location. |
| warning | builtin.citation_audit.low_confidence_claim | claim | zis_stability_2024:c1 | zis_stability_2024:c1 is marked low confidence or weak. | Re-read the evidence before using this claim as core support. |
| warning | builtin.citation_audit.theme_under_supported | registry | photocorrosion | photocorrosion has 1 supporting claim(s); target is 2. | Add more verified claims or lower the theme's stated coverage expectations. |
| warning | builtin.citation_audit.theme_too_few_papers | registry | photocorrosion | photocorrosion has evidence from 1 paper(s); target is 2. | Add more papers with verified claims for this theme. |
| warning | builtin.citation_audit.theme_only_review_statements | registry | photocorrosion | photocorrosion is supported only by review statements. | Look for direct experimental, methodological, or theoretical evidence. |
| warning | builtin.citation_audit.included_paper_with_weak_evidence | registry | zis_stability_2024 | zis_stability_2024 is included in the literature review but has weak/speculative evidence. | Re-read or add stronger evidence before relying on this paper. |
| warning | builtin.citation_audit.paper_theme_without_claim | registry | zis_charge_2025 | zis_charge_2025 is tagged for theme photocorrosion but has no clear supporting claim. | Add a claim block or remove the theme tag if the paper is not evidence. |
| warning | builtin.evidence_map.theme_min_claims | theme | photocorrosion | photocorrosion has 1 claim(s); target is 2. | Add verified claim blocks or lower the theme threshold. |
| warning | builtin.evidence_map.theme_min_papers | theme | photocorrosion | photocorrosion has evidence from 1 paper(s); target is 2. | Add evidence from more papers or lower the theme threshold. |
| warning | builtin.workspace_health.note_parse_warning | workspace | zis_stability_2024 | zis_stability_2024.md: Claim A is missing evidence location. | Review the note against the structured note format. |
| warning | builtin.workspace_health.suspiciously_incomplete | workspace | zisStability2024 | zisStability2024 looks sparse. | Review the entry for missing author, venue, DOI, or URL fields. |
| warning | builtin.workspace_health.theme_under_supported | workspace | photocorrosion | photocorrosion has 1 supporting claim(s); target is 2. | Add more verified claims or adjust the theme threshold. |
| warning | builtin.workspace_health.theme_too_few_papers | workspace | photocorrosion | photocorrosion has evidence from 1 paper(s); target is 2. | Add evidence from more papers or adjust the theme threshold. |
| error | builtin.workspace_health.claim_missing_evidence_location | workspace | zis_stability_2024:c1 | zis_stability_2024:c1 has no section/page evidence location. | Add a section, page, figure, table, or appendix location. |
| warning | zis.theme.photocorrosion.min_papers | theme | photocorrosion | Theme photocorrosion has 1 supporting paper(s); project target is 3. | Add more user-verified notes and claims before treating this theme as review-ready. |
| warning | zis.theme.photocorrosion.strong_claims | theme | photocorrosion | Theme photocorrosion has 0 strong claim(s); project target is 1. | Re-read the supporting papers or add stronger primary evidence before using confident manuscript wording. |


## Configured Rules

- `zis.theme.photocorrosion.min_papers` (theme, theme_min_papers, enabled): Photocorrosion needs at least three supporting papers
- `zis.theme.photocorrosion.strong_claims` (theme, theme_min_strong_claims, enabled): Photocorrosion needs at least one strong claim
- `zis.claim.strong_claims_need_location` (claim, required_field, enabled): Strong claims need a section or page location
- `zis.manuscript.no_unknown_citations` (manuscript, manuscript_no_unknown_citations, enabled): Manuscripts should not contain unknown citation keys
