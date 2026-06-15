# Workflow Run: Release Candidate Check

This report was generated from a local declarative workflow recipe. It does not execute shell commands, run untrusted Python code, use cloud services, or fabricate evidence.

Recipe ID: `release_candidate_check`
Project: `zis_photocatalysis`
Root: `projects/zis_photocatalysis`
Dry run: `true`
Safety level: `read_only_or_cache`
Project note: Intentionally imperfect synthetic photocatalysis review profile for dogfooding evidence-gap, weak-claim, and citation-audit workflows.

## Step Results

| Step | Type | Status | Message | Outputs |
| --- | --- | --- | --- | --- |
| `validate_registry` | `validate_registry` | passed | Validated registry with 2 paper(s). Findings: 0. |  |
| `validate_bibtex` | `validate_bibtex` | passed | Validated 2 BibTeX entrie(s). Findings: 1. |  |
| `doctor` | `run_doctor` | planned | Would run workspace health with 5 finding(s). | `reports/workflow_release_candidate_workspace_health.md` |
| `integrity` | `run_integrity` | planned | Would run integrity check with 6 finding(s). | `reports/workflow_release_candidate_integrity.md` |
| `rules` | `run_rules` | planned_with_errors | Would run rules with 16 finding(s). | `reports/workflow_release_candidate_rules.md` |
| `dashboard` | `run_dashboard` | planned | Would generate dashboard report. | `reports/workflow_release_candidate_dashboard.md` |
| `index` | `search_index_rebuild` | failed | build_index_records() got an unexpected keyword argument 'root' |  |

## Findings

| Severity | Code | Step | Message | Suggested action |
| --- | --- | --- | --- | --- |
| warning | `suspiciously_incomplete` | `validate_bibtex` | zisStability2024: zisStability2024 looks sparse. | Review the entry for missing author, venue, DOI, or URL fields. |
| warning | `note_parse_warning` | `doctor` | zis_stability_2024: zis_stability_2024.md: Claim A is missing evidence location. | Review the note against the structured note format. |
| warning | `suspiciously_incomplete` | `doctor` | zisStability2024: zisStability2024 looks sparse. | Review the entry for missing author, venue, DOI, or URL fields. |
| warning | `theme_under_supported` | `doctor` | photocorrosion: photocorrosion has 1 supporting claim(s); target is 2. | Add more verified claims or adjust the theme threshold. |
| warning | `theme_too_few_papers` | `doctor` | photocorrosion: photocorrosion has evidence from 1 paper(s); target is 2. | Add evidence from more papers or adjust the theme threshold. |
| error | `claim_missing_evidence_location` | `doctor` | zis_stability_2024:c1: zis_stability_2024:c1 has no section/page evidence location. | Add a section, page, figure, table, or appendix location. |
| warning | `note_parse_warning` | `integrity` | zis_stability_2024: zis_stability_2024.md: Claim A is missing evidence location. | Review the note against the structured note format. |
| warning | `suspiciously_incomplete` | `integrity` | zisStability2024: zisStability2024 looks sparse. | Review the entry for missing author, venue, DOI, or URL fields. |
| warning | `theme_under_supported` | `integrity` | photocorrosion: photocorrosion has 1 supporting claim(s); target is 2. | Add more verified claims or adjust the theme threshold. |
| warning | `theme_too_few_papers` | `integrity` | photocorrosion: photocorrosion has evidence from 1 paper(s); target is 2. | Add evidence from more papers or adjust the theme threshold. |
| error | `claim_missing_evidence_location` | `integrity` | zis_stability_2024:c1: zis_stability_2024:c1 has no section/page evidence location. | Add a section, page, figure, table, or appendix location. |
| warning | `local_file_warning` | `integrity` | Scan folder missing: papers | Run `paperwb files audit` for details. |
| error | `builtin.citation_audit.claim_missing_evidence_location` | `rules` | zis_stability_2024:c1: zis_stability_2024:c1 has no section or page evidence location. | Add section, page, figure, table, or appendix location. |
| warning | `builtin.citation_audit.low_confidence_claim` | `rules` | zis_stability_2024:c1: zis_stability_2024:c1 is marked low confidence or weak. | Re-read the evidence before using this claim as core support. |
| warning | `builtin.citation_audit.theme_under_supported` | `rules` | photocorrosion: photocorrosion has 1 supporting claim(s); target is 2. | Add more verified claims or lower the theme's stated coverage expectations. |
| warning | `builtin.citation_audit.theme_too_few_papers` | `rules` | photocorrosion: photocorrosion has evidence from 1 paper(s); target is 2. | Add more papers with verified claims for this theme. |
| warning | `builtin.citation_audit.theme_only_review_statements` | `rules` | photocorrosion: photocorrosion is supported only by review statements. | Look for direct experimental, methodological, or theoretical evidence. |
| warning | `builtin.citation_audit.included_paper_with_weak_evidence` | `rules` | zis_stability_2024: zis_stability_2024 is included in the literature review but has weak/speculative evidence. | Re-read or add stronger evidence before relying on this paper. |
| warning | `builtin.citation_audit.paper_theme_without_claim` | `rules` | zis_charge_2025: zis_charge_2025 is tagged for theme photocorrosion but has no clear supporting claim. | Add a claim block or remove the theme tag if the paper is not evidence. |
| warning | `builtin.evidence_map.theme_min_claims` | `rules` | photocorrosion: photocorrosion has 1 claim(s); target is 2. | Add verified claim blocks or lower the theme threshold. |
| warning | `builtin.evidence_map.theme_min_papers` | `rules` | photocorrosion: photocorrosion has evidence from 1 paper(s); target is 2. | Add evidence from more papers or lower the theme threshold. |
| warning | `builtin.workspace_health.note_parse_warning` | `rules` | zis_stability_2024: zis_stability_2024.md: Claim A is missing evidence location. | Review the note against the structured note format. |
| warning | `builtin.workspace_health.suspiciously_incomplete` | `rules` | zisStability2024: zisStability2024 looks sparse. | Review the entry for missing author, venue, DOI, or URL fields. |
| warning | `builtin.workspace_health.theme_under_supported` | `rules` | photocorrosion: photocorrosion has 1 supporting claim(s); target is 2. | Add more verified claims or adjust the theme threshold. |
| warning | `builtin.workspace_health.theme_too_few_papers` | `rules` | photocorrosion: photocorrosion has evidence from 1 paper(s); target is 2. | Add evidence from more papers or adjust the theme threshold. |
| error | `builtin.workspace_health.claim_missing_evidence_location` | `rules` | zis_stability_2024:c1: zis_stability_2024:c1 has no section/page evidence location. | Add a section, page, figure, table, or appendix location. |
| warning | `zis.theme.photocorrosion.min_papers` | `rules` | photocorrosion: Theme photocorrosion has 1 supporting paper(s); project target is 3. | Add more user-verified notes and claims before treating this theme as review-ready. |
| warning | `zis.theme.photocorrosion.strong_claims` | `rules` | photocorrosion: Theme photocorrosion has 0 strong claim(s); project target is 1. | Re-read the supporting papers or add stronger primary evidence before using confident manuscript wording. |
| error | `step_failed` | `index` | build_index_records() got an unexpected keyword argument 'root' | Fix the step inputs or run this command directly for more detail. |

## Files Written

- `reports/workflow_release_candidate_workspace_health.md`
- `reports/workflow_release_candidate_integrity.md`
- `reports/workflow_release_candidate_rules.md`
- `reports/workflow_release_candidate_dashboard.md`
