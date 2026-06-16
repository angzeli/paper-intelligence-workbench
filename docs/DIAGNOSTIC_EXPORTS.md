# Diagnostic Exports

Support diagnostics answer operational questions about a workbench project:

- installed package version
- available CLI command groups
- project folder shape
- registry and BibTeX validation status
- counts of papers, notes, claims, themes, and reports
- report inventory
- schema field names
- safe command reproduction steps

Commands:

```bash
paperwb support doctor --project clean_demo
paperwb support redact-preview --project clean_demo
paperwb support reproduce --project clean_demo
paperwb support bundle --project clean_demo --out scratch/clean_demo_support_bundle
```

These commands are diagnostic. They do not modify registry rows, BibTeX files,
notes, claims, drafts, cache indexes, backups, or audit logs. Only explicit
`--out` paths and support bundle folders are written.

Use `paperwb doctor`, `paperwb integrity check`, and `paperwb dashboard` for
normal local maintenance. Use `paperwb support ...` when you need a sanitized
debug artifact.
