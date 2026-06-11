# Rule Report v1.5

This report combines built-in validation adapters with optional project-specific declarative rules.
It audits local metadata and evidence tracking only; it does not modify files or judge scientific truth.

Project: zis_photocatalysis
Rule file: `projects/zis_photocatalysis/rules.json`
Configured rules: 4
Built-in adapter findings: 0
Configured rule findings: 2
Total findings: 2

## Findings

| Severity | Rule ID | Target | Identifier | Message | Suggested action |
| --- | --- | --- | --- | --- | --- |
| warning | zis.theme.photocorrosion.min_papers | theme | photocorrosion | Theme photocorrosion has 1 supporting paper(s); project target is 3. | Add more user-verified notes and claims before treating this theme as review-ready. |
| warning | zis.theme.photocorrosion.strong_claims | theme | photocorrosion | Theme photocorrosion has 0 strong claim(s); project target is 1. | Re-read the supporting papers or add stronger primary evidence before using confident manuscript wording. |


## Configured Rules

- `zis.theme.photocorrosion.min_papers` (theme, theme_min_papers, enabled): Photocorrosion needs at least three supporting papers
- `zis.theme.photocorrosion.strong_claims` (theme, theme_min_strong_claims, enabled): Photocorrosion needs at least one strong claim
- `zis.claim.strong_claims_need_location` (claim, required_field, enabled): Strong claims need a section or page location
- `zis.manuscript.no_unknown_citations` (manuscript, manuscript_no_unknown_citations, enabled): Manuscripts should not contain unknown citation keys
