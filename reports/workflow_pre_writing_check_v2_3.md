# Workflow Run: Pre-writing Check

This report was generated from a local declarative workflow recipe. It does not execute shell commands, run untrusted Python code, use cloud services, or fabricate evidence.

Recipe ID: `pre_writing_check`
Project: `zis_photocatalysis`
Root: `projects/zis_photocatalysis`
Dry run: `true`
Safety level: `writes_reports`

## Step Results

| Step | Type | Status | Message | Outputs |
| --- | --- | --- | --- | --- |
| `validate_registry` | `validate_registry` | passed | Validated registry with 2 paper(s). Findings: 0. |  |
| `validate_bibtex` | `validate_bibtex` | passed | Validated 2 BibTeX entrie(s). Findings: 1. |  |
| `evidence_map` | `generate_report` | planned | Would generate evidence-map report. | `reports/workflow_pre_writing_evidence_map.md` |
| `citation_audit` | `generate_report` | planned | Would generate citation-audit report. | `reports/workflow_pre_writing_citation_audit.md` |
| `missing_evidence` | `generate_report` | planned | Would generate missing-evidence report. | `reports/workflow_pre_writing_missing_evidence.md` |
| `writing_packet` | `writing_packet` | planned | Would generate writing packet for photocorrosion. | `reports/workflow_pre-writing-check_writing-packet_photocorrosion_writing_packet.md` |

## Findings

| Severity | Code | Step | Message | Suggested action |
| --- | --- | --- | --- | --- |
| warning | `suspiciously_incomplete` | `validate_bibtex` | zisStability2024: zisStability2024 looks sparse. | Review the entry for missing author, venue, DOI, or URL fields. |

## Files Written

- `reports/workflow_pre_writing_evidence_map.md`
- `reports/workflow_pre_writing_citation_audit.md`
- `reports/workflow_pre_writing_missing_evidence.md`
- `reports/workflow_pre-writing-check_writing-packet_photocorrosion_writing_packet.md`
