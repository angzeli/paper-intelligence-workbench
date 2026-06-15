# Report Recipes

Report recipes are workflow steps that generate repeatable local reports.

Supported report-oriented step types include:

- `generate_report`
- `run_dashboard`
- `run_rules`
- `run_doctor`
- `run_integrity`
- `manuscript_qa`
- `writing_packet`
- `export_claims`

Example:

```json
{
  "step_id": "citation_audit",
  "name": "Generate citation audit",
  "step_type": "generate_report",
  "params": {
    "report_type": "citation-audit"
  },
  "output": "reports/workflow_citation_audit.md"
}
```

`generate_report` currently supports core local reports such as inventory,
reading status, BibTeX audit, evidence map, citation audit, missing notes, weak
claims, missing evidence, theme dashboard, and workspace health. Theme-specific
writing packets should use the `writing_packet` step.

Recipe outputs are planning and audit artifacts. They should be regenerated
from local registry, BibTeX, notes, claims, and theme files rather than edited
as source data.
