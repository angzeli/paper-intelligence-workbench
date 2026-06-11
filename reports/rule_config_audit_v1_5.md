# Rule Configuration Audit v1.5

This report validates declarative local JSON rules. Rule files are data only; they do not execute Python code.

Rule file: `projects/zis_photocatalysis/rules.json`
Rule set: Synthetic ZIS photocatalysis project rules
Rules loaded: 4

## Findings

No findings.


## Rule IDs

- `zis.theme.photocorrosion.min_papers` (theme, theme_min_papers, enabled) - Photocorrosion needs at least three supporting papers
- `zis.theme.photocorrosion.strong_claims` (theme, theme_min_strong_claims, enabled) - Photocorrosion needs at least one strong claim
- `zis.claim.strong_claims_need_location` (claim, required_field, enabled) - Strong claims need a section or page location
- `zis.manuscript.no_unknown_citations` (manuscript, manuscript_no_unknown_citations, enabled) - Manuscripts should not contain unknown citation keys
