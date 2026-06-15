# Workflow Run: Weekly Review

This report was generated from a local declarative workflow recipe. It does not execute shell commands, run untrusted Python code, use cloud services, or fabricate evidence.

Recipe ID: `weekly_review`
Project: `zis_photocatalysis`
Root: `projects/zis_photocatalysis`
Dry run: `true`
Safety level: `writes_reports`

## Step Results

| Step | Type | Status | Message | Outputs |
| --- | --- | --- | --- | --- |
| `validate_registry` | `validate_registry` | passed | Validated registry with 2 paper(s). Findings: 0. |  |
| `validate_bibtex` | `validate_bibtex` | passed | Validated 2 BibTeX entrie(s). Findings: 1. |  |
| `extract_claims` | `extract_claims` | planned | Would export 2 extracted claim(s). | `reports/workflow_weekly_review_claims.csv` |
| `evidence_map` | `generate_report` | planned | Would generate evidence-map report. | `reports/workflow_weekly_review_evidence_map.md` |
| `citation_audit` | `generate_report` | planned | Would generate citation-audit report. | `reports/workflow_weekly_review_citation_audit.md` |
| `weak_claims` | `generate_report` | planned | Would generate weak-claims report. | `reports/workflow_weekly_review_weak_claims.md` |
| `dashboard` | `run_dashboard` | planned | Would generate dashboard report. | `reports/workflow_weekly_review_dashboard.md` |

## Findings

| Severity | Code | Step | Message | Suggested action |
| --- | --- | --- | --- | --- |
| warning | `suspiciously_incomplete` | `validate_bibtex` | zisStability2024: zisStability2024 looks sparse. | Review the entry for missing author, venue, DOI, or URL fields. |

## Files Written

- `reports/workflow_weekly_review_claims.csv`
- `reports/workflow_weekly_review_evidence_map.md`
- `reports/workflow_weekly_review_citation_audit.md`
- `reports/workflow_weekly_review_weak_claims.md`
- `reports/workflow_weekly_review_dashboard.md`
