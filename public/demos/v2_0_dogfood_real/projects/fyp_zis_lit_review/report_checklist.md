# Report Checklist: Photocatalysis

- `paperwb doctor --project PROJECT`
- `paperwb validate-bib projects/PROJECT/bibtex/library.bib --registry projects/PROJECT/registry.csv`
- `paperwb rules report --project PROJECT --out projects/PROJECT/reports/rule_report.md --force`
- `paperwb dashboard --project PROJECT --no-audit-log --out projects/PROJECT/reports/dashboard.md --force`
- `paperwb report evidence-map --project PROJECT --out projects/PROJECT/reports/evidence_map.md --force`
- `paperwb report citation-audit --project PROJECT --out projects/PROJECT/reports/citation_audit.md --force`
- `paperwb report weak-claims --project PROJECT --out projects/PROJECT/reports/weak_claims.md --force`
