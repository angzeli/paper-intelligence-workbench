# Support Bundles

`paperwb support bundle` creates a local diagnostic folder for debugging a
project without sharing private research content.

```bash
paperwb support bundle --project clean_demo --out scratch/clean_demo_support_bundle
```

The default mode is safe. It writes generated summaries and sanitized samples
only; it does not copy source notes, drafts, PDFs, cache databases, backups, or
audit logs.

## Bundle Files

- `manifest.json`
- `environment.md`
- `cli_inventory.md`
- `project_structure.md`
- `validation_summary.md`
- `report_inventory.md`
- `schema_summary.md`
- `data_safety_summary.md`
- `command_reproduction.md`
- `sanitized_registry_sample.csv`
- `sanitized_claims_sample.csv`
- `sanitized_findings.json`
- `README_SUPPORT_BUNDLE.md`

Use `--force` only when you intend to rewrite known bundle files in an existing
output directory.

## Local-only Verbose Mode

```bash
paperwb support bundle --project clean_demo --verbose-local-only --out scratch/local_bundle
```

Verbose mode is for private debugging on your own machine. Inspect the output
before sharing it because it can include paper titles, authors, DOI/URL values,
BibTeX keys, and claim text.
